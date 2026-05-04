from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Motherboard(Base):
    __tablename__ = "motherboards"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)

    socket = Column(String, nullable=False)
    chipset = Column(String)
    ram_type = Column(String)  # DDR4 / DDR5
    max_ram = Column(Integer)
    memory_slots = Column(Integer)
    pcie_x1_slots = Column(Integer)
    m2_slots = Column(Integer)
    sata_ports = Column(Integer)
    total_channels = Column(Integer)
    form_factor = Column(String)  # ATX / Micro-ATX / Mini-ITX
    min_memory_frequency = Column(Integer)  # in MHz
    max_memory_frequency = Column(Integer)  # in MHz
    sys_fan = Column(Integer)  # number of system fan headers

    product = relationship("Product", back_populates="motherboard_spec")
