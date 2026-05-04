from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class CPU(Base):
    __tablename__ = "cpus"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    manufacturer = Column(String, nullable=False)
    socket = Column(String, nullable=False)
    cores = Column(Integer)
    threads = Column(Integer)
    base_clock = Column(Float)
    boost_clock = Column(Float)
    tdp = Column(Integer)
    memory_support = Column(String)
    max_memory = Column(Integer)
    l3_cache = Column(Integer)
    pcie_support = Column(String)
    performance_score = Column(Integer)
    graphics_model = Column(String, nullable=True)

    product = relationship("Product", back_populates="cpu_spec")