from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class RAM(Base):
    __tablename__ = "rams"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    capacity = Column(Integer)  # GB per module
    modules_count = Column(Integer)
    memory_bandwidth = Column(Integer)  # MB/s
    ram_type = Column(String)  # DDR4 / DDR5
    frequency = Column(Integer)
    cas_latency = Column(Integer)
    timings = Column(String)
    voltage = Column(Float)

    product = relationship("Product", back_populates="ram_spec")