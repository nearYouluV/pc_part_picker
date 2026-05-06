from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.builder_schemas import ALLOWED_BUILD_CATEGORIES, ALLOWED_BUILD_GOALS
from app.models.base import CategoryEnum
from app.models.build import BuildComponent, BuildGoalEnum, PCBuild
from app.models.product import Product


CATEGORY_TO_ENUM = {
    "cpu": CategoryEnum.CPU,
    "gpu": CategoryEnum.GPU,
    "ram": CategoryEnum.RAM,
    "storage": CategoryEnum.STORAGE,
    "motherboard": CategoryEnum.MOTHERBOARD,
    "psu": CategoryEnum.PSU,
    "cooler": CategoryEnum.COOLER,
}


class BuilderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _build_stmt(self, build_id: int, user_id: int):
        return (
            select(PCBuild)
            .where(PCBuild.id == build_id, PCBuild.user_id == user_id)
            .execution_options(populate_existing=True)
            .options(
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.cpu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.gpu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.motherboard_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.ram_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.psu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.storage_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.cooler_spec),
            )
        )

    def _list_builds_stmt(self, user_id: int):
        return (
            select(PCBuild)
            .where(PCBuild.user_id == user_id)
            .order_by(PCBuild.created_at.desc())
            .execution_options(populate_existing=True)
            .options(
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.cpu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.gpu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.motherboard_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.ram_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.psu_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.storage_spec),
                joinedload(PCBuild.components)
                .joinedload(BuildComponent.product)
                .joinedload(Product.cooler_spec),
            )
        )

    async def _get_build(self, build_id: int, user_id: int) -> PCBuild | None:
        result = await self.db.execute(self._build_stmt(build_id, user_id))
        return result.unique().scalar_one_or_none()

    async def list_builds(self, user_id: int) -> list[PCBuild]:
        result = await self.db.execute(self._list_builds_stmt(user_id))
        return list(result.unique().scalars().all())

    async def create_build(self, user_id: int, name: str, budget: int | None, goal: str) -> PCBuild:
        normalized_goal = goal.strip().lower()
        if normalized_goal not in ALLOWED_BUILD_GOALS:
            raise ValueError(f"Unsupported goal: {goal}")

        build = PCBuild(
            user_id=user_id,
            name=name,
            budget=budget,
            goal=BuildGoalEnum(normalized_goal),
        )
        self.db.add(build)
        await self.db.commit()
        await self.db.refresh(build)
        return build

    async def add_or_replace_component(self, build_id: int, user_id: int, category: str, product_id: int, quantity: int | None = None) -> PCBuild:
        normalized_category = category.strip().lower()
        if normalized_category not in ALLOWED_BUILD_CATEGORIES:
            raise ValueError(f"Unsupported category: {category}")

        build = await self._get_build(build_id, user_id)
        if not build:
            raise LookupError("Build not found")

        category_enum = CATEGORY_TO_ENUM[normalized_category]

        product_result = await self.db.execute(select(Product).where(Product.id == product_id))
        selected_product = product_result.scalar_one_or_none()
        if not selected_product:
            raise LookupError("Product not found")

        if selected_product.category != category_enum:
            raise ValueError("Product category mismatch")

        existing_component = next((c for c in build.components if c.category == category_enum), None)
        if existing_component:
            existing_component.product_id = product_id
            if quantity is not None:
                existing_component.quantity = quantity
        else:
            q = quantity or 1
            self.db.add(BuildComponent(build_id=build.id, category=category_enum, product_id=product_id, quantity=q))

        await self.db.commit()
        refreshed = await self._get_build(build_id, user_id)
        if not refreshed:
            raise LookupError("Build not found")
        return refreshed

    async def update_build(self, build_id: int, user_id: int, name: str | None, budget: int | None, goal: str | None) -> PCBuild:
        build = await self._get_build(build_id, user_id)
        if not build:
            raise LookupError("Build not found")

        if name is not None:
            build.name = name
        if budget is not None:
            build.budget = budget
        if goal is not None:
            normalized_goal = goal.strip().lower()
            if normalized_goal not in ALLOWED_BUILD_GOALS:
                raise ValueError(f"Unsupported goal: {goal}")
            build.goal = BuildGoalEnum(normalized_goal)

        await self.db.commit()
        refreshed = await self._get_build(build_id, user_id)
        if not refreshed:
            raise LookupError("Build not found")
        return refreshed

    async def remove_component(self, build_id: int, user_id: int, category: str) -> PCBuild:
        normalized_category = category.strip().lower()
        if normalized_category not in ALLOWED_BUILD_CATEGORIES:
            raise ValueError(f"Unsupported category: {category}")

        build = await self._get_build(build_id, user_id)
        if not build:
            raise LookupError("Build not found")

        category_enum = CATEGORY_TO_ENUM[normalized_category]
        existing_component = next((c for c in build.components if c.category == category_enum), None)
        if existing_component:
            await self.db.delete(existing_component)
            await self.db.commit()

        refreshed = await self._get_build(build_id, user_id)
        if not refreshed:
            raise LookupError("Build not found")
        return refreshed

    async def get_build(self, build_id: int, user_id: int) -> PCBuild:
        build = await self._get_build(build_id, user_id)
        if not build:
            raise LookupError("Build not found")
        return build

    async def delete_build(self, build_id: int, user_id: int) -> None:
        build = await self._get_build(build_id, user_id)
        if not build:
            raise LookupError("Build not found")

        await self.db.delete(build)
        await self.db.commit()

    @staticmethod
    async def get_build_static(db: AsyncSession, build_id: int) -> PCBuild | None:
        """Static method to get a build by ID (used by AI endpoints)"""
        result = await db.execute(
            select(PCBuild)
            .where(PCBuild.id == build_id)
            .options(
                joinedload(PCBuild.components).joinedload(BuildComponent.product),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.cpu_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.gpu_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.motherboard_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.ram_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.psu_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.storage_spec),
                joinedload(PCBuild.components).joinedload(BuildComponent.product).joinedload(Product.cooler_spec),
            )
        )
        return result.unique().scalar_one_or_none()

    async def add_component_to_build(self, build_id: int, category: str, product_id: int) -> None:
        """Add or replace a component in a build (used by AI endpoints)"""
        user_id = (await self.db.get(PCBuild, build_id)).user_id
        await self.add_or_replace_component(build_id, user_id, category, product_id)



