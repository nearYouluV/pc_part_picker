from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class GPU(Base):
    __tablename__ = "gpus"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    vram = Column(Integer)
    memory_type = Column(String)
    frequency = Column(Integer)
    max_resolution = Column(String)
    performance = Column(Integer)
    recommended_power_supply = Column(Integer)
    power_connector = Column(String)

    product = relationship("Product", back_populates="gpu_spec")
