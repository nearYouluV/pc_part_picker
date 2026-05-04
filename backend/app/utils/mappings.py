CPU_MAPPING = {
    "socket": "Socket connector (SOCKET)",
    "cores": "Number of Cores",
    "threads": "The number of flows",
    "base_clock": "CPU frequency",
    "boost_clock": "Maximum clock frequency",
    "l3_cache": "The volume of the cache l3",
    "tdp": "Thermal board",
    "memory_support": "Memory type",
    "max_memory": "Max. memory size",
    "pcie_support": "PCIe support",
    "performance_score": "Performance",
    "graphics_model": "The name of the graphic nucleus"
}

MOTHERBOARD_MAPPING = {
    "socket": "Socket connector (SOCKET)",
    "chipset" : "Chipset (North Bridge)",
    "ram_type": "Type of memory",
    "memory_slots": "Number of memory slots",
    "total_channels": "TOMAL CHANNals",
    "max_ram": "Max. memory size",
    "min_memory_frequency": "The minimum memory frequency",
    "max_memory_frequency": "Maximum memory frequency",
    "sata_ports": "The number of Sata III",
    "pcie_x1_slots": "Number PCI-E 1x",
    "m2_slots": "Number of slots M.2",
    "sys_fan": "SYS_FAN",
    "form_factor": "Form factor",
    "brand": "Brand"
}

GPU = {
    "vram": "Memory size",
    "memory_type": "Type of memory",
    "frequency": "The frequency of video memory",
    "max_resolution": "Maximum resolution",
    "performance": "Performance",
    "recommended_power_supply": "Recommended power power supply",
    "power_connector": "Connector add. Nutrition",
}

RAM = {
    "memory_bandwidth": "Passing capacity",
    "frequency": "Frequency",
    "ram_type": "Type of",
    "cas_latency": "CAS LATENCY (CL)",
    "timings": "Tailers scheme",
    "voltage": "Supply voltage",
    "capacity": "The volume of one module",
    "modules_count": "The number of modules"
}

PSU = {
    "power": "Power",
    "efficiency": "Efficiency (certificate 80 plus)",
    "pfc": "Power factor correction (PFC)",
    "video_connector": "Connection to video cards",
    "modularity": "Unfastened cables",
}


SSD_MAPPING = {
    "capacity": "Memory size",
    "interface": "Interface",
    "form_factor": "Form factor",
    "read_speed": "Reading speed",
    "write_speed": "Recording speed",
    "memory_cells": "Type of memory cells"
}

HDD_MAPPING = {
    "capacity": "Memory size",
    "interface": "Interface",
    "form_factor": "Form factor",
    "read_speed": "Data transmission speed",
    "write_speed": "Data transmission speed",
    "rpm": "Spindle rotation speed"
}

AIR_COOLING_MAPPING = {
    "tdp_support": "Maximum TDP",
    "fan_size" : "Diameter",
    "tower_type": "Tower of the tower",
    "connection": "Connection",
    "fan_rpm": "Fan rotation speed",
    "noise_level": "Noise level",
    "airflow": "Air flow",
    "heatpipes": "The number of heat pipes",
    "fan_count": "The number of fans",
    "height": "Cooler height",
}

WATER_COOLING_MAPPING = {
    "fan_size" : "Diameter",
    "connection": "Connection",
    "fan_rpm": "Fan rotation speed",
    "airflow": "Air flow",
    "fan_count": "The number of fans",
    "radiator_size": "Type of"
}


BASE_MAPPINGS = {
    "cpu": CPU_MAPPING,
    "gpu": GPU,
    "ram": RAM,
    "motherboard": MOTHERBOARD_MAPPING,
    "psu": PSU,
}

STORAGE_MAPPINGS = {
    "ssd": SSD_MAPPING,
    "hdd": HDD_MAPPING,
}

COOLING_MAPPINGS = {
    "air_cooling": AIR_COOLING_MAPPING,
    "liquid_cooling": WATER_COOLING_MAPPING
}

CATEGORY_MAPPINGS = {
    "gpu": 397,
    "cpu": 398,
    "hdd": 399,
    "motherboard": 400,
    "ram": 403,
    "ssd": 407,
    "air_cooling" : 1317,
    "liquid_cooling" : 2381,
    "psu" : 406,
}




BUDGET_DISTRIBUTION = {
    "esports": {
        "cpu": (0.22, 0.30),
        "gpu": (0.15, 0.25),
        "ram": (0.22, 0.30),
        "storage": (0.05, 0.10),
        "motherboard": (0.10, 0.15),
        "psu": (0.07, 0.10),
        "igpu_allowed": False
    },
    "aaa": {
        "cpu": (0.12, 0.20),
        "gpu": (0.35, 0.45),
        "ram": (0.18, 0.25),
        "storage": (0.06, 0.12),
        "motherboard": (0.08, 0.12),
        "psu": (0.07, 0.12),
        "igpu_allowed": False
    },
    "balanced": {
        "cpu": (0.18, 0.25),
        "gpu": (0.25, 0.35),
        "ram": (0.20, 0.28),
        "storage": (0.06, 0.12),
        "motherboard": (0.10, 0.15),
        "psu": (0.07, 0.12),
        "igpu_allowed": False
    },
    "office": {
        "cpu": (0.25, 0.35),
        "gpu": (0.00, 0.15),
        "ram": (0.30, 0.45),
        "storage": (0.10, 0.15),
        "motherboard": (0.10, 0.15),
        "psu": (0.07, 0.12),
        "igpu_allowed": True
    }
}