def build_warnings(build: PCBuild) -> list[str]:
    warnings: list[str] = []

    components_by_category = {component.category.value: component for component in build.components}

    cpu_component = components_by_category.get("cpu")
    motherboard_component = components_by_category.get("motherboard")
    ram_component = components_by_category.get("ram")
    psu_component = components_by_category.get("psu")
    gpu_component = components_by_category.get("gpu")
    cooler_component = components_by_category.get("cooler")

    cpu_socket = None
    motherboard_socket = None

    if cpu_component and cpu_component.product and cpu_component.product.cpu_spec:
        cpu_socket = cpu_component.product.cpu_spec.socket
    if motherboard_component and motherboard_component.product and motherboard_component.product.motherboard_spec:
        motherboard_socket = motherboard_component.product.motherboard_spec.socket

    if cpu_socket and motherboard_socket and cpu_socket != motherboard_socket:
        warnings.append("CPU socket does not match motherboard socket")

    motherboard_ram_type = None
    selected_ram_type = None

    if motherboard_component and motherboard_component.product and motherboard_component.product.motherboard_spec:
        motherboard_ram_type = motherboard_component.product.motherboard_spec.ram_type
    if ram_component and ram_component.product and ram_component.product.ram_spec:
        selected_ram_type = ram_component.product.ram_spec.ram_type

    if motherboard_ram_type and selected_ram_type:
        # Extract DDR generation (e.g., "DDR5" from "DDR5 DIMM")
        motherboard_ddr = str(motherboard_ram_type).lower().split()[0] if motherboard_ram_type else ""
        selected_ddr = str(selected_ram_type).lower().split()[0] if selected_ram_type else ""
        if motherboard_ddr and selected_ddr and motherboard_ddr != selected_ddr:
            warnings.append("RAM type does not match motherboard RAM type")

    # Warn about RAM module counts (single-module kits and exceeding motherboard slots)
    if ram_component and ram_component.product and ram_component.product.ram_spec:
        kit_modules = ram_component.product.ram_spec.modules_count or 1
        quantity = getattr(ram_component, "quantity", 1) or 1
        total_modules = kit_modules * quantity
        if kit_modules == 1:
            warnings.append("Selected RAM kit contains only 1 module — 2 modules (dual-channel) are recommended")
        if motherboard_component and motherboard_component.product and motherboard_component.product.motherboard_spec:
            board_slots = motherboard_component.product.motherboard_spec.memory_slots or None
            if total_modules and board_slots and total_modules > board_slots:
                warnings.append(f"Selected RAM modules ({total_modules}) exceed motherboard slots ({board_slots})")

    if psu_component and psu_component.product and psu_component.product.psu_spec:
        psu_power = psu_component.product.psu_spec.power or 0
        cpu_tdp = 0
        if cpu_component and cpu_component.product and cpu_component.product.cpu_spec:
            cpu_tdp = cpu_component.product.cpu_spec.tdp or 0

        gpu_recommended_power = 0
        if gpu_component and gpu_component.product and gpu_component.product.gpu_spec:
            gpu_recommended_power = gpu_component.product.gpu_spec.recommended_power_supply or 0

        required_power = max(150 + cpu_tdp + 100, gpu_recommended_power)
        if psu_power < required_power:
            warnings.append(
                f"PSU power may be insufficient: {psu_power}W selected, at least {required_power}W recommended"
            )

    if cooler_component and cooler_component.product and cooler_component.product.cooler_spec:
        cooler_tdp_support = cooler_component.product.cooler_spec.tdp_support or 0
        cooler_type = str(cooler_component.product.cooler_spec.cooling_type or "").lower()

        cpu_tdp = 0
        if cpu_component and cpu_component.product and cpu_component.product.cpu_spec:
            cpu_tdp = cpu_component.product.cpu_spec.tdp or 0

        required_cooler_tdp = cpu_tdp + 20
        if cpu_tdp and cooler_tdp_support and cooler_tdp_support < required_cooler_tdp:
            warnings.append(
                f"Cooler may be insufficient: {cooler_tdp_support}W support selected, at least {required_cooler_tdp}W recommended"
            )

        if cpu_tdp > 150 and cooler_type and "air" in cooler_type:
            warnings.append("High CPU TDP detected (>150W): liquid cooling is recommended over air cooling")

    return warnings
