from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.builder_schemas import AddComponentRequest, BuildCreateRequest, BuildDetailResponse, BuildUpdateRequest, ProductRecommendationResponse
from app.database import get_async_db
from app.models.base import CategoryEnum
from app.models.user import User
from app.models.product import Product
from app.services.auth_service import get_current_active_user
from app.services.builder_service import BuilderService, build_warnings
from app.utils.scoring_engine import build_context_from_build, rank_category_products


router = APIRouter(prefix="/builder", tags=["builder"])


def serialize_build(build) -> BuildDetailResponse:
    selected_components = {}
    total_price = 0

    for component in build.components:
        if not component.product:
            continue

        selected_components[component.category.value] = {
            "product_id": component.product.id,
            "external_id": component.product.external_id,
            "name": component.product.name,
            "price": component.product.price,
            "category": component.product.category.value,
            "quantity": getattr(component, "quantity", 1) or 1,
        }
        total_price += component.product.price or 0

    return BuildDetailResponse(
        id=build.id,
        user_id=build.user_id,
        name=build.name,
        budget=build.budget,
        goal=build.goal.value,
        selected_components=selected_components,
        total_price=total_price,
        compatibility_warnings=build_warnings(build),
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


@router.get("/category/{category}", response_model=list[ProductRecommendationResponse])
async def list_category_products(
    category: str,
    build_id: int = Query(..., ge=1),
    compatible_only: bool = Query(True),
    search: str | None = Query(default=None, max_length=120),
    condition: str | None = Query(default=None, max_length=60),
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
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
                "performance": product.cpu_spec.performance_score,
                "graphics_model": product.cpu_spec.graphics_model,
            }
        elif product.motherboard_spec:
            specs = {
                "socket": product.motherboard_spec.socket,
                "ram_type": product.motherboard_spec.ram_type,
                "max_ram": product.motherboard_spec.max_ram,
                "min_memory_frequency": product.motherboard_spec.min_memory_frequency,
                "max_memory_frequency": product.motherboard_spec.max_memory_frequency,
            }
        elif product.ram_spec:
            specs = {
                "ram_type": product.ram_spec.ram_type,
                "frequency": product.ram_spec.frequency,
                "capacity": product.ram_spec.capacity,
                "memory_bandwidth": product.ram_spec.memory_bandwidth,
                "modules_count": product.ram_spec.modules_count,
            }
        elif product.gpu_spec:
            specs = {
                "performance": product.gpu_spec.performance,
                "vram": product.gpu_spec.vram,
                "recommended_power_supply": product.gpu_spec.recommended_power_supply,
            }
        elif product.psu_spec:
            specs = {
                "power": product.psu_spec.power,
                "certification": product.psu_spec.certification,
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
