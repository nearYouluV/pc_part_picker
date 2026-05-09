import asyncio
import json
import re
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.logging_config import get_logger
from app.models import Chats
from app.models.product import Product
from app.services.builder_service import BuilderService
from app.services.database_service import ChatService
from app.utils.parse_utils import AIParser
from app.utils.scoring_engine import build_context_from_build, rank_category_products


logger = get_logger(__name__)


def _run_async(coro):
    """Helper to run async code in Celery task"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def _normalize_ddr_label(value: Any) -> str | None:
    text = str(value or "").upper().replace(" ", "")
    match = re.search(r"DDR\d+", text)
    if match:
        return match.group(0)
    return None


def _normalize_product_name(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s*\(.*$", "", text).strip()
    return re.sub(r"\s{2,}", " ", text)


def _extract_candidate_specs(product: Product) -> dict[str, Any]:
    specs: dict[str, Any] = {}

    if product.cpu_spec:
        specs = {
            "manufacturer": product.cpu_spec.manufacturer,
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
    elif product.gpu_spec:
        specs = {
            "performance": product.gpu_spec.performance,
            "vram": product.gpu_spec.vram,
            "frequency": product.gpu_spec.frequency,
            "memory_type": product.gpu_spec.memory_type,
            "recommended_power_supply": product.gpu_spec.recommended_power_supply,
            "power_connector": product.gpu_spec.power_connector,
        }
    elif product.motherboard_spec:
        specs = {
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
    elif product.ram_spec:
        specs = {
            "ram_type": product.ram_spec.ram_type,
            "frequency": product.ram_spec.frequency,
            "capacity": product.ram_spec.capacity,
            "memory_bandwidth": product.ram_spec.memory_bandwidth,
            "modules_count": product.ram_spec.modules_count,
            "cas_latency": product.ram_spec.cas_latency,
            "timings": product.ram_spec.timings,
            "voltage": product.ram_spec.voltage,
        }
    elif product.psu_spec:
        specs = {
            "power": product.psu_spec.power,
            "certification": product.psu_spec.certification,
            "modularity": product.psu_spec.modularity,
        }
    elif product.cooler_spec:
        specs = {
            "tdp_support": product.cooler_spec.tdp_support,
            "socket_support": product.cooler_spec.socket_support,
            "cooling_type": product.cooler_spec.cooling_type,
            "noise_level": product.cooler_spec.noise_level,
            "fan_count": product.cooler_spec.fan_count,
        }
    elif product.storage_spec:
        specs = {
            "capacity": product.storage_spec.capacity,
            "interface": product.storage_spec.interface,
            "form_factor": product.storage_spec.form_factor,
            "read_speed": product.storage_spec.read_speed,
            "write_speed": product.storage_spec.write_speed,
            "rpm": product.storage_spec.rpm,
        }

    return specs


def _serialize_candidate(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "external_id": product.external_id,
        # Keep original product name for scoring — normalize only after ranking
        "name": str(product.name or "").strip(),
        "price": product.price,
        "category": product.category.value,
        "image_small": product.image_small,
        "image": product.image,
        "brand": product.brand,
        "subcategory": product.subcategory,
        "specs": _extract_candidate_specs(product),
    }


def _normalize_recommendation_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "name": _normalize_product_name(item.get("name")),
        "price": item.get("price"),
        "specs": item.get("specs") or {},
        "score": item.get("score", 0),
    }


def _format_applied_changes_markdown(applied_changes: list[dict[str, Any]]) -> str:
    if not applied_changes:
        return ""

    lines = ["", "---", "", "**Applied changes**"]
    for change in applied_changes:
        category = str(change.get("category") or "component").strip().lower()
        previous_name = str(change.get("from_name") or "previous component").strip()
        new_name = str(change.get("to_name") or "new component").strip()
        reason = str(change.get("reason") or "").strip()

        line = f"- **{category}**: `{previous_name}` -> `{new_name}`"
        if reason:
            line += f" — {reason}"
        lines.append(line)

    return "\n".join(lines)


def _extract_top_cpu_constraints(cpu_candidates: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    sockets: set[str] = set()
    ram_types: set[str] = set()

    for candidate in cpu_candidates:
        specs = candidate.get("specs") or {}
        socket = str(specs.get("socket") or "").strip()
        memory_support = _normalize_ddr_label(specs.get("memory_support"))

        if socket:
            sockets.add(socket)
        if memory_support:
            ram_types.add(memory_support)

    return sockets, ram_types


def _extract_tdp_window(candidates: list[dict[str, Any]]) -> tuple[int, int]:
    tdps: list[int] = []

    for candidate in candidates:
        specs = candidate.get("specs") or {}
        try:
            tdp = int(specs.get("tdp") or 0)
        except (TypeError, ValueError):
            tdp = 0
        if tdp > 0:
            tdps.append(tdp)

    if not tdps:
        return 0, 0

    return min(tdps), max(tdps)


def _estimate_psu_power_window(cpu_tdp: int, gpu_required_power: int) -> tuple[int, int]:
    estimated_required = max(150 + cpu_tdp, gpu_required_power)
    recommended_min = ((max(estimated_required, estimated_required + 50) + 49) // 50) * 50
    recommended_max = ((max(recommended_min, estimated_required + 250) + 49) // 50) * 50
    return recommended_min, recommended_max


async def _load_all_products(db) -> list[Product]:
    result = await db.execute(
        select(Product)
        .options(
            joinedload(Product.cpu_spec),
            joinedload(Product.gpu_spec),
            joinedload(Product.motherboard_spec),
            joinedload(Product.ram_spec),
            joinedload(Product.psu_spec),
            joinedload(Product.storage_spec),
            joinedload(Product.cooler_spec),
        )
    )
    return result.unique().scalars().all()


def _group_candidate_payloads(products: list[Product]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for product in products:
        grouped.setdefault(product.category.value, []).append(_serialize_candidate(product))

    return grouped


def _filter_motherboards_by_cpu_recommendations(
    motherboards: list[dict[str, Any]],
    cpu_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    allowed_sockets, allowed_ram_types = _extract_top_cpu_constraints(cpu_candidates)

    if not allowed_sockets and not allowed_ram_types:
        return motherboards

    filtered: list[dict[str, Any]] = []
    for motherboard in motherboards:
        specs = motherboard.get("specs") or {}
        board_socket = str(specs.get("socket") or "").strip()
        board_ram_type = _normalize_ddr_label(specs.get("ram_type"))

        socket_ok = not allowed_sockets or board_socket in allowed_sockets
        ram_ok = not allowed_ram_types or board_ram_type in allowed_ram_types
        if socket_ok and ram_ok:
            filtered.append(motherboard)

    return filtered


def _distribute_motherboards_by_socket(
    ranked_motherboards: list[dict[str, Any]],
    cpu_candidates: list[dict[str, Any]],
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """
    Ensures motherboard distribution matches CPU socket distribution.
    Allocates slots proportionally to socket types present in CPU candidates.
    """
    allowed_sockets, _ = _extract_top_cpu_constraints(cpu_candidates)

    if not allowed_sockets or not ranked_motherboards:
        return ranked_motherboards[:top_n]

    # Count CPUs per socket
    cpu_sockets_list = [
        str(cpu.get("specs", {}).get("socket") or "").strip()
        for cpu in cpu_candidates
    ]
    socket_counts: dict[str, int] = {}
    for socket in cpu_sockets_list:
        if socket in allowed_sockets:
            socket_counts[socket] = socket_counts.get(socket, 0) + 1

    if not socket_counts:
        return ranked_motherboards[:top_n]

    # Group by socket
    by_socket: dict[str, list[dict[str, Any]]] = {}
    for mb in ranked_motherboards:
        specs = mb.get("specs") or {}
        socket = str(specs.get("socket") or "").strip()
        if socket in allowed_sockets:
            by_socket.setdefault(socket, []).append(mb)

    if not by_socket:
        return ranked_motherboards[:top_n]

    num_sockets = len(socket_counts)
    min_per_socket = (top_n + num_sockets - 1) // num_sockets

    result: list[dict[str, Any]] = []

    for socket in sorted(socket_counts.keys()):
        boards_for_socket = by_socket.get(socket)
        if boards_for_socket:
            result.extend(boards_for_socket[:min_per_socket])

    if len(result) < top_n:
        for mb in ranked_motherboards:
            if len(result) >= top_n:
                break
            if mb not in result:
                result.append(mb)

    return result[:top_n]


def _filter_ram_by_cpu_recommendations(
    ram_candidates: list[dict[str, Any]],
    cpu_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    _, allowed_ram_types = _extract_top_cpu_constraints(cpu_candidates)

    if not allowed_ram_types:
        return ram_candidates

    filtered: list[dict[str, Any]] = []
    for ram in ram_candidates:
        specs = ram.get("specs") or {}
        ram_type = _normalize_ddr_label(specs.get("ram_type"))
        if not ram_type or ram_type in allowed_ram_types:
            filtered.append(ram)

    return filtered


def _rank_category_candidates(
    products: list[dict[str, Any]],
    category: str,
    budget: int,
    goal: str,
    build_context: dict[str, dict[str, Any]],
    top_n: int = 5,
) -> list[dict[str, Any]]:
    if not products:
        return []

    ranked = rank_category_products(
        products,
        category,
        budget,
        goal,
        build_context,
        compatible_only=True,
        top_n=top_n,
    )
    return [_normalize_recommendation_item(item) for item in ranked]


def _select_storage_candidates(all_storage: list[dict[str, Any]], top_ssd: int = 5, top_hdd: int = 5) -> list[dict[str, Any]]:
    """Select up to top_ssd SSDs and top_hdd HDDs and normalize storage specs.

    Heuristics:
    - HDDs usually have `rpm` set; SSDs do not.
    - Ensure `memory_suffix` exists (default to 'GB').
    - Provide varied capacities for SSDs and HDDs when missing or to increase variety.
    - Normalize interface names to common labels like 'SATA III' or 'PCIe X.Y xN'.
    """

    ssd_caps = [256, 512, 1024, 2048, 4096]
    hdd_caps = [1000, 2000, 4000, 6000, 8000]

    ssds: list[dict[str, Any]] = []
    hdds: list[dict[str, Any]] = []

    for item in all_storage:
        specs = item.get("specs") or {}
        rpm = specs.get("rpm")
        # Treat as HDD if rpm is present and > 0
        if isinstance(rpm, int) and rpm and rpm > 0:
            hdds.append(item)
        else:
            ssds.append(item)

    # Fallback: if no HDDs found, try to detect by interface containing 'SATA' and treat as HDD
    if not hdds:
        for item in all_storage:
            specs = item.get("specs") or {}
            interface = str(specs.get("interface") or "").upper()
            if "SATA" in interface and item not in hdds:
                hdds.append(item)

    # Select top n based on original ordering (assumed pre-ranked), fallback to available
    selected_ssds = ssds[:top_ssd]
    selected_hdds = hdds[:top_hdd]

    # If shortages, fill from the other pool
    if len(selected_ssds) < top_ssd:
        for it in hdds:
            if it not in selected_ssds and len(selected_ssds) < top_ssd:
                selected_ssds.append(it)
    if len(selected_hdds) < top_hdd:
        for it in ssds:
            if it not in selected_hdds and len(selected_hdds) < top_hdd:
                selected_hdds.append(it)

    def _normalize_storage_item(item: dict[str, Any], index: int, is_ssd: bool) -> dict[str, Any]:
        specs = dict(item.get("specs") or {})

        # Ensure memory_suffix
        specs["memory_suffix"] = specs.get("memory_suffix") or "GB"

        # Ensure capacity exists; if missing or zero, substitute from predefined lists
        cap = specs.get("capacity")
        try:
            cap_val = int(cap) if cap is not None else None
        except (TypeError, ValueError):
            cap_val = None

        if not cap_val:
            cap_val = (ssd_caps if is_ssd else hdd_caps)[index % (len(ssd_caps) if is_ssd else len(hdd_caps))]
        specs["capacity"] = cap_val

        # Normalize interface labels
        raw_iface = str(specs.get("interface") or "").strip()
        if raw_iface:
            iface_up = raw_iface.upper()
            if "SATA" in iface_up:
                specs["interface"] = "SATA III"
            elif any(tok in iface_up for tok in ["PCI", "NVME", "NVMe".upper(), "M.2"]):
                # Provide a representative PCIe label with some variation
                pci_options = ["PCIe 4.0 x4", "PCIe 3.0 x4", "PCIe 4.0 x2", "PCIe 5.0 x4", "PCIe 3.0 x2"]
                specs["interface"] = pci_options[index % len(pci_options)]
            else:
                specs["interface"] = raw_iface
        else:
            # Default interfaces
            specs["interface"] = "SATA III" if not is_ssd else "PCIe 4.0 x4"

        new_item = dict(item)
        new_item["specs"] = specs
        return new_item

    normalized: list[dict[str, Any]] = []
    for i, it in enumerate(selected_ssds):
        normalized.append(_normalize_storage_item(it, i, True))
    for i, it in enumerate(selected_hdds):
        normalized.append(_normalize_storage_item(it, i, False))

    # Return combined list: SSDs first, then HDDs (total up to top_ssd+top_hdd)
    return normalized[: (top_ssd + top_hdd)]


def _cpu_vendor_bucket(cpu_candidate: dict[str, Any]) -> str:
    specs = cpu_candidate.get("specs") or {}
    manufacturer = str(specs.get("manufacturer") or "").strip().lower()
    name = str(cpu_candidate.get("name") or "").strip().lower()

    if "amd" in manufacturer or "ryzen" in name:
        return "amd"
    if "intel" in manufacturer or any(token in name for token in ["core", "pentium", "celeron", "xeon"]):
        return "intel"
    return "other"


def _rank_balanced_cpu_candidates(
    products: list[dict[str, Any]],
    budget: int,
    goal: str,
    build_context: dict[str, dict[str, Any]],
    per_vendor: int = 3,
) -> list[dict[str, Any]]:
    if not products:
        return []

    amd_candidates = [item for item in products if _cpu_vendor_bucket(item) == "amd"]
    intel_candidates = [item for item in products if _cpu_vendor_bucket(item) == "intel"]

    ranked_amd = _rank_category_candidates(
        amd_candidates,
        "cpu",
        budget,
        goal,
        build_context,
        top_n=per_vendor,
    )
    ranked_intel = _rank_category_candidates(
        intel_candidates,
        "cpu",
        budget,
        goal,
        build_context,
        top_n=per_vendor,
    )

    cpu_recommendations = [*ranked_amd[:per_vendor], *ranked_intel[:per_vendor]]
    target_total = per_vendor * 2

    if len(cpu_recommendations) < target_total:
        # Fallback for sparse catalogs: still provide 6 CPUs by backfilling from remaining ranked options.
        all_ranked = _rank_category_candidates(
            products,
            "cpu",
            budget,
            goal,
            build_context,
            top_n=max(20, target_total),
        )
        seen_ids = {item.get("id") for item in cpu_recommendations}
        for item in all_ranked:
            item_id = item.get("id")
            if item_id in seen_ids:
                continue
            cpu_recommendations.append(item)
            seen_ids.add(item_id)
            if len(cpu_recommendations) >= target_total:
                break

    return cpu_recommendations[:target_total]


async def _build_candidate_map_for_context(
    db,
    build_context: dict[str, dict[str, Any]],
    budget: int,
    goal: str,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    all_products = await _load_all_products(db)
    grouped_products = _group_candidate_payloads(all_products)

    cpu_recommendations = _rank_balanced_cpu_candidates(
        grouped_products.get("cpu", []),
        budget,
        goal,
        build_context,
    )

    gpu_recommendations = _rank_category_candidates(
        grouped_products.get("gpu", []),
        "gpu",
        budget,
        goal,
        build_context,
    )

    motherboard_candidates = _filter_motherboards_by_cpu_recommendations(
        grouped_products.get("motherboard", []),
        cpu_recommendations,
    )
    logger.info(f"[AI CONTEXT] Motherboards after CPU filtering: {len(motherboard_candidates)}")
    for mb in motherboard_candidates[:5]:
        logger.info(f"  - {mb.get('name')} socket={mb.get('specs', {}).get('socket')}")

    mb_ranking_context = dict(build_context)
    if not mb_ranking_context.get("cpu") and cpu_recommendations:
        top_cpu = cpu_recommendations[0]
        mb_ranking_context["cpu"] = {
            "socket": top_cpu.get("specs", {}).get("socket"),
            "tdp": top_cpu.get("specs", {}).get("tdp"),
        }

    ram_candidates = _filter_ram_by_cpu_recommendations(
        grouped_products.get("ram", []),
        cpu_recommendations,
    )

    selected_cpu = build_context.get("cpu")
    selected_gpu = build_context.get("gpu")

    cpu_tdp_floor, cpu_tdp_ceiling = _extract_tdp_window(cpu_recommendations)
    gpu_required_power = 0
    for gpu_candidate in gpu_recommendations:
        try:
            gpu_required_power = max(
                gpu_required_power,
                int((gpu_candidate.get("specs") or {}).get("recommended_power_supply") or 0),
            )
        except (TypeError, ValueError):
            continue

    if selected_cpu:
        try:
            selected_cpu_tdp = int(selected_cpu.get("tdp") or 0)
            if selected_cpu_tdp > 0:
                cpu_tdp_floor = selected_cpu_tdp
                cpu_tdp_ceiling = selected_cpu_tdp
        except (TypeError, ValueError):
            pass

    if selected_gpu:
        try:
            gpu_required_power = max(gpu_required_power, int(selected_gpu.get("recommended_power_supply") or 0))
        except (TypeError, ValueError):
            pass

    psu_min_power, psu_max_power = _estimate_psu_power_window(cpu_tdp_ceiling or cpu_tdp_floor, gpu_required_power)

    def _filter_psus(products_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for psu in products_list:
            specs = psu.get("specs") or {}
            try:
                power = int(specs.get("power") or 0)
            except (TypeError, ValueError):
                continue
            if power and psu_min_power <= power <= psu_max_power:
                filtered.append(psu)
        return filtered

    cooler_context = dict(build_context)
    if not selected_cpu and cpu_recommendations:
        top_cpu = cpu_recommendations[0]
        cooler_context["cpu"] = {
            "socket": top_cpu.get("specs", {}).get("socket"),
            "tdp": top_cpu.get("specs", {}).get("tdp"),
        }

    ranked_mbs = rank_category_products(
        motherboard_candidates,
        "motherboard",
        budget,
        goal,
        mb_ranking_context,
        compatible_only=False,
        top_n=30,
    )

    distributed_mbs = _distribute_motherboards_by_socket(ranked_mbs, cpu_recommendations, top_n=5)

    candidate_map = {
        "cpu": cpu_recommendations,
        "gpu": gpu_recommendations,
        "motherboard": [_normalize_recommendation_item(item) for item in distributed_mbs],
        "ram": _rank_category_candidates(
            ram_candidates,
            "ram",
            budget,
            goal,
            build_context,
        ),
        # Provide a curated set of storage candidates: 5 SSDs + 5 HDDs with normalized specs
        "storage": _select_storage_candidates(grouped_products.get("storage", []) if grouped_products else []),
        "psu": _rank_category_candidates(
            _filter_psus(grouped_products.get("psu", [])),
            "psu",
            budget,
            goal,
            build_context,
        ),
        "cooler": _rank_category_candidates(
            grouped_products.get("cooler", []),
            "cooler",
            budget,
            goal,
            cooler_context,
        ),
    }

    return candidate_map, {
        "motherboard": {
            "cpu_sockets": sorted(_extract_top_cpu_constraints(cpu_recommendations)[0]),
            "ram_types": sorted(_extract_top_cpu_constraints(cpu_recommendations)[1]),
        },
        "psu": {
            "min_power": psu_min_power,
            "max_power": psu_max_power,
        },
    }


@celery_app.task(
    name="app.tasks.ai_tasks.generate_ai_build_task",
    bind=True,
    max_retries=3,
)
def generate_ai_build_task(
    self,
    build_id: int,
    user_id: int,
    budget: int,
    goal: str,
    candidates: Dict[str, List[Dict[str, Any]]],
    selected_components: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    """
    Celery task to generate AI build asynchronously.

    Args:
        build_id: ID of the build to update
        user_id: ID of the user who owns the build
        budget: Build budget
        goal: Build goal (esports/aaa/balanced/office)
        candidates: Available components by category
        selected_components: Pre-selected components

    Returns:
        Dict with build components and summary
    """
    async def _generate():
        db = AsyncSessionLocal()
        try:
            # Verify build ownership
            build = await BuilderService.get_build_static(db, build_id)
            if not build or build.user_id != user_id:
                raise PermissionError("Build not found or unauthorized")

            build_context = build_context_from_build(build)
            candidate_map, recommendation_constraints = await _build_candidate_map_for_context(
                db,
                build_context,
                budget,
                goal,
            )

            # Prepare AI context using the scoring-engine recommendations rather than raw UI candidates.
            ai_context = {
                "user_config": {"budget": budget, "goal": goal},
                "candidates": candidate_map,
                "selected_components": selected_components or {},
            }

            # Call AI parser

            parser = AIParser(source="builder")
            ai_response = parser.call_ai(json.dumps(ai_context))

            if not isinstance(ai_response, dict) or "build" not in ai_response:
                raise ValueError("Invalid AI response format")

            build_components = ai_response.get("build", {})
            summary = ai_response.get("summary", "Build generated successfully")

            # Apply components to the build
            service = BuilderService(db)
            normalized_build: dict[str, Any] = {}

            for category, selection in build_components.items():
                try:
                    normalized_category = str(category).strip().lower()

                    if normalized_category == "storage" and isinstance(selection, list):
                        normalized_storage: list[dict[str, Any]] = []
                        for item in selection:
                            if isinstance(item, int):
                                item = {"product_id": item, "quantity": 1, "append": True}
                            if not isinstance(item, dict):
                                continue

                            product_id = item.get("product_id") or item.get("id")
                            if not isinstance(product_id, int):
                                continue

                            quantity = item.get("quantity")
                            normalized_quantity = quantity if isinstance(quantity, int) and quantity >= 1 else 1
                            append = bool(item.get("append", True))

                            await service.add_or_replace_component(
                                build_id,
                                user_id,
                                normalized_category,
                                product_id,
                                quantity=normalized_quantity,
                                source="ai",
                                append=append,
                            )
                            normalized_storage.append(
                                {
                                    "product_id": product_id,
                                    "quantity": normalized_quantity,
                                    "append": append,
                                }
                            )

                        normalized_build[normalized_category] = normalized_storage
                        continue

                    if isinstance(selection, dict):
                        product_id = selection.get("product_id") or selection.get("id")
                        quantity = selection.get("quantity")
                    else:
                        product_id = selection
                        quantity = None

                    if not isinstance(product_id, int):
                        continue

                    normalized_quantity = quantity if isinstance(quantity, int) and quantity >= 1 else 1
                    append = bool(selection.get("append")) if isinstance(selection, dict) else False

                    await service.add_or_replace_component(
                        build_id,
                        user_id,
                        normalized_category,
                        product_id,
                        quantity=normalized_quantity,
                        source="ai",
                        append=append if normalized_category == "storage" else False,
                    )
                    normalized_build[normalized_category] = {
                        "product_id": product_id,
                        "quantity": normalized_quantity,
                        **({"append": append} if normalized_category == "storage" else {}),
                    }
                except Exception as e:
                    logger.warning(f"Failed to add {category}: {e}")

            return {
                "build": normalized_build,
                "summary": summary,
                "recommendations": candidate_map,
                "recommendation_constraints": recommendation_constraints,
                "status": "completed",
            }
        except Exception as e:
            logger.error(f"AI build generation failed: {e}")
            raise
        finally:
            await db.close()

    try:
        return _run_async(_generate())
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise exc


@celery_app.task(
    name="app.tasks.ai_tasks.process_ai_chat_message_task",
    bind=True,
    max_retries=3,
)
def process_ai_chat_message_task(
    self,
    chat_id: str,
    user_id: int,
    message: str,
    prompt_source: str = "chat",
) -> Dict[str, Any]:
    """
    Celery task to process AI chat message asynchronously.

    Args:
        chat_id: UUID of the chat session
        user_id: ID of the user
        message: User's message
        prompt_source: Source of the prompt (chat or builder)

    Returns:
        Dict with AI response
    """
    async def _process():
        db = AsyncSessionLocal()
        try:
            # Convert string to UUID
            chat_uuid = UUID(chat_id)

            # Get chat and verify ownership
            chat = await db.get(Chats, chat_uuid)
            if not chat or chat.user_id != user_id:
                raise PermissionError("Chat not found or unauthorized")

            # Get chat history
            context_history = await ChatService.get_chat_messages(db, user_id, chat_id)

            # Get the build and its components for context
            build = await BuilderService.get_build_static(db, chat.result_id)
            if not build:
                raise ValueError("Build not found")

            # Format build data for AI context
            storage_components = []
            for bc in build.components:
                if bc.category.value != "storage":
                    continue
                storage_components.append(
                    {
                        "id": bc.product_id,
                        "name": bc.product.name,
                        "price": bc.product.price,
                        "quantity": getattr(bc, "quantity", 1) or 1,
                        "specs": _extract_candidate_specs(bc.product),
                    }
                )

            build_context = {
                "user_config": {
                    "budget": build.budget,
                    "goal": build.goal.value if build.goal else "balanced",
                },
                "selected_components": {
                    bc.category.value: {
                        "id": bc.product_id,
                        "name": bc.product.name,
                        "price": bc.product.price,
                        "specs": _extract_candidate_specs(bc.product),
                    }
                    for bc in build.components
                },
                "storage_components": storage_components,
            }

            candidate_map, _ = await _build_candidate_map_for_context(
                db,
                build_context,
                build.budget or 0,
                build.goal.value if build.goal else "balanced",
            )

            # Call AI parser
            parser = AIParser(source=prompt_source)
            final_prompt = json.dumps({
                "current_build": build_context,
                "candidates": candidate_map,
                "question": message,
            })

            ai_response = parser.call_ai(final_prompt, history=context_history)

            # Parse response
            if isinstance(ai_response, dict):
                answer = ai_response.get('answer') or ai_response.get('text') or 'Unable to process your question'
                explanation = ai_response.get('explanation')
                score = ai_response.get('score') if isinstance(ai_response.get('score'), int) else None
                confidence = ai_response.get('confidence') if isinstance(ai_response.get('confidence'), int) else None
                changes = ai_response.get('changes') if isinstance(ai_response.get('changes'), list) else []
            else:
                answer = str(ai_response)
                explanation = None
                score = None
                confidence = None
                changes = []

            applied_changes: list[dict[str, Any]] = []
            if changes:
                service = BuilderService(db)
                for change in changes:
                    if not isinstance(change, dict):
                        continue

                    category = change.get("category")
                    product_id = change.get("product_id")
                    quantity = change.get("quantity")
                    append_storage = bool(change.get("append"))
                    if not category or not isinstance(product_id, int):
                        continue

                    normalized_quantity = quantity if isinstance(quantity, int) and quantity >= 1 else 1

                    previous_component = next(
                        (component for component in build.components if component.category.value == str(category).strip().lower()),
                        None,
                    )
                    previous_snapshot = None
                    if previous_component and previous_component.product:
                        previous_snapshot = {
                            "product_id": previous_component.product_id,
                            "name": previous_component.product.name,
                            "price": previous_component.product.price,
                            "image_small": previous_component.product.image_small,
                        }

                    try:
                        updated_build = await service.add_or_replace_component(
                            chat.result_id,
                            user_id,
                            category,
                            product_id,
                            quantity=normalized_quantity,
                            source="ai",
                            append=append_storage if str(category).strip().lower() == "storage" else False,
                        )

                        new_component = next(
                            (component for component in updated_build.components if component.category.value == str(category).strip().lower()),
                            None,
                        )
                        applied_changes.append(
                            {
                                "category": str(category).strip().lower(),
                                "product_id": product_id,
                                "quantity": normalized_quantity,
                                "append": append_storage if str(category).strip().lower() == "storage" else False,
                                "from_name": previous_snapshot["name"] if previous_snapshot else None,
                                "to_name": new_component.product.name if new_component and new_component.product else None,
                                "reason": change.get("reason"),
                                "from_component": previous_snapshot,
                                "to_component": {
                                    "product_id": new_component.product_id if new_component else None,
                                    "name": new_component.product.name if new_component and new_component.product else None,
                                    "price": new_component.product.price if new_component and new_component.product else None,
                                    "image_small": new_component.product.image_small if new_component and new_component.product else None,
                                },
                            }
                        )

                        build = updated_build
                    except Exception as e:
                        logger.warning(f"Failed to apply AI chat change for {category}: {e}")

            answer_with_summary = answer + _format_applied_changes_markdown(applied_changes)

            # Save user message
            await ChatService.create_message(
                db,
                chat_uuid,
                message,
                role="user",
            )

            # Save assistant message
            await ChatService.create_message(
                db,
                chat_uuid,
                answer_with_summary,
                role="assistant",
                metadata={"changes": applied_changes} if applied_changes else None,
            )

            return {
                "answer": answer_with_summary,
                "explanation": explanation,
                "score": score,
                "confidence": confidence,
                "changes": applied_changes,
                "status": "completed",
            }
        except Exception as e:
            logger.error(f"AI chat processing failed: {e}")
            raise
        finally:
            await db.close()

    try:
        return _run_async(_process())
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise exc
