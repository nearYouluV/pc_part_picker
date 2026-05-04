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
            "tdp": getattr(cpu_spec, "tdp", None),
            "memory_support": getattr(cpu_spec, "memory_support", None),
            "max_memory": getattr(cpu_spec, "max_memory", None),
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
        cores = specs.get("cores", 0)
        manufacturer = str(specs.get("manufacturer", "")).lower()
        is_amd = manufacturer == "amd" or "amd" in name

        if goal == "esports":
            if is_amd:
                score += 20
            if "x3d" in name:
                # Strong, decisive boost for X3D CPUs in esports builds so they dominate
                # other candidates. This is intentionally large to make X3D clearly
                # preferred for esports recommendations.
                score += 20000
            if "ryzen" in name:
                score += 10
            if cores >= 8:
                score += 15
            if cores <= 6 and "x3d" not in name:
                score -= 10

        elif goal == "aaa":
            if cores >= 6:
                score += 10

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

    # --------------------------------
    # 5. RAM
    # --------------------------------
    if category == "ram":
        freq = specs.get("frequency") or 0
        capacity = specs.get("capacity") or 0
        ram_label = f"{name} {subcategory}"

        if "sodimm" in ram_label or "so-dimm" in ram_label or "so dimm" in ram_label:
            score -= 100

        if goal == "office":
            if capacity >= 16:
                score += 35
            if capacity >= 32:
                score += 10
            if capacity < 16:
                score -= 20
        else:
            if capacity >= 32:
                score += 45
            elif capacity >= 16:
                score += 15
            else:
                score -= 20

        if freq:
            # Keep speed as a small, generation-agnostic tie-breaker so DDR2, DDR3,
            # DDR4, DDR5, and future DDR6 all score consistently without hardcoded limits.
            score += min(freq / 2000, 4)

    # --------------------------------
    # 6. STORAGE (SSD meta)
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
                "socket": product.cpu_spec.socket,
                "tdp": product.cpu_spec.tdp,
                "cores": product.cpu_spec.cores,
                "memory_support": product.cpu_spec.memory_support,
                "max_memory": product.cpu_spec.max_memory,
                "performance": product.cpu_spec.performance_score,
                "graphics_model": product.cpu_spec.graphics_model,
            }
        elif getattr(product, "motherboard_spec", None):
            specs = {
                "socket": product.motherboard_spec.socket,
                "ram_type": product.motherboard_spec.ram_type,
                "max_ram": product.motherboard_spec.max_ram,
                "min_memory_frequency": product.motherboard_spec.min_memory_frequency,
                "max_memory_frequency": product.motherboard_spec.max_memory_frequency,
                "memory_slots": product.motherboard_spec.memory_slots,
            }
        elif getattr(product, "ram_spec", None):
            specs = {
                "ram_type": product.ram_spec.ram_type,
                "frequency": product.ram_spec.frequency,
                "capacity": product.ram_spec.capacity,
                "memory_bandwidth": product.ram_spec.memory_bandwidth,
                "modules_count": product.ram_spec.modules_count,
                "quantity": getattr(component, "quantity", 1) or 1,
            }
        elif getattr(product, "gpu_spec", None):
            specs = {
                "performance": product.gpu_spec.performance,
                "vram": product.gpu_spec.vram,
                "recommended_power_supply": product.gpu_spec.recommended_power_supply,
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
        if cpu_socket and board_socket:
            if board_socket == cpu_socket:
                details.append(f"Socket matches CPU: {board_socket}")
            else:
                compatible = False
                details.append(_compatibility_message("Socket", False, board_socket, cpu_socket))

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
        board_min_frequency = motherboard.get("min_memory_frequency") if motherboard else None
        board_max_frequency = motherboard.get("max_memory_frequency") if motherboard else None
        cpu_memory_support = cpu.get("memory_support") if cpu else None
        cpu_max_memory = cpu.get("max_memory") if cpu else None
        ram_capacity = specs.get("capacity")
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

        if board_max_ram and ram_capacity:
            if ram_capacity <= board_max_ram:
                details.append(f"Motherboard max RAM {board_max_ram}GB covers {ram_capacity}GB kit")
            else:
                compatible = False
                details.append(_compatibility_message("Motherboard max RAM", False, f"{board_max_ram}GB", f"{ram_capacity}GB"))

        if cpu_max_memory and ram_capacity:
            if ram_capacity <= cpu_max_memory:
                details.append(f"CPU max memory {cpu_max_memory}GB covers {ram_capacity}GB kit")
            else:
                compatible = False
                details.append(_compatibility_message("CPU max memory", False, f"{cpu_max_memory}GB", f"{ram_capacity}GB"))

        if board_min_frequency and ram_frequency and ram_frequency < board_min_frequency:
            compatible = False
            details.append(_compatibility_message("RAM frequency", False, f"{board_min_frequency}MHz+", f"{ram_frequency}MHz"))

        if board_max_frequency and ram_frequency and ram_frequency > board_max_frequency:
            compatible = False
            details.append(_compatibility_message("RAM frequency", False, f"up to {board_max_frequency}MHz", f"{ram_frequency}MHz"))

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
        used_keywords = ("used", "ref", "востановленно")
        is_used = any(k in name_lower or k in sub_lower or k in brand_lower or k in cond_lower for k in used_keywords)
        if is_used:
            score -= 80
            compatibility_details.insert(0, "Detected used/refurbished item — deprioritized in recommendations")

        # budget / x3d flags used for deterministic sorting
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

        name_lower = str(product.get("name", "") or "").lower()
        x3d = "x3d" in name_lower

        ranked.append(
            {
                **product,
                "score": round(score, 2),
                "compatible": compatible,
                "compatibility_details": compatibility_details,
                "in_budget": in_budget,
                "x3d": x3d,
            }
        )

    if sort_by == "price_low":
        ranked.sort(key=lambda item: (item.get("price", 0), not item.get("compatible", False), -item.get("score", 0)))
    elif sort_by == "price_high":
        ranked.sort(key=lambda item: (-item.get("price", 0), not item.get("compatible", False), -item.get("score", 0)))
    else:
        # Recommended sorting: put X3D first for esports, otherwise prefer in-budget items,
        # then compatibility, then score, then prefer lower price as tiebreaker.
        if goal == "esports":
            # Prioritize items that fit the budget first, then prefer X3D CPUs,
            # then compatibility, then raw score. This keeps in-budget items
            # most relevant while still promoting X3D strongly inside that group.
            ranked.sort(
                key=lambda item: (
                    item.get("in_budget", False),
                    item.get("x3d", False),
                    item.get("compatible", False),
                    item.get("score", 0),
                    -item.get("price", 0),
                ),
                reverse=True,
            )
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