from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.inspection import inspect as sqlalchemy_inspect

from app.database import get_async_db
from app.services.auth_service import get_current_active_user
from app.models.product import Product
from app.models.cpu import CPU
from app.models.gpu import GPU
from app.models.motherboard import Motherboard
from app.models.ram import RAM
from app.models.storage import StorageSpec
from app.models.psu import PSU
from app.models.cooling import CoolingSpec
from app.models.user import User
from app.builder_schemas import ProductDetailResponse, ProductRecommendationResponse

router = APIRouter(prefix="/product", tags=["product"])


def extract_specs(spec_obj) -> dict:
    """Extract specs from any spec model by using SQLAlchemy mapper columns."""
    if not spec_obj:
        return {}
    mapper = sqlalchemy_inspect(spec_obj.__class__)
    return {col.name: getattr(spec_obj, col.name) for col in mapper.columns if not col.name.startswith('_')}

@router.get("/search", response_model=list[ProductRecommendationResponse])
async def search_products(
    query: str = Query(..., min_length=1, max_length=120),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    stmt = select(Product).where(Product.name.ilike(f"%{query.strip()}%"))
    result = await db.execute(
        stmt.options(
            joinedload(Product.cpu_spec),
            joinedload(Product.gpu_spec),
            joinedload(Product.motherboard_spec),
            joinedload(Product.ram_spec),
            joinedload(Product.storage_spec),
            joinedload(Product.psu_spec),
            joinedload(Product.cooler_spec),
        ).limit(50)
    )

    products = result.unique().scalars().all()

    out = []
    for product in products:
        specs = {}
        if product.cpu_spec:
            specs = {"manufacturer": product.cpu_spec.manufacturer, "socket": product.cpu_spec.socket}
        elif product.ram_spec:
            specs = {"ram_type": product.ram_spec.ram_type, "capacity": product.ram_spec.capacity}
        elif product.storage_spec:
            specs = {"capacity": product.storage_spec.capacity, "interface": product.storage_spec.interface}

        out.append(ProductRecommendationResponse(
            product_id=product.id,
            external_id=product.external_id,
            name=product.name,
            price=product.price or 0,
            image_small=product.image_small,
            image=product.image,
            brand=product.brand,
            category=product.category.value if product.category else None,
            subcategory=product.subcategory,
            specs=specs,
            score=0.0,
            compatible=True,
            compatibility_details=[],
        ))

    return out


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            joinedload(Product.cpu_spec),
            joinedload(Product.gpu_spec),
            joinedload(Product.motherboard_spec),
            joinedload(Product.ram_spec),
            joinedload(Product.storage_spec),
            joinedload(Product.psu_spec),
            joinedload(Product.cooler_spec),
        )
    )

    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    specs = {}
    if product.cpu_spec:
        specs = extract_specs(product.cpu_spec)
    elif product.gpu_spec:
        specs = extract_specs(product.gpu_spec)
    elif product.motherboard_spec:
        specs = extract_specs(product.motherboard_spec)
    elif product.ram_spec:
        specs = extract_specs(product.ram_spec)
    elif product.storage_spec:
        specs = extract_specs(product.storage_spec)
    elif product.psu_spec:
        specs = extract_specs(product.psu_spec)
    elif product.cooler_spec:
        specs = extract_specs(product.cooler_spec)

    # Basic serialization
    return ProductDetailResponse(
        product_id=product.id,
        external_id=product.external_id,
        name=product.name,
        price=product.price,
        image_small=product.image_small,
        image=product.image,
        brand=product.brand,
        category=product.category.value if product.category else None,
        subcategory=product.subcategory,
        description=(product.other_features or {}).get('description') if product.other_features else None,
        specs=specs,
        other_features=product.other_features,
    )
