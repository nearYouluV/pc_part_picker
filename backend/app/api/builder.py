from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.builder_schemas import (
    AddComponentRequest,
    BuildCreateRequest,
    BuildDetailResponse,
    BuildReviewRequest,
    BuildReviewView,
    BuildSuggestionRequest,
    BuildSuggestionView,
    BuildUpdateRequest,
    ProductRecommendationResponse,
)
from app.database import get_async_db
from app.models.base import CategoryEnum
from app.models.build import BuildReview, BuildSuggestion
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.psu import PSU
from app.models.ram import RAM
from app.models.storage import StorageSpec
from app.models.cooling import CoolingSpec
from app.models.user import User
from app.models.product import Product
from app.services.auth_service import get_current_active_user
from app.services.builder_service import BuilderService, build_warnings
from app.utils.scoring_engine import build_context_from_build, rank_category_products


router = APIRouter(prefix="/builder", tags=["builder"])


def _apply_numeric_bounds(stmt, column, min_value: int | float | None = None, max_value: int | float | None = None):
    if min_value is not None:
        stmt = stmt.where(column >= min_value)
    if max_value is not None:
        stmt = stmt.where(column <= max_value)
    return stmt


def _apply_text_match(stmt, column, value: str | None):
    if value and value.strip():
        stmt = stmt.where(column.ilike(f"%{value.strip()}%"))
    return stmt


