from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


def build_crud_router(
    service: Any,
    create_schema: type,
    update_schema: type,
    response_schema: type,
) -> APIRouter:
    router = APIRouter()

    @router.post("", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    async def create(payload: create_schema, session: AsyncSession = Depends(get_db)):
        return await service.create(session, payload.model_dump())

    @router.get("", response_model=list[response_schema])
    async def list_items(session: AsyncSession = Depends(get_db)):
        return await service.list(session)

    @router.get("/{item_id}", response_model=response_schema)
    async def get(item_id: UUID, session: AsyncSession = Depends(get_db)):
        return await service.get(session, item_id)

    @router.put("/{item_id}", response_model=response_schema)
    async def update(
        item_id: UUID,
        payload: update_schema,
        session: AsyncSession = Depends(get_db),
    ):
        return await service.update(
            session, item_id, payload.model_dump(exclude_unset=True)
        )

    @router.delete("/{item_id}", status_code=status.HTTP_200_OK)
    async def delete(item_id: UUID, session: AsyncSession = Depends(get_db)):
        await service.delete(session, item_id)
        return {"message": "Deleted successfully"}

    return router
