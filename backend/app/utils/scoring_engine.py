import re
from typing import Any

from app.utils.mappings import BUDGET_DISTRIBUTION


def _component_field(component: Any, field: str, default: Any = None) -> Any:
    if isinstance(component, dict):
        return component.get(field, default)
    return getattr(component, field, default)


def _component_specs(component: Any) -> dict[str, Any]:
    if isinstance(component, dict):
        specs = component.get("specs")
        return specs if isinstance(specs, dict) else {}

    cpu_spec = getattr(component, "cpu_spec", None)
    if cpu_spec:
        return {
            "manufacturer": getattr(cpu_spec, "manufacturer", None),
            "socket": getattr(cpu_spec, "socket", None),
            "cores": getattr(cpu_spec, "cores", None),
            "threads": getattr(cpu_spec, "threads", None),
            "base_clock": getattr(cpu_spec, "base_clock", None),
            "boost_clock": getattr(cpu_spec, "boost_clock", None),
            "tdp": getattr(cpu_spec, "tdp", None),
            "memory_support": getattr(cpu_spec, "memory_support", None),
            "max_memory": getattr(cpu_spec, "max_memory", None),
            "l3_cache": getattr(cpu_spec, "l3_cache", None),
            "performance": getattr(cpu_spec, "performance_score", None),
            "performance_score": getattr(cpu_spec, "performance_score", None),
            "graphics_model": getattr(cpu_spec, "graphics_model", None),
        }

    gpu_spec = getattr(component, "gpu_spec", None)
    if gpu_spec:
        return {
            "performance": getattr(gpu_spec, "performance", None),
            "vram": getattr(gpu_spec, "vram", None),
            "recommended_power_supply": getattr(gpu_spec, "recommended_power_supply", None),
        }

    ram_spec = getattr(component, "ram_spec", None)
    if ram_spec:
        return {
            "frequency": getattr(ram_spec, "frequency", None),
            "capacity": getattr(ram_spec, "capacity", None),
            "modules_count": getattr(ram_spec, "modules_count", None),
            "memory_bandwidth": getattr(ram_spec, "memory_bandwidth", None),
            "cas_latency": getattr(ram_spec, "cas_latency", None),
            "timings": getattr(ram_spec, "timings", None),
            "voltage": getattr(ram_spec, "voltage", None),
            "ram_type": getattr(ram_spec, "ram_type", None),
        }

    storage_spec = getattr(component, "storage_spec", None)
    if storage_spec:
        return {
            "interface": getattr(storage_spec, "interface", None),
            "form_factor": getattr(storage_spec, "form_factor", None),
            "read_speed": getattr(storage_spec, "read_speed", None),
            "rpm": getattr(storage_spec, "rpm", None),
        }

    motherboard_spec = getattr(component, "motherboard_spec", None)
    if motherboard_spec:
        return {
            "socket": getattr(motherboard_spec, "socket", None),
            "ram_type": getattr(motherboard_spec, "ram_type", None),
            "chipset": getattr(motherboard_spec, "chipset", None),
            "max_ram": getattr(motherboard_spec, "max_ram", None),
            "memory_slots": getattr(motherboard_spec, "memory_slots", None),
            "pcie_x1_slots": getattr(motherboard_spec, "pcie_x1_slots", None),
            "m2_slots": getattr(motherboard_spec, "m2_slots", None),
            "sata_ports": getattr(motherboard_spec, "sata_ports", None),
            "total_channels": getattr(motherboard_spec, "total_channels", None),
            "form_factor": getattr(motherboard_spec, "form_factor", None),
            "min_memory_frequency": getattr(motherboard_spec, "min_memory_frequency", None),
            "max_memory_frequency": getattr(motherboard_spec, "max_memory_frequency", None),
            "sys_fan": getattr(motherboard_spec, "sys_fan", None),
        }

    psu_spec = getattr(component, "psu_spec", None)
    if psu_spec:
        return {
            "power": getattr(psu_spec, "power", None),
            "certification": getattr(psu_spec, "certification", None),
        }

    cooler_spec = getattr(component, "cooler_spec", None)
    if cooler_spec:
        return {
            "tdp_support": getattr(cooler_spec, "tdp_support", None),
            "socket_support": getattr(cooler_spec, "socket_support", None),
        }

    return {}


