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
    is_public: bool | None = None


class AddComponentRequest(BaseModel):
    category: str
    product_id: int
    quantity: int | None = Field(default=None, ge=1)
    append: bool = False


class BuildComponentView(BaseModel):
    product_id: int
    external_id: int | None = None
    name: str
    price: int
    category: str
    quantity: int = 1
    source: str = "user"


class BuildReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class BuildReviewView(BaseModel):
    id: int
    build_id: int
    user_id: int
    username: str
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


class BuildSuggestionRequest(BaseModel):
    category: str
    suggested_product_id: int
    quantity: int = Field(default=1, ge=1)
    comment: str | None = Field(default=None, max_length=2000)


class BuildSuggestionView(BaseModel):
    id: int
    build_id: int
    user_id: int
    username: str
    category: str
    suggested_product_id: int
    suggested_product_name: str
    suggested_product_price: int
    quantity: int
    comment: str | None = None
    status: str
    applied_by_user_id: int | None = None
    applied_by_username: str | None = None
    applied_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BuildDetailResponse(BaseModel):
    id: int
    user_id: int
    name: str
    budget: int | None
    goal: str
    is_public: bool = False
    owner_username: str | None = None
    average_rating: float | None = None
    review_count: int = 0
    suggestions: list[BuildSuggestionView] = Field(default_factory=list)
    selected_components: dict[str, BuildComponentView]
    storage_components: list[BuildComponentView] = Field(default_factory=list)
    total_price: int
    compatibility_warnings: list[str]
    reviews: list[BuildReviewView] = Field(default_factory=list)
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
    category: str | None = None
    subcategory: str | None = None
    specs: dict[str, object] = Field(default_factory=dict)
    score: float
    compatible: bool
    compatibility_details: list[str]


class ProductDetailResponse(BaseModel):
    product_id: int
    external_id: int | None = None
    name: str
    price: int | None = None
    image_small: str | None = None
    image: str | None = None
    brand: str | None = None
    category: str | None = None
    subcategory: str | None = None
    description: str | None = None
    specs: dict[str, object] = Field(default_factory=dict)
    other_features: dict[str, object] | None = None
