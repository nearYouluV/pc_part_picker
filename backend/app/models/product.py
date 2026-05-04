from sqlalchemy import Column, Integer, String, Enum, JSON
from sqlalchemy.orm import relationship
from .base import Base, CategoryEnum


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)

    # базові дані з маркетплейсу
    external_id = Column(Integer, unique=True, nullable=True)

    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image_small = Column(String, nullable=True)
    image = Column(String, nullable=True)
    url = Column(String, nullable=True)

    # класифікація (логічний рівень)
    category = Column(Enum(CategoryEnum), nullable=False)
    subcategory = Column(String, nullable=True)

    # metadata (корисно для AI/фільтрації)
    brand = Column(String, nullable=True)

    other_features = Column(JSON, nullable=True)  # JSON для зберігання додаткових характеристик
    # --- relationships до spec таблиць ---

    cpu_spec = relationship("CPU", back_populates="product", uselist=False, cascade="all, delete-orphan")
    gpu_spec = relationship("GPU", back_populates="product", uselist=False, cascade="all, delete-orphan")
    motherboard_spec = relationship("Motherboard", back_populates="product", uselist=False, cascade="all, delete-orphan")
    ram_spec = relationship("RAM", back_populates="product", uselist=False, cascade="all, delete-orphan")
    psu_spec = relationship("PSU", back_populates="product", uselist=False, cascade="all, delete-orphan")
    storage_spec = relationship("StorageSpec", back_populates="product", uselist=False, cascade="all, delete-orphan")
    cooler_spec = relationship("CoolingSpec", back_populates="product", uselist=False, cascade="all, delete-orphan")