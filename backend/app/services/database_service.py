from datetime import datetime, timezone
from typing import Type, TypeVar, List, Optional, Any, Dict
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, Enum, JSON, case, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import joinedload

from app.logging_config import get_logger
from app.models import product, cpu, gpu, motherboard, ram, psu, cooling, storage, Chats, ChatMessage
logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class DatabaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================================================
    # 1. UPSERT LAYER
    # =========================================================

    async def _get_product_by_external_id(self, external_id: int):
        stmt = select(product.Product).where(
            product.Product.external_id == external_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_spec(self, spec_model: Type[ModelType], product_id: int):
        stmt = select(spec_model).where(spec_model.product_id == product_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_product_with_spec(
        self,
        external_id: int,
        product_data: Dict[str, Any],
        spec_model: Type[ModelType],
        spec_data: Dict[str, Any]
    ) -> product.Product:

        product_table = product.Product.__table__
        insert_stmt = pg_insert(product_table).values(
            external_id=external_id,
            **product_data,
        )

        update_values: Dict[str, Any] = {
            "price": insert_stmt.excluded.price,
        }

        for field_name, column in product_table.c.items():
            if field_name in {"id", "external_id", "price"} or field_name not in product_data:
                continue

            # Skip Enum and JSON types - only set on INSERT, never on conflict
            if isinstance(column.type, (Enum, JSON)):
                continue

            excluded_value = insert_stmt.excluded[field_name]
            current_value = column

            if isinstance(column.type, String):
                update_values[field_name] = case(
                    (
                        (current_value.is_(None) | (current_value == "")),
                        excluded_value,
                    ),
                    else_=current_value,
                )

        upsert_stmt = (
            insert_stmt.on_conflict_do_update(
                index_elements=[product_table.c.external_id],
                set_=update_values,
            )
            .returning(product_table.c.id)
        )

        product_id = await self.db.scalar(upsert_stmt)
        if product_id is None:
            raise RuntimeError("Failed to upsert product")

        obj = await self.db.get(product.Product, product_id)
        if obj is None:
            raise RuntimeError("Failed to load upserted product")

        # -----------------------
        # SPEC UPSERT
        # -----------------------
        spec = await self._get_spec(spec_model, obj.id)

        if spec:
            for k, v in spec_data.items():
                setattr(spec, k, v)
        else:
            spec = spec_model(product_id=obj.id, **spec_data)
            self.db.add(spec)

        return obj

    async def commit(self):
        await self.db.commit()

    # =========================================================
    # 2. READ LAYER
    # =========================================================

    def _with_all_specs(self, stmt):
        return stmt.options(
            joinedload(product.Product.cpu_spec),
            joinedload(product.Product.gpu_spec),
            joinedload(product.Product.motherboard_spec),
            joinedload(product.Product.ram_spec),
            joinedload(product.Product.storage_spec),
            joinedload(product.Product.cooler_spec),
            joinedload(product.Product.psu_spec),
        )

    async def get_product_by_external_id(
        self,
        external_id: int,
        with_specs: bool = True
    ) -> Optional[product.Product]:

        stmt = select(product.Product).where(
            product.Product.external_id == external_id
        )

        if with_specs:
            stmt = self._with_all_specs(stmt)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_products_by_category(
        self,
        category: product.CategoryEnum,
        limit: int = 100,
        offset: int = 0,
        with_specs: bool = False
    ) -> List[product.Product]:

        stmt = (
            select(product.Product)
            .where(product.Product.category == category)
            .limit(limit)
            .offset(offset)
        )

        if with_specs:
            stmt = self._with_all_specs(stmt)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_products(
        self,
        query: str,
        limit: int = 50
    ) -> List[product.Product]:

        stmt = (
            select(product.Product)
            .where(product.Product.name.ilike(f"%{query}%"))
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================================================
    # 3. COMPONENT QUERIES
    # =========================================================

    async def get_cpus(self, limit: int = 50):
        stmt = select(cpu.CPU).options(joinedload(cpu.CPU.product)).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_gpus(self, limit: int = 50):
        stmt = select(gpu.GPU).options(joinedload(gpu.GPU.product)).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_motherboards_by_socket(self, socket: str):
        stmt = (
            select(motherboard.Motherboard)
            .where(motherboard.Motherboard.socket == socket)
            .options(joinedload(motherboard.Motherboard.product))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_rams_by_type(self, ram_type: str):
        stmt = (
            select(ram.RAM)
            .where(ram.RAM.ram_type == ram_type)
            .options(joinedload(ram.RAM.product))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_storage(self, limit: int = 100):
        stmt = (
            select(storage.StorageSpec)
            .options(joinedload(storage.StorageSpec.product))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_psu_by_power(self, min_power: int):
        stmt = (
            select(psu.PSU)
            .where(psu.PSU.power >= min_power)
            .options(joinedload(psu.PSU.product))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_coolers(self, socket: str, min_tdp: int):
        stmt = (
            select(cooling.CoolingSpec)
            .where(cooling.CoolingSpec.tdp_support >= min_tdp)
            .options(joinedload(cooling.CoolingSpec.product))
        )
        result = await self.db.execute(stmt)

        coolers = result.scalars().all()

        return [
            c for c in coolers
            if socket in (c.socket_support or "")
        ]


class ChatService:
    """Service layer for chat operations"""

    @staticmethod
    async def create_chat(db: AsyncSession, user_id: int, result_id: int = None):
        """Create a new chat session"""
        chat = Chats(
            id=uuid4(),
            user_id=user_id,
            result_id=result_id,
            created_at=datetime.now(timezone.utc)
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def get_or_create_chat_for_result(db: AsyncSession, user_id: int, result_id: int):
        """Get or create a chat session for a specific result"""
        result = await db.execute(
            select(Chats)
            .where(Chats.user_id == user_id, Chats.result_id == result_id)
        )
        chat = result.scalar_one_or_none()

        if not chat:
            chat = await ChatService.create_chat(db, user_id, result_id)

        return chat

    @staticmethod
    async def create_message(
            db: AsyncSession,
            chat_id: str,
            message: str,
            role: str = "user",
            ) -> ChatMessage:
        """Create a new chat message"""
        msg = ChatMessage(
            id=uuid4(),
            chat_id=chat_id,
            role=role,
            content=message,
            created_at=datetime.now(timezone.utc)
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    @staticmethod
    async def get_chat_messages(db: AsyncSession, user_id: int, chat_id: str):
        """Get chat messages for a specific chat session"""
        if not chat_id:
            return []

        # Get all messages for this chat
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc())
        )

        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages]
