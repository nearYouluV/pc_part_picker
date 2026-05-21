import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base, CategoryEnum, TimestampMixin


class BuildGoalEnum(str, enum.Enum):
    ESPORTS = "esports"
    AAA = "aaa"
    OFFICE = "office"
    BALANCED = "balanced"


class PCBuild(TimestampMixin, Base):
    __tablename__ = "pc_builds"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    budget = Column(Integer, nullable=True)
    goal = Column(Enum(BuildGoalEnum), nullable=False, default=BuildGoalEnum.BALANCED)
    is_public = Column(Boolean, nullable=False, default=False, index=True)

    user = relationship("User")
    components = relationship(
        "BuildComponent",
        back_populates="build",
        cascade="all, delete-orphan",
    )
    reviews = relationship(
        "BuildReview",
        back_populates="build",
        cascade="all, delete-orphan",
    )
    suggestions = relationship(
        "BuildSuggestion",
        back_populates="build",
        cascade="all, delete-orphan",
    )


class BuildComponent(TimestampMixin, Base):
    __tablename__ = "build_components"
    __table_args__ = (
        UniqueConstraint("build_id", "category", "product_id", name="uq_build_component_category_product"),
    )

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey("pc_builds.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    source = Column(String, nullable=False, default="user")

    build = relationship("PCBuild", back_populates="components")
    product = relationship("Product")


class BuildReview(TimestampMixin, Base):
    __tablename__ = "build_reviews"
    __table_args__ = (
        UniqueConstraint("build_id", "user_id", name="uq_build_reviews_build_user"),
    )

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey("pc_builds.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)

    build = relationship("PCBuild", back_populates="reviews")
    user = relationship("User")


class BuildSuggestion(TimestampMixin, Base):
    __tablename__ = "build_suggestions"

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey("pc_builds.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    suggested_product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    comment = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    applied_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)

    build = relationship("PCBuild", back_populates="suggestions")
    user = relationship("User", foreign_keys=[user_id])
    applied_by_user = relationship("User", foreign_keys=[applied_by_user_id])
    suggested_product = relationship("Product")
