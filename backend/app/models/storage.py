from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class StorageSpec(Base):
    __tablename__ = "storage_specs"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    capacity = Column(Integer)
    interface = Column(String)  # SATA / PCIe
    form_factor = Column(String)  # 2.5 / M.2 / 3.5
    memory_cells = Column(String)  # 3D-NAND / TLC / QLC
    read_speed = Column(Integer) # MB/s
    write_speed = Column(Integer) # MB/s
    memory_suffix = Column(String, nullable=True) # e.g "TB" or "GB"
    rpm = Column(Integer, nullable=True)

    product = relationship(
        "Product",
        back_populates="storage_spec"
    )