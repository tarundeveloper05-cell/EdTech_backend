from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admission_model import AdmissionApplication, AdmissionDocument


class AdmissionApplicationRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = AdmissionApplication(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await session.get(AdmissionApplication, item_id)

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(AdmissionApplication))
        return list(result.scalars().all())

    async def get_by_status(self, session: AsyncSession, status_value: str):
        result = await session.execute(
            select(AdmissionApplication).where(AdmissionApplication.status == status_value)
        )
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, item: AdmissionApplication, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete(self, session: AsyncSession, item: AdmissionApplication) -> None:
        await session.delete(item)
        await session.flush()


class AdmissionDocumentRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = AdmissionDocument(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID):
        return await session.get(AdmissionDocument, item_id)

    async def get_all(self, session: AsyncSession):
        result = await session.execute(select(AdmissionDocument))
        return list(result.scalars().all())

    async def get_by_application(self, session: AsyncSession, application_id: UUID):
        result = await session.execute(
            select(AdmissionDocument).where(AdmissionDocument.application_id == application_id)
        )
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, item: AdmissionDocument, data: dict):
        for field, value in data.items():
            setattr(item, field, value)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def delete(self, session: AsyncSession, item: AdmissionDocument) -> None:
        await session.delete(item)
        await session.flush()


admission_application_repository = AdmissionApplicationRepository()
admission_document_repository = AdmissionDocumentRepository()
