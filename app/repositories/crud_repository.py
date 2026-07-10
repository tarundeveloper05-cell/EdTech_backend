from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class CRUDRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT]):
        self.model = model

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> ModelT:
        item = self.model(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def list(self, session: AsyncSession) -> list[ModelT]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def get(self, session: AsyncSession, item_id: UUID) -> ModelT | None:
        result = await session.execute(select(self.model).where(self.model.id == item_id))
        return result.scalar_one_or_none()

    async def get_by_field(
        self,
        session: AsyncSession,
        field_name: str,
        value: Any,
        exclude_id: UUID | None = None,
    ) -> ModelT | None:
        query = select(self.model).where(getattr(self.model, field_name) == value)
        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_fields(
        self,
        session: AsyncSession,
        fields: dict[str, Any],
        exclude_id: UUID | None = None,
    ) -> ModelT | None:
        query = select(self.model)
        for field_name, value in fields.items():
            query = query.where(getattr(self.model, field_name) == value)
        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update(
        self, session: AsyncSession, item: ModelT, data: dict[str, Any]
    ) -> ModelT:
        for field, value in data.items():
            setattr(item, field, value)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete(self, session: AsyncSession, item: ModelT) -> None:
        await session.delete(item)
        await session.flush()