def _apply_category_filters(stmt, category: str, **filters):
    if category == "cpu":
        stmt = stmt.join(Product.cpu_spec)
        stmt = _apply_numeric_bounds(stmt, CPU.cores, filters.get("cores_min"), filters.get("cores_max"))
        # Frequencies from UI are provided in MHz — stored values are in MHz. Accept as-is.
        base_clock_min = filters.get("base_clock_min")
        base_clock_max = filters.get("base_clock_max")
        boost_clock_min = filters.get("boost_clock_min")
        boost_clock_max = filters.get("boost_clock_max")
        if base_clock_min is not None:
            base_clock_min = float(base_clock_min)
        if base_clock_max is not None:
            base_clock_max = float(base_clock_max)
        if boost_clock_min is not None:
            boost_clock_min = float(boost_clock_min)
        if boost_clock_max is not None:
            boost_clock_max = float(boost_clock_max)
        stmt = _apply_numeric_bounds(stmt, CPU.base_clock, base_clock_min, base_clock_max)
        stmt = _apply_numeric_bounds(stmt, CPU.boost_clock, boost_clock_min, boost_clock_max)
        stmt = _apply_numeric_bounds(stmt, CPU.tdp, filters.get("tdp_min"), filters.get("tdp_max"))
        stmt = _apply_numeric_bounds(stmt, CPU.l3_cache, filters.get("l3_cache_min"), filters.get("l3_cache_max"))
        l3_band = filters.get("l3_cache_band")
        if l3_band == "gt65":
            stmt = stmt.where(CPU.l3_cache > 65)
        elif l3_band == "41_64":
            stmt = stmt.where(CPU.l3_cache.between(41, 64))
        elif l3_band == "25_40":
            stmt = stmt.where(CPU.l3_cache.between(25, 40))
        elif l3_band == "10_24":
            stmt = stmt.where(CPU.l3_cache.between(10, 24))
        elif l3_band == "lt10":
            stmt = stmt.where(CPU.l3_cache < 10)
        stmt = _apply_text_match(stmt, CPU.socket, filters.get("socket"))
        stmt = _apply_text_match(stmt, CPU.manufacturer, filters.get("manufacturer"))

    elif category == "gpu":
        stmt = stmt.join(Product.gpu_spec)
        # UI sends VRAM in GB, while GPU.vram is stored in MB.
        vram_min = filters.get("vram_min")
        vram_max = filters.get("vram_max")
        if vram_min is not None:
            vram_min = int(vram_min) * 1024
        if vram_max is not None:
            vram_max = int(vram_max) * 1024
        stmt = _apply_numeric_bounds(stmt, GPU.vram, vram_min, vram_max)
        # GPU frequency: UI provides MHz — accept as-is.
        frequency_min = filters.get("frequency_min")
        frequency_max = filters.get("frequency_max")
        if frequency_min is not None:
            frequency_min = float(frequency_min)
        if frequency_max is not None:
            frequency_max = float(frequency_max)
        stmt = _apply_numeric_bounds(stmt, GPU.frequency, frequency_min, frequency_max)
        stmt = _apply_numeric_bounds(stmt, GPU.performance, filters.get("performance_min"), filters.get("performance_max"))
        stmt = _apply_numeric_bounds(stmt, GPU.recommended_power_supply, filters.get("recommended_power_supply_min"), filters.get("recommended_power_supply_max"))
        stmt = _apply_text_match(stmt, GPU.memory_type, filters.get("memory_type"))
        stmt = _apply_text_match(stmt, Product.brand, filters.get("brand"))

    elif category == "motherboard":
        stmt = stmt.join(Product.motherboard_spec)
        stmt = _apply_text_match(stmt, Motherboard.socket, filters.get("socket"))
        stmt = _apply_text_match(stmt, Motherboard.chipset, filters.get("chipset"))
        stmt = _apply_text_match(stmt, Motherboard.ram_type, filters.get("ram_type"))
        stmt = _apply_numeric_bounds(stmt, Motherboard.max_ram, filters.get("max_ram_min"), filters.get("max_ram_max"))
        stmt = _apply_numeric_bounds(stmt, Motherboard.memory_slots, filters.get("memory_slots_min"), filters.get("memory_slots_max"))
        stmt = _apply_numeric_bounds(stmt, Motherboard.m2_slots, filters.get("m2_slots_min"), filters.get("m2_slots_max"))
        stmt = _apply_numeric_bounds(stmt, Motherboard.sata_ports, filters.get("sata_ports_min"), filters.get("sata_ports_max"))
        # Memory frequency filters: UI provides MHz — accept as-is.
        min_mem_freq_min = filters.get("min_memory_frequency_min")
        min_mem_freq_max = filters.get("min_memory_frequency_max")
        max_mem_freq_min = filters.get("max_memory_frequency_min")
        max_mem_freq_max = filters.get("max_memory_frequency_max")
        if min_mem_freq_min is not None:
            min_mem_freq_min = float(min_mem_freq_min)
        if min_mem_freq_max is not None:
            min_mem_freq_max = float(min_mem_freq_max)
        if max_mem_freq_min is not None:
            max_mem_freq_min = float(max_mem_freq_min)
        if max_mem_freq_max is not None:
            max_mem_freq_max = float(max_mem_freq_max)
        stmt = _apply_numeric_bounds(stmt, Motherboard.min_memory_frequency, min_mem_freq_min, min_mem_freq_max)
        stmt = _apply_numeric_bounds(stmt, Motherboard.max_memory_frequency, max_mem_freq_min, max_mem_freq_max)

    elif category == "ram":
        stmt = stmt.join(Product.ram_spec)
        stmt = _apply_numeric_bounds(stmt, RAM.capacity, filters.get("capacity_min"), filters.get("capacity_max"))
        # RAM frequency: UI provides MHz — accept as-is.
        ram_freq_min = filters.get("frequency_min")
        ram_freq_max = filters.get("frequency_max")
        if ram_freq_min is not None:
            ram_freq_min = float(ram_freq_min)
        if ram_freq_max is not None:
            ram_freq_max = float(ram_freq_max)
        stmt = _apply_numeric_bounds(stmt, RAM.frequency, ram_freq_min, ram_freq_max)
        stmt = _apply_numeric_bounds(stmt, RAM.cas_latency, filters.get("cas_latency_min"), filters.get("cas_latency_max"))
        stmt = _apply_numeric_bounds(stmt, RAM.modules_count, filters.get("modules_count_min"), filters.get("modules_count_max"))
        stmt = _apply_text_match(stmt, RAM.ram_type, filters.get("ram_type"))

    elif category == "psu":
        stmt = stmt.join(Product.psu_spec)
        stmt = _apply_numeric_bounds(stmt, PSU.power, filters.get("power_min"), filters.get("power_max"))
        stmt = _apply_text_match(stmt, PSU.certification, filters.get("certification"))
        modularity = filters.get("modularity")
        if modularity is True:
            stmt = stmt.where(PSU.modularity.is_(True))
        elif modularity is False:
            stmt = stmt.where(PSU.modularity.is_(False))

    elif category == "storage":
        stmt = stmt.join(Product.storage_spec)
        stmt = _apply_numeric_bounds(stmt, StorageSpec.capacity, filters.get("capacity_min"), filters.get("capacity_max"))
        stmt = _apply_numeric_bounds(stmt, StorageSpec.read_speed, filters.get("read_speed_min"), filters.get("read_speed_max"))
        stmt = _apply_numeric_bounds(stmt, StorageSpec.write_speed, filters.get("write_speed_min"), filters.get("write_speed_max"))
        stmt = _apply_numeric_bounds(stmt, StorageSpec.rpm, filters.get("rpm_min"), filters.get("rpm_max"))
        stmt = _apply_text_match(stmt, StorageSpec.interface, filters.get("interface"))
        stmt = _apply_text_match(stmt, StorageSpec.form_factor, filters.get("form_factor"))

    elif category == "cooler":
        stmt = stmt.join(Product.cooler_spec)
        stmt = _apply_numeric_bounds(stmt, CoolingSpec.tdp_support, filters.get("tdp_support_min"), filters.get("tdp_support_max"))
        stmt = _apply_numeric_bounds(stmt, CoolingSpec.noise_level, filters.get("noise_level_min"), filters.get("noise_level_max"))
        stmt = _apply_numeric_bounds(stmt, CoolingSpec.fan_count, filters.get("fan_count_min"), filters.get("fan_count_max"))
        stmt = _apply_numeric_bounds(stmt, CoolingSpec.height, filters.get("height_min"), filters.get("height_max"))
        cooling_type_filter = filters.get("cooling_type")
        if cooling_type_filter and str(cooling_type_filter).strip():
            cooling_type_text = str(cooling_type_filter).strip().lower()
            if cooling_type_text in {"water", "liquid", "aio"}:
                stmt = stmt.where(CoolingSpec.cooling_type.ilike("%liquid%"))
            elif cooling_type_text in {"air"}:
                stmt = stmt.where(CoolingSpec.cooling_type.ilike("%air%"))
            else:
                stmt = _apply_text_match(stmt, CoolingSpec.cooling_type, str(cooling_type_filter))
        socket_support = filters.get("socket_support")
        if socket_support and socket_support.strip():
            stmt = stmt.where(CoolingSpec.socket_support.contains([socket_support.strip()]))

    return stmt


