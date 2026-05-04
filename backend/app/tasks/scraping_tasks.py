import asyncio
import re
from typing import Any

from sqlalchemy import Boolean, Float, Integer
from sqlalchemy.inspection import inspect

from app.celery_app import celery_app
from app.database import AsyncSessionLocal, async_engine
from app.logging_config import get_logger
from app.models.cooling import CoolingSpec
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.psu import PSU
from app.models.ram import RAM
from app.models.storage import StorageSpec
from app.models.product import Product
from app.services.database_service import DatabaseService
from app.tasks.telemart_scraper import TelemartScraper


logger = get_logger(__name__)

SUPPORTED_TRIGGER_CATEGORIES = {
    "cpu": ["cpu"],
    "gpu": ["gpu"],
    "ram": ["ram"],
    "ssd": ["ssd"],
    "hdd": ["hdd"],
    "motherboard": ["motherboard"],
    "psu": ["psu"],
    "air_cooling": ["air_cooling"],
    "liquid_cooling": ["liquid_cooling"],
}

SPEC_MODELS = {
    "cpu": CPU,
    "gpu": GPU,
    "ram": RAM,
    "ssd": StorageSpec,
    "hdd": StorageSpec,
    "motherboard": Motherboard,
    "psu": PSU,
    "air_cooling": CoolingSpec,
    "liquid_cooling": CoolingSpec,
}


def _filter_columns(model_cls: type[Any], data: dict[str, Any], excluded: set[str] | None = None) -> dict[str, Any]:
    excluded = excluded or set()
    model_columns = {column.name for column in inspect(model_cls).columns}
    allowed_columns = model_columns - excluded
    return {k: v for k, v in data.items() if k in allowed_columns}


def _to_int(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+", value.replace(" ", ""))
        if match:
            return int(match.group(0))
    return value


def _to_float(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:[.,]\d+)?", value.replace(" ", ""))
        if match:
            return float(match.group(0).replace(",", "."))
    return value


def _to_bool(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "+"}:
            return True
        if normalized in {"false", "0", "no", "n", "-"}:
            return False
    return value


def _coerce_for_model(model_cls: type[Any], data: dict[str, Any]) -> dict[str, Any]:
    columns = {column.name: column for column in inspect(model_cls).columns}
    coerced: dict[str, Any] = {}

    for key, value in data.items():
        column = columns.get(key)
        if column is None:
            coerced[key] = value
            continue

        column_type = column.type
        if isinstance(column_type, Integer):
            coerced[key] = _to_int(value)
        elif isinstance(column_type, Float):
            coerced[key] = _to_float(value)
        elif isinstance(column_type, Boolean):
            coerced[key] = _to_bool(value)
        else:
            coerced[key] = value

    return coerced


async def _scrape_and_persist(product_type: str) -> int:
    scraper = TelemartScraper(product_type=product_type)
    items = await scraper.fetch_all()
    spec_model = SPEC_MODELS[product_type]

    async with AsyncSessionLocal() as db:
        service = DatabaseService(db)

        for item in items:
            raw_product = item.get("product", {})
            raw_specs = item.get("specs", {})

            external_id = raw_product.get("product_id")
            if not external_id:
                continue

            product_data = {
                "name": raw_product.get("name"),
                "price": raw_product.get("price"),
                "image_small": raw_product.get("image_small") if raw_product.get("image_small") else None,
                "image": raw_product.get("image") if raw_product.get("image") else None,
                "url": raw_product.get("url"),
                "category": raw_product.get("category"),
                "subcategory": raw_product.get("subcategory"),
                "brand": raw_product.get("brand"),
                "other_features": raw_product.get("other_features"),
            }

            filtered_product_data = _filter_columns(Product, product_data, excluded={"id", "external_id"})
            filtered_spec_data = _filter_columns(spec_model, raw_specs, excluded={"id", "product_id"})
            filtered_product_data = _coerce_for_model(Product, filtered_product_data)
            filtered_spec_data = _coerce_for_model(spec_model, filtered_spec_data)

            await service.upsert_product_with_spec(
                external_id=int(external_id),
                product_data=filtered_product_data,
                spec_model=spec_model,
                spec_data=filtered_spec_data,
            )

        await service.commit()

    return len(items)


async def _scrape_category(product_types: list[str]) -> dict[str, Any]:
    scraped_counts: dict[str, int] = {}
    total_items = 0

    try:
        for product_type in product_types:
            count = await _scrape_and_persist(product_type)
            scraped_counts[product_type] = count
            total_items += count
            logger.info("scraping_category_completed", product_type=product_type, count=count)

        return {
            "total_items": total_items,
            "details": scraped_counts,
        }
    finally:
        await async_engine.dispose()


@celery_app.task(name="app.tasks.scraping_tasks.scrape_category_task")
def scrape_category_task(category: str) -> dict[str, Any]:
    normalized = category.strip().lower()
    if normalized not in SUPPORTED_TRIGGER_CATEGORIES:
        raise ValueError(f"Unsupported category: {category}")

    result = asyncio.run(_scrape_category(SUPPORTED_TRIGGER_CATEGORIES[normalized]))
    result["category"] = normalized
    return result
