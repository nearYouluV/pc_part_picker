from pyexpat import features

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from app.logging_config import configure_logging, get_logger
import orjson
import math
from app.utils.feature_extractor import extract_features, split_features
from app.utils.mapper import map_product
from app.utils.mappings import BASE_MAPPINGS, CATEGORY_MAPPINGS, STORAGE_MAPPINGS, COOLING_MAPPINGS
import re
from app.models.base import CategoryEnum

configure_logging()

CATEGORY_NORMALIZATION = {
    "ssd": (CategoryEnum.STORAGE, "ssd"),
    "hdd": (CategoryEnum.STORAGE, "hdd"),
    "cpu": (CategoryEnum.CPU, None),
    "gpu": (CategoryEnum.GPU, None),
    "ram": (CategoryEnum.RAM, None),
    "motherboard": (CategoryEnum.MOTHERBOARD, None),
    "psu": (CategoryEnum.PSU, None),
    "air_cooling": (CategoryEnum.COOLER, "air_cooling"),
    "liquid_cooling": (CategoryEnum.COOLER, "liquid_cooling"),
}

def parse_cpu_socket_compatibility(value: str) -> list[str]:
    if not value:
        return []

    clean = re.sub(r"<.*?>", "\n", value)

    match = re.search(r"Compatible:(.*?)(Not compatible:|$)", clean, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    compatible_block = match.group(1)

    sockets = re.findall(r"(LGA\d+|AM\d+|TRX?\d+|FM\d+)", compatible_block)

    return list(set(sockets))

class TelemartScraper:
    def __init__(self,  product_type):
        self.category_id = CATEGORY_MAPPINGS.get(product_type)
        self.product_type = product_type
        self.base_url = 'https://telemart.ua/ua/assembly/filter-products/'
        self.request_timeout = 20
        self.logger = get_logger("telemart_scraper")
        self.min_price = None
        self.max_price = None

    def _get_mapping(self):
        if self.product_type in STORAGE_MAPPINGS:
            return STORAGE_MAPPINGS[self.product_type]
        elif self.product_type in COOLING_MAPPINGS:
            return COOLING_MAPPINGS[self.product_type]
        return BASE_MAPPINGS.get(self.product_type, {})

    async def safe_request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        json_data: Dict = None,
        retries: int = 5,
    ) -> Dict[str, Any]:

        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        retryable_status_codes = {502, 503, 504, 429}
        if not json_data:
            json_data = {
                'id_category': self.category_id,
                'filters': [
                    'available',
                    'recommend',
                    'stock',
                ],
                'search': '',
                'sort': 'popular',
                'page': 0,
            }
        if self.min_price is not None:
            json_data['price_min_uah'] = self.min_price
        if self.max_price is not None:
            json_data['price_max_uah'] = self.max_price
        for attempt in range(retries):
            try:
                async with session.request(
                    method,
                    url,
                    json=json_data,
                    timeout=timeout,
                ) as resp:
                    try:
                        content = await resp.json(loads=orjson.loads)
                    except aiohttp.ContentTypeError:
                        content = await resp.text()
                        return {"error": f"Invalid JSON response: {content}"}

                    if resp.status != 200:
                        if resp.status in retryable_status_codes and attempt < retries - 1:
                            wait_time = (2 ** attempt) + (attempt * 1)  # exponential backoff with jitter
                            self.logger.warning(
                                "Request failed, retrying...",
                                extra={
                                    "method": method,
                                    "status": resp.status,
                                    "attempt": attempt + 1,
                                    "retries": retries,
                                    "wait_seconds": wait_time
                                }
                            )

                            await asyncio.sleep(wait_time)
                            continue

                        try:
                            error_details = orjson.loads(content).get("error", {})
                            error_msg = error_details.get("reason", f"HTTP {resp.status}")
                            self.logger.error(
                                "Request failed",
                                extra={
                                    "method": method,
                                    "status": resp.status,
                                    "reason": error_msg
                                }
                            )
                        except BaseException:
                            self.logger.error(
                                "Request failed",
                                extra={
                                    "method": method,
                                    "status": resp.status,
                                    "reason": "unparsed_error_response"
                                }
                            )

                        return {"error": f"HTTP {resp.status}"}
                    return content

            except aiohttp.ClientConnectorError as e:
                if attempt == retries - 1:
                    self.logger.error(
                        "request_failed",
                        method=method,
                        error_type="client_connector_error",
                        error=str(e),
                    )
                    return {"error": str(e), "error_type": "client_connector_error"}
                wait_time = (2 ** attempt) + 1

                self.logger.warning(
                    "request_retry",
                    method=method,
                    attempt=attempt + 1,
                    retries=retries,
                    wait_seconds=wait_time,
                    error_type="client_connector_error",
                )
                await asyncio.sleep(wait_time)

            except aiohttp.ServerDisconnectedError as e:
                if attempt == retries - 1:
                    self.logger.error(
                        "request_failed",
                        method=method,
                        error_type="server_disconnected_error",
                        error=str(e),
                    )
                    return {"error": str(e), "error_type": "server_disconnected_error"}

                wait_time = (2 ** attempt) + 1

                self.logger.warning(
                    "request_retry",
                    method=method,
                    attempt=attempt + 1,
                    retries=retries,
                    wait_seconds=wait_time,
                    error_type="server_disconnected_error",
                )
                await asyncio.sleep(wait_time)

            except asyncio.TimeoutError as e:
                if attempt == retries - 1:
                    self.logger.error(
                        "request_failed",
                        method=method,
                        error_type="timeout_error",
                        error=str(e),
                    )
                    return {"error": str(e), "error_type": "timeout_error"}

                wait_time = (2 ** attempt) + 1
                await asyncio.sleep(wait_time)

            except Exception as e:
                if attempt == retries - 1:
                    self.logger.error(
                        "request_failed",
                        method=method,
                        error_type="request_error",
                        error=str(e),
                    )
                    return {"error": str(e), "error_type": "request_error"}

                await asyncio.sleep(1)

    async def fetch_all(self):
        async with aiohttp.ClientSession() as session:

            base_payload = {
                "id_category": self.category_id,
                "filters": ["available", "recommend", "stock"],
                "sort": "popular",
                "search": "",
                "page": 0,
            }

            first = await self.safe_request(session, "POST", self.base_url, json_data=base_payload)
            total = first["data"]["pagination"]["totalCount"]
            per_page = first["data"]["pagination"]["perPage"]
            pages = math.ceil(total / per_page)

            self.logger.info(f"Total pages: {pages}")

            # ---------------------------
            # ASYNC PAGE FETCHING
            # ---------------------------

            async def fetch_page(page: int):
                payload = dict(base_payload)
                payload["page"] = page

                data = await self.safe_request(session, "POST", self.base_url, json_data=payload)

                items = data.get("data", {}).get("products", [])

                page_results = []

                for item in items:
                    features = extract_features(item)

                    product_map = self._get_mapping()
                    mapped_features, other_features = split_features(features, product_map)
                    normalized = map_product(mapped_features, product_map)
                    category, subcategory = CATEGORY_NORMALIZATION[self.product_type]
                    page_results.append({
                        "product": {
                            "name": item["name"],
                            "price": item["price"],
                            "image_small": item["image_small"],
                            "image": item["image"],
                            "product_id": item["product_id"],
                            "category": category,
                            "subcategory": subcategory,
                            "other_features": other_features
                        },
                        "specs": normalized
                    })

                    if item.get("manufactor"):
                        page_results[-1]['product']['brand'] = item.get("manufactor")
                        if self.product_type == "cpu":
                            page_results[-1]['specs']['manufacturer'] = item.get("manufactor")
                    elif features.get("brand"):
                        page_results[-1]['product']['brand'] = features.get("brand")
                    if "cooling" in self.product_type:
                        intel_raw = features.get("Compatibility with Intel")
                        amd_raw = features.get("Compatibility with AMD")
                        intel_sockets = parse_cpu_socket_compatibility(intel_raw)
                        amd_sockets = parse_cpu_socket_compatibility(amd_raw)

                        all_sockets = list(set(intel_sockets + amd_sockets))
                        page_results[-1]['specs']['socket_support'] = all_sockets

                        if self.product_type == "air_cooling":
                            page_results[-1]['specs']['cooling_type'] = "AIR"
                        elif self.product_type == "liquid_cooling":
                            page_results[-1]['specs']['cooling_type'] = "LIQUID"

                return page_results

            tasks = [fetch_page(page) for page in range(pages)]

            pages_data = await asyncio.gather(*tasks)

            results = [item for page in pages_data for item in page]
            print(results[0])
            return results

async def main():
    scraper = TelemartScraper(product_type="liquid_cooling")
    await scraper.fetch_all()

if __name__ == "__main__":
    asyncio.run(main())