def serialize_review(review: BuildReview) -> BuildReviewView:
    username = review.user.username if review.user else "Unknown"
    return BuildReviewView(
        id=review.id,
        build_id=review.build_id,
        user_id=review.user_id,
        username=username,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


def serialize_suggestion(suggestion: BuildSuggestion) -> BuildSuggestionView:
    suggested_product = suggestion.suggested_product
    return BuildSuggestionView(
        id=suggestion.id,
        build_id=suggestion.build_id,
        user_id=suggestion.user_id,
        username=suggestion.user.username if suggestion.user else "Unknown",
        category=suggestion.category.value,
        suggested_product_id=suggestion.suggested_product_id,
        suggested_product_name=suggested_product.name if suggested_product else "Unknown",
        suggested_product_price=suggested_product.price if suggested_product else 0,
        quantity=suggestion.quantity,
        comment=suggestion.comment,
        status=suggestion.status,
        applied_by_user_id=suggestion.applied_by_user_id,
        applied_by_username=suggestion.applied_by_user.username if suggestion.applied_by_user else None,
        applied_at=suggestion.applied_at,
        created_at=suggestion.created_at,
        updated_at=suggestion.updated_at,
    )


def serialize_build(
    build,
    *,
    average_rating: float | None = None,
    review_count: int | None = None,
    reviews: list[BuildReview] | None = None,
    suggestions: list[BuildSuggestion] | None = None,
    owner_username: str | None = None,
) -> BuildDetailResponse:
    selected_components = {}
    storage_components = []
    total_price = 0

    for component in build.components:
        if not component.product:
            continue

        quantity = getattr(component, "quantity", 1) or 1
        component_payload = {
            "product_id": component.product.id,
            "external_id": component.product.external_id,
            "name": component.product.name,
            "price": component.product.price,
            "category": component.product.category.value,
            "quantity": quantity,
            "source": getattr(component, "source", "user"),
        }

        if component.category.value == "storage":
            storage_components.append(component_payload)
            if "storage" not in selected_components:
                selected_components["storage"] = component_payload
        else:
            selected_components[component.category.value] = component_payload

        total_price += (component.product.price or 0) * quantity

    return BuildDetailResponse(
        id=build.id,
        user_id=build.user_id,
        name=build.name,
        budget=build.budget,
        goal=build.goal.value,
        is_public=bool(getattr(build, "is_public", False)),
        owner_username=owner_username or (build.user.username if getattr(build, "user", None) else None),
        average_rating=average_rating,
        review_count=review_count if review_count is not None else len(reviews or []),
        selected_components=selected_components,
        storage_components=storage_components,
        total_price=total_price,
        compatibility_warnings=build_warnings(build),
        reviews=[serialize_review(review) for review in (reviews or [])],
        suggestions=[serialize_suggestion(suggestion) for suggestion in (suggestions or [])],
        created_at=build.created_at,
        updated_at=build.updated_at,
    )


@router.post("/create", response_model=BuildDetailResponse)
async def create_build(
    payload: BuildCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.create_build(
            user_id=current_user.id,
            name=payload.name,
            budget=payload.budget,
            goal=payload.goal,
        )
        build = await service.get_build(build.id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_build(build)


@router.get("/builds", response_model=list[BuildDetailResponse])
async def list_builds(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    builds = await service.list_builds(current_user.id)
    return [serialize_build(build) for build in builds]


@router.get("/public-builds", response_model=list[BuildDetailResponse])
async def list_public_builds(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    builds = await service.list_public_builds()
    serialized_builds = []
    for build in builds:
        reviews = list(getattr(build, "reviews", []) or [])
        average_rating = round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else None
        serialized_builds.append(
            serialize_build(
                build,
                average_rating=average_rating,
                review_count=len(reviews),
                reviews=reviews,
                owner_username=build.user.username if getattr(build, "user", None) else None,
            )
        )

    return serialized_builds


@router.get("/public-builds/{build_id}", response_model=BuildDetailResponse)
async def get_public_build(
    build_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    build = await service.get_public_build(build_id)
    if not build:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Build not found")

    reviews = getattr(build, "reviews", []) or []
    suggestions = []
    if current_user.id == build.user_id:
        suggestions = await service.list_build_suggestions(build_id)
    average_rating = round(sum(review.rating for review in reviews) / len(reviews), 2) if reviews else None

    return serialize_build(
        build,
        average_rating=average_rating,
        review_count=len(reviews),
        reviews=reviews,
        suggestions=suggestions,
        owner_username=build.user.username if getattr(build, "user", None) else None,
    )


@router.get("/public-builds/{build_id}/reviews", response_model=list[BuildReviewView])
async def list_public_build_reviews(
    build_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    build = await service.get_public_build(build_id)
    if not build:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Build not found")

    reviews = await service.list_build_reviews(build_id)
    return [serialize_review(review) for review in reviews]


@router.post("/public-builds/{build_id}/reviews", response_model=BuildReviewView)
async def create_public_build_review(
    build_id: int,
    payload: BuildReviewRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        review = await service.upsert_build_review(
            build_id=build_id,
            user_id=current_user.id,
            rating=payload.rating,
            comment=payload.comment,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return serialize_review(review)


@router.get("/public-builds/{build_id}/suggestions", response_model=list[BuildSuggestionView])
async def list_public_build_suggestions(
    build_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    build = await service.get_public_build(build_id)
    if not build:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Build not found")
    if build.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the build owner can view suggestions")

    suggestions = await service.list_build_suggestions(build_id)
    return [serialize_suggestion(suggestion) for suggestion in suggestions]


@router.post("/public-builds/{build_id}/suggestions", response_model=BuildSuggestionView)
async def create_public_build_suggestion(
    build_id: int,
    payload: BuildSuggestionRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        suggestion = await service.create_build_suggestion(
            build_id=build_id,
            user_id=current_user.id,
            category=payload.category,
            suggested_product_id=payload.suggested_product_id,
            quantity=payload.quantity,
            comment=payload.comment,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_suggestion(suggestion)


@router.post("/public-builds/{build_id}/suggestions/{suggestion_id}/apply", response_model=BuildSuggestionView)
async def apply_public_build_suggestion(
    build_id: int,
    suggestion_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        suggestion = await service.apply_build_suggestion(build_id, current_user.id, suggestion_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_suggestion(suggestion)


@router.post("/public-builds/{build_id}/suggestions/{suggestion_id}/reject", response_model=BuildSuggestionView)
async def reject_public_build_suggestion(
    build_id: int,
    suggestion_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        suggestion = await service.reject_build_suggestion(build_id, current_user.id, suggestion_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_suggestion(suggestion)


@router.get("/category/{category}", response_model=list[ProductRecommendationResponse])
async def list_category_products(
    category: str,
    build_id: int = Query(..., ge=1),
    compatible_only: bool = Query(True),
    search: str | None = Query(default=None, max_length=120),
    condition: str | None = Query(default=None, max_length=60),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    cores_min: int | None = Query(default=None, ge=0),
    cores_max: int | None = Query(default=None, ge=0),
    base_clock_min: float | None = Query(default=None, ge=0),
    base_clock_max: float | None = Query(default=None, ge=0),
    boost_clock_min: float | None = Query(default=None, ge=0),
    boost_clock_max: float | None = Query(default=None, ge=0),
    tdp_min: int | None = Query(default=None, ge=0),
    tdp_max: int | None = Query(default=None, ge=0),
    l3_cache_min: int | None = Query(default=None, ge=0),
    l3_cache_max: int | None = Query(default=None, ge=0),
    l3_cache_band: str | None = Query(default=None, max_length=20),
    socket: str | None = Query(default=None, max_length=50),
    manufacturer: str | None = Query(default=None, max_length=80),
    vram_min: int | None = Query(default=None, ge=0),
    vram_max: int | None = Query(default=None, ge=0),
    frequency_min: int | None = Query(default=None, ge=0),
    frequency_max: int | None = Query(default=None, ge=0),
    performance_min: int | None = Query(default=None, ge=0),
    performance_max: int | None = Query(default=None, ge=0),
    recommended_power_supply_min: int | None = Query(default=None, ge=0),
    recommended_power_supply_max: int | None = Query(default=None, ge=0),
    chipset: str | None = Query(default=None, max_length=80),
    ram_type: str | None = Query(default=None, max_length=30),
    max_ram_min: int | None = Query(default=None, ge=0),
    max_ram_max: int | None = Query(default=None, ge=0),
    memory_slots_min: int | None = Query(default=None, ge=0),
    memory_slots_max: int | None = Query(default=None, ge=0),
    m2_slots_min: int | None = Query(default=None, ge=0),
    m2_slots_max: int | None = Query(default=None, ge=0),
    sata_ports_min: int | None = Query(default=None, ge=0),
    sata_ports_max: int | None = Query(default=None, ge=0),
    min_memory_frequency_min: int | None = Query(default=None, ge=0),
    min_memory_frequency_max: int | None = Query(default=None, ge=0),
    max_memory_frequency_min: int | None = Query(default=None, ge=0),
    max_memory_frequency_max: int | None = Query(default=None, ge=0),
    capacity_min: int | None = Query(default=None, ge=0),
    capacity_max: int | None = Query(default=None, ge=0),
    cas_latency_min: int | None = Query(default=None, ge=0),
    cas_latency_max: int | None = Query(default=None, ge=0),
    modules_count_min: int | None = Query(default=None, ge=0),
    modules_count_max: int | None = Query(default=None, ge=0),
    certification: str | None = Query(default=None, max_length=80),
    modularity: bool | None = Query(default=None),
    power_min: int | None = Query(default=None, ge=0),
    power_max: int | None = Query(default=None, ge=0),
    interface: str | None = Query(default=None, max_length=50),
    form_factor: str | None = Query(default=None, max_length=40),
    read_speed_min: int | None = Query(default=None, ge=0),
    read_speed_max: int | None = Query(default=None, ge=0),
    write_speed_min: int | None = Query(default=None, ge=0),
    write_speed_max: int | None = Query(default=None, ge=0),
    rpm_min: int | None = Query(default=None, ge=0),
    rpm_max: int | None = Query(default=None, ge=0),
    tdp_support_min: int | None = Query(default=None, ge=0),
    tdp_support_max: int | None = Query(default=None, ge=0),
    noise_level_min: int | None = Query(default=None, ge=0),
    noise_level_max: int | None = Query(default=None, ge=0),
    fan_count_min: int | None = Query(default=None, ge=0),
    fan_count_max: int | None = Query(default=None, ge=0),
    height_min: int | None = Query(default=None, ge=0),
    height_max: int | None = Query(default=None, ge=0),
    cooling_type: str | None = Query(default=None, max_length=40),
    socket_support: str | None = Query(default=None, max_length=50),
    sort_by: str = Query(default="recommended"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    normalized_category = category.strip().lower()
    try:
        category_enum = CategoryEnum(normalized_category)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported category: {category}") from exc

    service = BuilderService(db)
    try:
        build = await service.get_build(build_id=build_id, user_id=current_user.id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    stmt = (
        select(Product)
        .where(Product.category == category_enum)
        .options(
            joinedload(Product.cpu_spec),
            joinedload(Product.gpu_spec),
            joinedload(Product.motherboard_spec),
            joinedload(Product.ram_spec),
            joinedload(Product.psu_spec),
            joinedload(Product.storage_spec),
            joinedload(Product.cooler_spec),
        )
        .order_by(Product.price.asc())
    )

    stmt = _apply_category_filters(
        stmt,
        normalized_category,
        cores_min=cores_min,
        cores_max=cores_max,
        base_clock_min=base_clock_min,
        base_clock_max=base_clock_max,
        boost_clock_min=boost_clock_min,
        boost_clock_max=boost_clock_max,
        tdp_min=tdp_min,
        tdp_max=tdp_max,
        l3_cache_min=l3_cache_min,
        l3_cache_max=l3_cache_max,
        l3_cache_band=l3_cache_band,
        socket=socket,
        manufacturer=manufacturer,
        vram_min=vram_min,
        vram_max=vram_max,
        frequency_min=frequency_min,
        frequency_max=frequency_max,
        performance_min=performance_min,
        performance_max=performance_max,
        recommended_power_supply_min=recommended_power_supply_min,
        recommended_power_supply_max=recommended_power_supply_max,
        chipset=chipset,
        ram_type=ram_type,
        max_ram_min=max_ram_min,
        max_ram_max=max_ram_max,
        memory_slots_min=memory_slots_min,
        memory_slots_max=memory_slots_max,
        m2_slots_min=m2_slots_min,
        m2_slots_max=m2_slots_max,
        sata_ports_min=sata_ports_min,
        sata_ports_max=sata_ports_max,
        min_memory_frequency_min=min_memory_frequency_min,
        min_memory_frequency_max=min_memory_frequency_max,
        max_memory_frequency_min=max_memory_frequency_min,
        max_memory_frequency_max=max_memory_frequency_max,
        capacity_min=capacity_min,
        capacity_max=capacity_max,
        cas_latency_min=cas_latency_min,
        cas_latency_max=cas_latency_max,
        modules_count_min=modules_count_min,
        modules_count_max=modules_count_max,
        certification=certification,
        modularity=modularity,
        power_min=power_min,
        power_max=power_max,
        interface=interface,
        form_factor=form_factor,
        read_speed_min=read_speed_min,
        read_speed_max=read_speed_max,
        write_speed_min=write_speed_min,
        write_speed_max=write_speed_max,
        rpm_min=rpm_min,
        rpm_max=rpm_max,
        tdp_support_min=tdp_support_min,
        tdp_support_max=tdp_support_max,
        noise_level_min=noise_level_min,
        noise_level_max=noise_level_max,
        fan_count_min=fan_count_min,
        fan_count_max=fan_count_max,
        height_min=height_min,
        height_max=height_max,
        cooling_type=cooling_type,
        socket_support=socket_support,
    )

    if search:
        search_term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(search_term),
                Product.brand.ilike(search_term),
                Product.subcategory.ilike(search_term),
            )
        )

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)

    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    result = await db.execute(stmt)
    products = result.unique().scalars().all()

    build_context = build_context_from_build(build)

    candidate_payloads = []
    for product in products:
        specs: dict[str, object] = {}

        if product.cpu_spec:
            specs = {
                "manufacturer": product.cpu_spec.manufacturer,
                "socket": product.cpu_spec.socket,
                "tdp": product.cpu_spec.tdp,
                "cores": product.cpu_spec.cores,
                "threads": product.cpu_spec.threads,
                "base_clock": product.cpu_spec.base_clock,
                "boost_clock": product.cpu_spec.boost_clock,
                "l3_cache": product.cpu_spec.l3_cache,
                "performance": product.cpu_spec.performance_score,
                "graphics_model": product.cpu_spec.graphics_model,
            }
        elif product.motherboard_spec:
            specs = {
                "name": product.name,
                "brand": product.brand,
                "socket": product.motherboard_spec.socket,
                "chipset": product.motherboard_spec.chipset,
                "ram_type": product.motherboard_spec.ram_type,
                "max_ram": product.motherboard_spec.max_ram,
                "memory_slots": product.motherboard_spec.memory_slots,
                "pcie_x1_slots": product.motherboard_spec.pcie_x1_slots,
                "m2_slots": product.motherboard_spec.m2_slots,
                "sata_ports": product.motherboard_spec.sata_ports,
                "total_channels": product.motherboard_spec.total_channels,
                "form_factor": product.motherboard_spec.form_factor,
                "min_memory_frequency": product.motherboard_spec.min_memory_frequency,
                "max_memory_frequency": product.motherboard_spec.max_memory_frequency,
                "sys_fan": product.motherboard_spec.sys_fan,
            }
        elif product.ram_spec:
            specs = {
                "ram_type": product.ram_spec.ram_type,
                "frequency": product.ram_spec.frequency,
                "capacity": product.ram_spec.capacity,
                "memory_bandwidth": product.ram_spec.memory_bandwidth,
                "modules_count": product.ram_spec.modules_count,
                "cas_latency": product.ram_spec.cas_latency,
                "timings": product.ram_spec.timings,
                "voltage": product.ram_spec.voltage,
            }
        elif product.gpu_spec:
            specs = {
                "name": product.name,
                "brand": product.brand,
                "performance": product.gpu_spec.performance,
                "vram": product.gpu_spec.vram,
                "frequency": product.gpu_spec.frequency,
                "memory_type": product.gpu_spec.memory_type,
                "max_resolution": product.gpu_spec.max_resolution,
                "recommended_power_supply": product.gpu_spec.recommended_power_supply,
                "power_connector": product.gpu_spec.power_connector,
            }
        elif product.psu_spec:
            specs = {
                "power": product.psu_spec.power,
                "certification": product.psu_spec.certification,
                "modularity": product.psu_spec.modularity,
            }
        elif product.storage_spec:
            specs = {
                "capacity": product.storage_spec.capacity,
                "interface": product.storage_spec.interface,
                "form_factor": product.storage_spec.form_factor,
                "read_speed": product.storage_spec.read_speed,
                "write_speed": product.storage_spec.write_speed,
                "rpm": product.storage_spec.rpm,
            }
        elif product.cooler_spec:
            specs = {
                "tdp_support": product.cooler_spec.tdp_support,
                "socket_support": product.cooler_spec.socket_support,
                "cooling_type": product.cooler_spec.cooling_type,
                "noise_level": product.cooler_spec.noise_level,
                "fan_count": product.cooler_spec.fan_count,
            }

        candidate_payloads.append(
            {
                "product_id": product.id,
                "external_id": product.external_id,
                "name": product.name,
                "price": product.price,
                "image_small": product.image_small,
                "image": product.image,
                "brand": product.brand,
                "subcategory": product.subcategory,
                "specs": specs,
                "condition": (product.other_features or {}).get("condition") if product.other_features else None,
            }
        )

    ranked = rank_category_products(
        candidate_payloads,
        normalized_category,
        build.budget,
        build.goal.value,
        build_context,
        compatible_only=compatible_only,
        condition=condition,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        top_n=len(candidate_payloads),
    )

    return ranked


@router.post("/{build_id}/add", response_model=BuildDetailResponse)
async def add_component(
    build_id: int,
    payload: AddComponentRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.add_or_replace_component(
            build_id=build_id,
            user_id=current_user.id,
            category=payload.category,
            product_id=payload.product_id,
            quantity=payload.quantity,
            append=payload.append,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_build(build)


@router.get("/{build_id}", response_model=BuildDetailResponse)
async def get_build(
    build_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.get_build(build_id=build_id, user_id=current_user.id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return serialize_build(build)


@router.put("/{build_id}", response_model=BuildDetailResponse)
async def update_build(
    build_id: int,
    payload: BuildUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.update_build(
            build_id=build_id,
            user_id=current_user.id,
            name=payload.name,
            budget=payload.budget,
            goal=payload.goal,
            is_public=payload.is_public,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_build(build)


@router.delete("/{build_id}")
async def delete_build(
    build_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        await service.delete_build(build_id=build_id, user_id=current_user.id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return {"message": "Build deleted successfully"}


@router.delete("/{build_id}/component/{category}", response_model=BuildDetailResponse)
async def remove_component(
    build_id: int,
    category: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.remove_component(
            build_id=build_id,
            user_id=current_user.id,
            category=category,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_build(build)


@router.delete("/{build_id}/component/{category}/{product_id}", response_model=BuildDetailResponse)
async def remove_component_item(
    build_id: int,
    category: str,
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    service = BuilderService(db)
    try:
        build = await service.remove_component(
            build_id=build_id,
            user_id=current_user.id,
            category=category,
            product_id=product_id,
            quantity=1,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return serialize_build(build)
