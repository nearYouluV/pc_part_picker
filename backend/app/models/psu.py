from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class PSU(Base):
    __tablename__ = "psus"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    power = Column(Integer)  # Watts
    certification = Column(String)  # 80+ Bronze, Gold
    pfc = Column(String)  # Active, Passive
    video_connector = Column(String)  # 6-pin, 8-pin, etc.
    modularity = Column(Boolean)

    product = relationship("Product", back_populates="psu_spec")