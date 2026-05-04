import re


def to_int(v):
    if not v:
        return None
    v = str(v).replace(" ", "")
    match = re.findall(r"\d+", str(v))
    return int(match[0]) if match else None


def to_float(v):
    if not v:
        return None
    v = str(v).replace(",", ".")
    match = re.findall(r"\d+\.?\d*", v)
    return float(match[0]) if match else None

def to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ['yes', 'true', '1', "+"]
    return bool(v)
def smart_cast(field, value):
    if value is None:
        return None

    if field in ["cores", "threads", "tdp", "max_memory", "performance", "vram", "capacity", "base_clock", "boost_clock", "frequency",
                  "min_memory_frequency", "recommended_power_supply", "memory_bandwidth", "modules_count", "fan_size", "heatpipes",
                    "fan_count", "height", "tdp_support", "radiator_size"]:
        return to_int(value)

    if field in ["voltage",  "airflow", "noise_level"]:
        return to_float(value)
    if field in ["modularity"]:
        return to_bool(value)

    if "шт." in str(value):
        value = str(value).replace("шт.", "pcs.")
    return value


def map_product(features: dict, mapping: dict) -> dict:
    result = {}

    for field, feature_name in mapping.items():
        raw = features.get(feature_name)
        result[field] = smart_cast(field, raw)

    return result