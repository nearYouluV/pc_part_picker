from sqlalchemy import JSON, Column, Integer, String, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class CoolingSpec(Base):
    __tablename__ = "cooling_specs"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    cooling_type = Column(String)  # AIR / WATER
    tdp_support = Column(Integer)  # max TDP
    fan_size = Column(Integer, nullable=True)  # mm
    radiator_size = Column(String, nullable=True)  # 120/240/360
    noise_level = Column(Integer, nullable=True)
    tower_type = Column(String, nullable=True)  # single/dual
    connection = Column(String, nullable=True)  # 3-pin / 4-pin
    fan_rpm = Column(String, nullable=True)  # range in RPM e.g. "800-2000"
    heatpipes = Column(Integer, nullable=True)
    airflow = Column(Integer, nullable=True)  # CFM
    fan_count = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)  # mm
    socket_support = Column(ARRAY(String), nullable=True)  # list of supported CPU sockets, e.g. ["LGA1200", "AM4"]
    radiator_size = Column(Integer, nullable=True)  # mm

    product = relationship("Product", back_populates="cooler_spec")