def _int_or_default(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_ram_cas_latency(specs: dict[str, Any], ram_name: str) -> int:
    cas = _int_or_default(specs.get("cas_latency"), 0)
    if cas > 0:
        return cas

    timings = str(specs.get("timings") or "").strip().lower()
    if timings:
        # Common timing formats: "30-38-38", "CL30-36-36".
        timings_match = re.search(r"(?:cl\s*)?(\d{2})", timings)
        if timings_match:
            return _int_or_default(timings_match.group(1), 0)

    # Fallback to patterns in product names like "CL30" or "C36".
    name_match = re.search(r"\b(?:cl|c)(\d{2})\b", ram_name.lower())
    if name_match:
        return _int_or_default(name_match.group(1), 0)

    return 0


def _normalize_mhz_value(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0

    if numeric <= 0:
        return 0.0

    # Normalize obvious Hz/kHz inputs to MHz while preserving already-MHz values.
    if numeric >= 1_000_000_000:
        return numeric / 1_000_000.0
    if numeric >= 1_000_000:
        return numeric / 1_000.0

    return numeric


def _chipset_tier(chipset: Any) -> tuple[str, int]:
    text = str(chipset or "").lower()
    if not text:
        return "unknown", 0

    match = re.search(r"\b([abhxz])\s*(\d{3})\b", text)
    if not match:
        return "unknown", 0

    code = match.group(1).upper()
    series = int(match.group(2))
    generation = series // 100
    quality_digit = (series // 10) % 10

    if code == "A":
        return f"A{generation}", 10 + generation
    if code == "B":
        return f"B{generation}", 20 + generation
    if code == "X":
        return f"X{generation}", 30 + generation

    if code == "H":
        return f"H{quality_digit}", 10 + generation + quality_digit * 2

    if code == "Z":
        return f"Z{quality_digit}", 28 + generation + quality_digit * 2

    return "unknown", 0


def _cpu_model_tier_score(cpu_name: str) -> int:
    name = cpu_name.lower()

    if "ryzen 9" in name or "i9" in name:
        return 14
    if "ryzen 7" in name or "i7" in name:
        return 12
    if "ryzen 5" in name or "i5" in name:
        return 9
    if "ryzen 3" in name or "i3" in name:
        return 2

    return 5


def _cpu_is_top_tier(cpu_name: str) -> bool:
    name = cpu_name.lower()
    return any(x in name for x in ["ryzen 9", "core i9", "ultra 9", "threadripper", "x3d"])

def normalize_goal(goal: str):
    goal = goal.lower()

    if any(x in goal for x in ["cs", "valorant", "fps", "esport"]):
        return "esports"

    if any(x in goal for x in ["aaa", "cyberpunk", "story", "single"]):
        return "aaa"

    if any(x in goal for x in ["office", "work", "browser", "excel"]):
        return "office"

    return "balanced"

def score_component(component, category, budget, goal, distribution):
    price = _component_field(component, "price", 0) or 0
    specs = _component_specs(component)
    name = str(_component_field(component, "name", "") or "").lower()
    subcategory = str(_component_field(component, "subcategory", "") or "").lower()

    score = 0

    # --------------------------------
    # 1. PRICE FIT (base) - HARD BUDGET CONSTRAINT
    # --------------------------------
    min_pct, max_pct = distribution.get(category, (0, 1))
    if budget and budget > 0:
        price_pct = price / budget

        # HARD FILTER: Products way over budget get massive penalty
        if price_pct > 1.5:
            # Over 150% of budget = auto-reject to bottom
            score -= 1000
        elif price_pct > max_pct:
            # Over category limit but not catastrophic = heavy penalty
            score -= 300
        elif price_pct < min_pct:
            score -= 15
        else:
            # Within budget range = bonus
            score += 40
    else:
        score += 10

    # --------------------------------
    # 2. PERFORMANCE
    # --------------------------------
    perf = specs.get("performance") or specs.get("performance_score")
    if perf:
        score += perf * 0.4

    # --------------------------------
    # 3. CPU LOGIC
    # --------------------------------
    if category == "cpu":
        cores = _int_or_default(specs.get("cores"), 0)
        threads = _int_or_default(specs.get("threads"), 0)
        l3_cache = _int_or_default(specs.get("l3_cache"), 0)
        base_clock = _normalize_mhz_value(specs.get("base_clock"))
        boost_clock = _normalize_mhz_value(specs.get("boost_clock"))
        manufacturer = str(specs.get("manufacturer", "")).lower()

        if goal == "esports":
            # Esports: prioritize L3 cache, boost clock, and sensible core counts.
            if manufacturer == "amd" or "amd" in name:
                score += 8

            if l3_cache:
                score += l3_cache * 0.9

            if boost_clock:
                score += min(boost_clock / 450, 14)

            if base_clock:
                score += min(base_clock / 700, 6)

            if 6 <= cores <= 8:
                score += 12
            elif 9 <= cores <= 12:
                score += 6
            elif cores >= 13:
                score -= 4
            elif cores and cores < 6:
                score -= 8

            if threads >= 12:
                score += 4

            score += _cpu_model_tier_score(name)

        elif goal == "balanced":
            if cores >= 6:
                score += 10
            if l3_cache:
                score += min(l3_cache * 0.35, 28)
            if boost_clock:
                score += min(boost_clock / 600, 9)
            if base_clock:
                score += min(base_clock / 900, 4)

        elif goal == "aaa":
            if cores >= 6:
                score += 10
            if boost_clock:
                score += min(boost_clock / 800, 6)




    # --------------------------------
    # 4. GPU LOGIC
    # --------------------------------
    if category == "gpu":
        if perf:
            if goal == "aaa":
                score += perf * 0.8   # GPU = king
            elif goal == "balanced":
                score += perf * 0.6
            else:
                score += perf * 0.3

        gpu_frequency = _normalize_mhz_value(specs.get("frequency"))
        if gpu_frequency:
            score += min(gpu_frequency / 2000, 8)

    # --------------------------------
    # 5. MOTHERBOARD
    # --------------------------------
    if category == "motherboard":
        chipset_label, chipset_score = _chipset_tier(specs.get("chipset"))
        memory_slots = _int_or_default(specs.get("memory_slots"), 0)
        pcie_x1_slots = _int_or_default(specs.get("pcie_x1_slots"), 0)
        m2_slots = _int_or_default(specs.get("m2_slots"), 0)
        sata_ports = _int_or_default(specs.get("sata_ports"), 0)
        total_channels = _int_or_default(specs.get("total_channels"), 0)
        sys_fan = _int_or_default(specs.get("sys_fan"), 0)
        max_ram = _int_or_default(specs.get("max_ram"), 0)
        min_mem_freq = _normalize_mhz_value(specs.get("min_memory_frequency"))
        max_mem_freq = _normalize_mhz_value(specs.get("max_memory_frequency"))

        if chipset_score:
            score += min(chipset_score / 3, 16)

        if memory_slots:
            score += min(memory_slots * 2.2, 10)
        if max_ram:
            score += min(max_ram / 64, 8)
        if m2_slots:
            score += min(m2_slots * 2.5, 8)
        if pcie_x1_slots:
            score += min(pcie_x1_slots * 1.2, 4)
        if sata_ports:
            score += min(sata_ports * 0.4, 3)
        if total_channels:
            score += min(total_channels * 1.5, 4)
        if sys_fan:
            score += min(sys_fan * 0.8, 4)

        if max_mem_freq:
            score += min(max_mem_freq / 1000, 10)
        if min_mem_freq:
            score += min(min_mem_freq / 3000, 3)

    # --------------------------------
    # 6. RAM
    # --------------------------------
    if category == "ram":
        freq = specs.get("frequency") or 0
        capacity_per_module = _int_or_default(specs.get("capacity"), 0)
        modules_count = max(_int_or_default(specs.get("modules_count"), 1), 1)
        total_capacity = capacity_per_module * modules_count
        bandwidth = _int_or_default(specs.get("memory_bandwidth"), 0)
        cas_latency = _extract_ram_cas_latency(specs, name)
        voltage_raw = specs.get("voltage")
        ram_label = f"{name} {subcategory}"

        if "sodimm" in ram_label or "so-dimm" in ram_label or "so dimm" in ram_label:
            score -= 100

        # Prefer 32GB total kit capacity as the default sweet spot across all budgets/goals.
        if total_capacity == 32:
            score += 70
        elif total_capacity > 32:
            # Keep higher-capacity kits compatible, but below 32GB recommendations.
            score += 20
        elif total_capacity >= 16:
            score += 35
        else:
            score -= 25

        if freq:
            # Keep speed as a small, generation-agnostic tie-breaker so DDR2, DDR3,
            # DDR4, DDR5, and future DDR6 all score consistently without hardcoded limits.
            score += min(freq / 2000, 4)

        # Prefer lower real latency when CAS and frequency are both available.
        if cas_latency and freq:
            latency_ns = (cas_latency * 2000) / freq
            if latency_ns <= 10:
                score += 12
            elif latency_ns <= 11:
                score += 9
            elif latency_ns <= 12:
                score += 6
            elif latency_ns <= 13:
                score += 3
            else:
                score -= 2

        # Mild tie-breaker by memory bandwidth.
        if bandwidth:
            score += min(bandwidth / 12000, 3)

        # Slightly favor lower-voltage kits for efficiency/thermals.
        try:
            voltage = float(voltage_raw) if voltage_raw is not None else 0.0
        except (TypeError, ValueError):
            voltage = 0.0

        if voltage > 0:
            if voltage <= 1.25:
                score += 2
            elif voltage <= 1.35:
                score += 1
            else:
                score -= 1

    # --------------------------------
    # 7. STORAGE (SSD meta)
    # --------------------------------
    if category == "storage":
        interface = str(specs.get("interface", "") or "").lower()
        form_factor = str(specs.get("form_factor", "") or "").lower()
        rpm = specs.get("rpm")
        looks_like_ssd = (
            "ssd" in subcategory
            or "ssd" in name
            or "nvme" in name
            or "m.2" in form_factor
            or "pcie" in interface
            or "nvme" in interface
            or not rpm
        )

        if looks_like_ssd:
            score += 30
        else:
            score -= 10

        read = specs.get("read_speed", 0)
        if read:
            score += read / 2000

    return score

def has_igpu(cpu):
    graphics_model = _component_specs(cpu).get("graphics_model")
    return bool(graphics_model)

def filter_cpu_motherboard(cpu_list, mb_list):
    valid = []

    for cpu in cpu_list:
        for mb in mb_list:
            cpu_socket = _component_specs(cpu).get("socket")
            mb_socket = _component_specs(mb).get("socket")
            if cpu_socket and mb_socket and cpu_socket == mb_socket:
                valid.append({
                    "cpu": cpu,
                    "motherboard": mb
                })

    return valid

def select_top_candidates(components, category, budget, goal, distribution, top_n=5):
    scored = []

    for c in components:
        s = score_component(c, category, budget, goal, distribution)
        scored.append((s, c))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [c for _, c in scored[:top_n]]


def adjust_distribution(distribution, gpu_price, budget):
    if not budget or budget <= 0:
        return distribution

    gpu_pct = gpu_price / budget

    if gpu_pct > 0.45:
        distribution["cpu"] = (0.15, 0.22)
        distribution["ram"] = (0.08, 0.12)

    return distribution

def build_candidates(all_components, budget, goal_raw):
    goal = normalize_goal(goal_raw)
    distribution = BUDGET_DISTRIBUTION[goal].copy()

    result = {}

    # --------------------------------
    # 1. GPU (at the beginning because it's the most important for gaming builds and heavily influences budget distribution)
    # --------------------------------
    gpus = select_top_candidates(
        all_components.get("gpu", []),
        "gpu",
        budget,
        goal,
        distribution
    )
    result["gpu"] = gpus

    if gpus:
        distribution = adjust_distribution(distribution, gpus[0]["price"], budget)

    # --------------------------------
    # 2. CPU
    # --------------------------------
    cpus = select_top_candidates(
        all_components.get("cpu", []),
        "cpu",
        budget,
        goal,
        distribution
    )

    # --------------------------------
    # 3. MOTHERBOARD (via socket matching)
    # --------------------------------
    motherboards = all_components.get("motherboard", [])

    cpu_mb_pairs = filter_cpu_motherboard(cpus, motherboards)

    if cpu_mb_pairs:
        result["cpu"] = [pair["cpu"] for pair in cpu_mb_pairs[:5]]
        result["motherboard"] = [pair["motherboard"] for pair in cpu_mb_pairs[:5]]
    else:
        result["cpu"] = cpus
        result["motherboard"] = select_top_candidates(
            motherboards,
            "motherboard",
            budget,
            goal,
            distribution
        )

    # --------------------------------
    # 4. other components (RAM, Storage, PSU)
    # --------------------------------
    for category in ["ram", "storage", "psu"]:
        result[category] = select_top_candidates(
            all_components.get(category, []),
            category,
            budget,
            goal,
            distribution
        )

    return result


def build_context_from_build(build) -> dict[str, dict[str, Any]]:
    context: dict[str, dict[str, Any]] = {}

    for component in getattr(build, "components", []):
        product = getattr(component, "product", None)
        if not product:
            continue

        specs: dict[str, Any] = {}

        if getattr(product, "cpu_spec", None):
            specs = {
                "name": product.name,
                "brand": product.brand,
                "socket": product.cpu_spec.socket,
                "tdp": product.cpu_spec.tdp,
                "cores": product.cpu_spec.cores,
                "threads": product.cpu_spec.threads,
                "base_clock": product.cpu_spec.base_clock,
                "boost_clock": product.cpu_spec.boost_clock,
                "memory_support": product.cpu_spec.memory_support,
                "max_memory": product.cpu_spec.max_memory,
                "l3_cache": product.cpu_spec.l3_cache,
                "performance": product.cpu_spec.performance_score,
                "graphics_model": product.cpu_spec.graphics_model,
            }
        elif getattr(product, "motherboard_spec", None):
            specs = {
                "name": product.name,
                "brand": product.brand,
                "socket": product.motherboard_spec.socket,
                "chipset": product.motherboard_spec.chipset,
                "ram_type": product.motherboard_spec.ram_type,
                "max_ram": product.motherboard_spec.max_ram,
                "memory_slots": product.motherboard_spec.memory_slots,
                "pcie_x1_slots": product.motherboard_spec.pcie_x1_slots,
                "m2_slots": product.motherboard_spec.m2_slots,
                "sata_ports": product.motherboard_spec.sata_ports,
                "total_channels": product.motherboard_spec.total_channels,
                "form_factor": product.motherboard_spec.form_factor,
                "min_memory_frequency": product.motherboard_spec.min_memory_frequency,
                "max_memory_frequency": product.motherboard_spec.max_memory_frequency,
                "sys_fan": product.motherboard_spec.sys_fan,
            }
        elif getattr(product, "ram_spec", None):
            specs = {
                "name": product.name,
                "brand": product.brand,
                "ram_type": product.ram_spec.ram_type,
                "frequency": product.ram_spec.frequency,
                "capacity": product.ram_spec.capacity,
                "memory_bandwidth": product.ram_spec.memory_bandwidth,
                "modules_count": product.ram_spec.modules_count,
                "quantity": getattr(component, "quantity", 1) or 1,
            }
        elif getattr(product, "gpu_spec", None):
            specs = {
                "name": product.name,
                "brand": product.brand,
                "performance": product.gpu_spec.performance,
                "vram": product.gpu_spec.vram,
                "frequency": product.gpu_spec.frequency,
                "memory_type": product.gpu_spec.memory_type,
                "max_resolution": product.gpu_spec.max_resolution,
                "recommended_power_supply": product.gpu_spec.recommended_power_supply,
                "power_connector": product.gpu_spec.power_connector,
            }
        elif getattr(product, "psu_spec", None):
            specs = {
                "power": product.psu_spec.power,
                "certification": product.psu_spec.certification,
            }
        elif getattr(product, "storage_spec", None):
            specs = {
                "capacity": product.storage_spec.capacity,
                "interface": product.storage_spec.interface,
                "form_factor": product.storage_spec.form_factor,
                "read_speed": product.storage_spec.read_speed,
                "write_speed": product.storage_spec.write_speed,
                "rpm": product.storage_spec.rpm,
            }
        elif getattr(product, "cooler_spec", None):
            specs = {
                "tdp_support": product.cooler_spec.tdp_support,
                "socket_support": product.cooler_spec.socket_support,
                "cooling_type": product.cooler_spec.cooling_type,
                "noise_level": product.cooler_spec.noise_level,
                "fan_count": product.cooler_spec.fan_count,
            }

        context[component.category.value] = specs

    return context


def _compatibility_message(prefix: str, matches: bool, expected: Any, actual: Any) -> str:
    if matches:
        return f"{prefix} matches {actual}"

    return f"{prefix} needs {expected}, current build has {actual}"


def evaluate_component_compatibility(category: str, candidate: dict[str, Any], build_context: dict[str, dict[str, Any]]):
    specs = candidate.get("specs", {})
    details: list[str] = []
    compatible = True

    cpu = build_context.get("cpu")
    motherboard = build_context.get("motherboard")
    ram = build_context.get("ram")
    gpu = build_context.get("gpu")
    psu = build_context.get("psu")

    if category == "cpu":
        motherboard_socket = motherboard.get("socket") if motherboard else None
        cpu_socket = specs.get("socket")
        if motherboard_socket and cpu_socket:
            if cpu_socket == motherboard_socket:
                details.append(f"Socket matches motherboard: {cpu_socket}")
            else:
                compatible = False
                details.append(_compatibility_message("Socket", False, cpu_socket, motherboard_socket))
        else:
            details.append("No socket conflict with the current build")

    elif category == "motherboard":
        cpu_socket = cpu.get("socket") if cpu else None
        board_socket = specs.get("socket")
        board_chipset_label, chipset_score = _chipset_tier(specs.get("chipset"))
        cpu_name = str(cpu.get("name", "") or "").lower() if cpu else ""
        cpu_cores = _int_or_default(cpu.get("cores"), 0) if cpu else 0
        cpu_l3_cache = _int_or_default(cpu.get("l3_cache"), 0) if cpu else 0
        cpu_boost_clock = _normalize_mhz_value(cpu.get("boost_clock")) if cpu else 0.0
        if cpu_socket and board_socket:
            if board_socket == cpu_socket:
                details.append(f"Socket matches CPU: {board_socket}")
            else:
                compatible = False
                details.append(_compatibility_message("Socket", False, board_socket, cpu_socket))

        if cpu_name:
            is_top_tier_cpu = (
                _cpu_is_top_tier(cpu_name)
                or cpu_cores >= 10
                or cpu_l3_cache >= 32
                or cpu_boost_clock >= 5000
            )

            if chipset_score <= 22 and is_top_tier_cpu:
                compatible = False
                details.append(
                    "Low-tier chipset boards are not recommended for top-tier CPUs; choose a B/H6+/H7+/X/Z chipset for this processor"
                )
            elif chipset_score >= 46:
                details.append(f"{board_chipset_label}-chipset board provides the strongest platform headroom for this CPU")
            elif chipset_score >= 34:
                details.append(f"{board_chipset_label}-chipset board offers a strong fit for this CPU")
            elif chipset_score >= 24:
                details.append(f"{board_chipset_label}-chipset board offers a balanced fit for this CPU")
            else:
                details.append(f"{board_chipset_label}-chipset board is better suited for budget or entry-level CPUs")

        selected_ram_type = ram.get("ram_type") if ram else None
        board_ram_type = specs.get("ram_type")
        if selected_ram_type and board_ram_type:
            # Extract DDR generation (e.g., "DDR5" from "DDR5 DIMM")
            selected_ddr = str(selected_ram_type).lower().split()[0] if selected_ram_type else ""
            board_ddr = str(board_ram_type).lower().split()[0] if board_ram_type else ""
            if selected_ddr == board_ddr:
                details.append(f"RAM type matches: {board_ram_type}")
            else:
                compatible = False
                details.append(_compatibility_message("RAM type", False, board_ram_type, selected_ram_type))

        if not details:
            details.append("Compatible with your current CPU and RAM choices")

    elif category == "ram":
        ram_name = str(candidate.get("name", "") or "").lower()
        ram_subcategory = str(candidate.get("subcategory", "") or "").lower()
        ram_label = f"{ram_name} {ram_subcategory}"

        if "sodimm" in ram_label or "so-dimm" in ram_label or "so dimm" in ram_label:
            compatible = False
            details.append("SODIMM laptop memory does not fit a desktop PC build")

        board_ram_type = motherboard.get("ram_type") if motherboard else None
        board_max_ram = motherboard.get("max_ram") if motherboard else None
        board_min_frequency = _normalize_mhz_value(motherboard.get("min_memory_frequency")) if motherboard else 0.0
        board_max_frequency = _normalize_mhz_value(motherboard.get("max_memory_frequency")) if motherboard else 0.0
        cpu_memory_support = cpu.get("memory_support") if cpu else None
        cpu_max_memory = cpu.get("max_memory") if cpu else None
        ram_capacity_per_module = _int_or_default(specs.get("capacity"), 0)
        ram_modules_count = max(_int_or_default(specs.get("modules_count"), 1), 1)
        ram_total_capacity = ram_capacity_per_module * ram_modules_count
        ram_frequency = specs.get("frequency")
        ram_type = specs.get("ram_type")

        if board_ram_type and ram_type:
            # Extract DDR generation (e.g., "DDR5" from "DDR5 DIMM")
            board_ddr = str(board_ram_type).lower().split()[0] if board_ram_type else ""
            ram_ddr = str(ram_type).lower().split()[0] if ram_type else ""
            if board_ddr == ram_ddr:
                details.append(f"Fits motherboard RAM type: {ram_type}")
            else:
                compatible = False
                details.append(_compatibility_message("RAM type", False, ram_type, board_ram_type))
        else:
            details.append("Compatible with the current build")

        if cpu_memory_support and ram_type:
            cpu_support_text = str(cpu_memory_support).lower()
            ram_type_text = str(ram_type).lower()
            if ram_type_text in cpu_support_text:
                details.append(f"Fits CPU memory support: {cpu_memory_support}")
            else:
                compatible = False
                details.append(_compatibility_message("CPU memory support", False, ram_type, cpu_memory_support))

        if board_max_ram and ram_total_capacity:
            if ram_total_capacity <= board_max_ram:
                details.append(f"Motherboard max RAM {board_max_ram}GB covers {ram_total_capacity}GB kit")
            else:
                compatible = False
                details.append(_compatibility_message("Motherboard max RAM", False, f"{board_max_ram}GB", f"{ram_total_capacity}GB"))

        if cpu_max_memory and ram_total_capacity:
            if ram_total_capacity <= cpu_max_memory:
                details.append(f"CPU max memory {cpu_max_memory}GB covers {ram_total_capacity}GB kit")
            else:
                compatible = False
                details.append(_compatibility_message("CPU max memory", False, f"{cpu_max_memory}GB", f"{ram_total_capacity}GB"))

        ram_frequency_mhz = _normalize_mhz_value(ram_frequency)

        if board_min_frequency and ram_frequency_mhz and ram_frequency_mhz < board_min_frequency:
            compatible = False
            details.append(_compatibility_message("RAM frequency", False, f"{board_min_frequency:.0f}MHz+", f"{ram_frequency_mhz:.0f}MHz"))

        if board_max_frequency and ram_frequency_mhz and ram_frequency_mhz > board_max_frequency:
            compatible = False
            details.append(_compatibility_message("RAM frequency", False, f"up to {board_max_frequency:.0f}MHz", f"{ram_frequency_mhz:.0f}MHz"))

        # Check recommended modules count and motherboard slots
        candidate_modules = specs.get("modules_count")
        board_slots = motherboard.get("memory_slots") if motherboard else None
        if candidate_modules:
            if candidate_modules == 1:
                details.append("Warning: Kit contains only 1 module — 2 modules (dual-channel) are recommended for best performance")
            if board_slots and candidate_modules > board_slots:
                compatible = False
                details.append(_compatibility_message("RAM modules", False, f"<= {board_slots}", f"{candidate_modules}"))

    elif category == "gpu":
        required_power = specs.get("recommended_power_supply")
        psu_power = psu.get("power") if psu else None
        if required_power and psu_power:
            if psu_power >= required_power:
                details.append(f"PSU power {psu_power}W covers the recommended {required_power}W")
            else:
                compatible = False
                details.append(_compatibility_message("PSU power", False, f"{required_power}W", f"{psu_power}W"))
        else:
            details.append("Power needs will be checked against the selected PSU")

    elif category == "psu":
        required_power = 150
        cpu_tdp = cpu.get("tdp") if cpu else None
        gpu_required = gpu.get("recommended_power_supply") if gpu else None

        if cpu_tdp:
            required_power += cpu_tdp
        if gpu_required:
            required_power = max(required_power, gpu_required)

        psu_power = specs.get("power")
        if psu_power:
            if psu_power >= required_power:
                details.append(f"Provides {psu_power}W for an estimated {required_power}W requirement")
            else:
                compatible = False
                details.append(_compatibility_message("Power", False, f"{required_power}W", f"{psu_power}W"))
        else:
            details.append("Power compatibility will be checked after choosing a PSU")

    elif category == "storage":
        details.append("Storage is compatible with the current platform")
        if motherboard and specs.get("interface"):
            details.append(f"Check available {specs.get('interface')} slots on the motherboard")

    elif category == "cooler":
        cpu_socket = cpu.get("socket") if cpu else None
        cpu_tdp = cpu.get("tdp") if cpu else None
        supported_sockets = specs.get("socket_support") or []
        tdp_support = specs.get("tdp_support")

        if cpu_socket and supported_sockets:
            if cpu_socket in supported_sockets:
                details.append(f"Supports CPU socket {cpu_socket}")
            else:
                compatible = False
                details.append(f"Does not list CPU socket {cpu_socket} in supported sockets")

        if cpu_tdp and tdp_support:
            if tdp_support >= cpu_tdp:
                details.append(f"Covers CPU TDP of {cpu_tdp}W")
            else:
                compatible = False
                details.append(f"TDP support {tdp_support}W is below CPU TDP {cpu_tdp}W")

        if not details:
            details.append("Compatible with the current build")

    if not details:
        details.append("Compatible with the current build")

    return compatible, details


def rank_category_products(
    products: list[dict[str, Any]],
    category: str,
    budget: int | None,
    goal_raw: str,
    build_context: dict[str, dict[str, Any]],
    compatible_only: bool = True,
    condition: str | None = None,
    search: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    sort_by: str = "recommended",
    top_n: int | None = 30,
):
    goal = normalize_goal(goal_raw)
    distribution = BUDGET_DISTRIBUTION[goal].copy()
    search_text = (search or "").strip().lower()

    filtered_products: list[dict[str, Any]] = []
    ranked: list[dict[str, Any]] = []

    for product in products:
        name = str(product.get("name", ""))
        brand = str(product.get("brand", "") or "")
        subcategory = str(product.get("subcategory", "") or "")
        price = product.get("price") or 0
        product_condition = str(product.get("condition", "") or "").lower()

        if search_text and search_text not in name.lower() and search_text not in brand.lower() and search_text not in subcategory.lower():
            continue

        if min_price is not None and price < min_price:
            continue

        if max_price is not None and price > max_price:
            continue

        # If a strict condition filter is provided, enforce it (e.g., 'new' or 'used')
        if condition:
            if condition.lower() not in product_condition:
                # also allow simple keyword detection in name/subcategory
                cond_in_name = condition.lower() in name.lower() or condition.lower() in subcategory.lower()
                if not cond_in_name:
                    continue

        compatible, compatibility_details = evaluate_component_compatibility(category, product, build_context)
        if compatible_only and not compatible:
            continue

        product["compatible"] = compatible
        product["compatibility_details"] = compatibility_details
        filtered_products.append(product)

    for product in filtered_products:
        compatible = bool(product.get("compatible"))
        compatibility_details = list(product.get("compatibility_details") or ["Compatible with the current build"])

        price = product.get("price") or 0
        min_pct, max_pct = distribution.get(category, (0, 1))
        category_limit = int((budget or 0) * max_pct) if budget and budget > 0 else None

        if category_limit is not None and price > category_limit:
            compatibility_details.insert(
                0,
                f"Too expensive for this build target: ₴{price} (recommended up to ~₴{category_limit} for {category})",
            )

        score = score_component(product, category, budget or 0, goal, distribution)
        score += 120 if compatible else -250

        # Penalize clearly used/refurbished items so new components appear first
        name_lower = str(product.get("name", "") or "").lower()
        sub_lower = str(product.get("subcategory", "") or "").lower()
        brand_lower = str(product.get("brand", "") or "").lower()
        cond_lower = str(product.get("condition", "") or "").lower()
        used_keywords = ("used", "ref", "восстановлено", "Б/у", "б/у", "ремонт", "ремонтирован", "ремонтная", "ремонтный", "следы")
        is_used = any(k in name_lower or k in sub_lower or k in brand_lower or k in cond_lower for k in used_keywords)
        if is_used:
            score -= 80
            compatibility_details.insert(0, "Detected used/refurbished item — deprioritized in recommendations")

        # budget flags used for deterministic sorting
        category_limit = int((budget or 0) * distribution.get(category, (0, 1))[1]) if budget and budget > 0 else None
        in_budget = True
        if category_limit is not None:
            in_budget = price <= category_limit

        # RAM-specific boosts: prefer 2-module kits for dual-channel setups
        specs = product.get("specs") or {}
        if category == "ram":
            modules = specs.get("modules_count")
            if modules == 2:
                score += 30
            elif modules and modules > 2:
                score += 10

            capacity_per_module = _int_or_default(specs.get("capacity"), 0)
            modules_count = max(_int_or_default(specs.get("modules_count"), 1), 1)
            total_capacity = capacity_per_module * modules_count

            if goal == "office" and total_capacity > 16:
                compatibility_details.append(
                    "Office build note: 16GB is usually enough; higher capacities are supported but ranked lower by default"
                )
            elif goal != "office" and total_capacity > 32:
                compatibility_details.append(
                    "RAM recommendation note: 32GB is the default sweet spot; higher capacities are supported but ranked lower by default"
                )

        ranked.append(
            {
                **product,
                "score": round(score, 2),
                "compatible": compatible,
                "compatibility_details": compatibility_details,
                "in_budget": in_budget,
            }
        )

    if sort_by == "price_low":
        ranked.sort(key=lambda item: (item.get("price", 0), not item.get("compatible", False), -item.get("score", 0)))
    elif sort_by == "price_high":
        ranked.sort(key=lambda item: (-item.get("price", 0), not item.get("compatible", False), -item.get("score", 0)))
    else:
        ranked.sort(
            key=lambda item: (
                item.get("in_budget", False),
                item.get("compatible", False),
                item.get("score", 0),
                -item.get("price", 0),
            ),
            reverse=True,
        )

    if top_n is None or top_n <= 0:
        return ranked

    return ranked[:top_n]