from datetime import datetime

from pydantic import BaseModel, Field


ALLOWED_BUILD_CATEGORIES = {"cpu", "gpu", "ram", "storage", "motherboard", "psu", "cooler"}
ALLOWED_BUILD_GOALS = {"esports", "aaa", "office", "balanced"}


class BuildCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    budget: int | None = Field(default=None, ge=0)
    goal: str


class BuildUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    budget: int | None = Field(default=None, ge=0)
    goal: str | None = None


class AddComponentRequest(BaseModel):
    category: str
    product_id: int
    quantity: int | None = Field(default=None, ge=1)


class BuildComponentView(BaseModel):
    product_id: int
    external_id: int | None = None
    name: str
    price: int
    category: str
    quantity: int = 1


class BuildDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    budget: int | None
    goal: str
    selected_components: dict[str, BuildComponentView]
    total_price: int
    compatibility_warnings: list[str]
    created_at: datetime
    updated_at: datetime


class ProductRecommendationResponse(BaseModel):
    product_id: int
    external_id: int | None = None
    name: str
    price: int
    image_small: str | None = None
    image: str | None = None
    brand: str | None = None
    subcategory: str | None = None
    specs: dict[str, object] = Field(default_factory=dict)
    score: float
    compatible: bool
    compatibility_details: list[str]
