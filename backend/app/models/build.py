import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UniqueConstraint
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

    user = relationship("User")
    components = relationship(
        "BuildComponent",
        back_populates="build",
        cascade="all, delete-orphan",
    )


class BuildComponent(TimestampMixin, Base):
    __tablename__ = "build_components"
    __table_args__ = (
        UniqueConstraint("build_id", "category", name="uq_build_component_category"),
    )

    id = Column(Integer, primary_key=True)
    build_id = Column(Integer, ForeignKey("pc_builds.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(Enum(CategoryEnum), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    build = relationship("PCBuild", back_populates="components")
    product = relationship("Product")
