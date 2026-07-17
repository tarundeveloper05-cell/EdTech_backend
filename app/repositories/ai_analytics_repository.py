from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analytics_model import AIAnalytics, AIChatHistory


class AIAnalyticsRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = AIAnalytics(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await session.get(AIAnalytics, item_id)
    async def get_all(self, session: AsyncSession):
        return list((await session.execute(select(AIAnalytics).order_by(AIAnalytics.generated_on.desc()))).scalars().all())
    async def delete(self, session: AsyncSession, item: AIAnalytics):
        await session.delete(item)
        await session.flush()
    async def get_by_student(self, session: AsyncSession, student_id: UUID):
        query = select(AIAnalytics).where(AIAnalytics.student_id == student_id).order_by(AIAnalytics.generated_on.desc())
        return list((await session.execute(query)).scalars().all())


class AIChatHistoryRepository:
    async def create(self, session: AsyncSession, data: dict):
        item = AIChatHistory(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get_by_id(self, session: AsyncSession, item_id: UUID): return await session.get(AIChatHistory, item_id)
    async def get_all(self, session: AsyncSession):
        return list((await session.execute(select(AIChatHistory).order_by(AIChatHistory.timestamp.desc()))).scalars().all())
    async def delete(self, session: AsyncSession, item: AIChatHistory):
        await session.delete(item)
        await session.flush()
    async def get_by_user(self, session: AsyncSession, user_id: UUID):
        query = select(AIChatHistory).where(AIChatHistory.user_id == user_id).order_by(AIChatHistory.timestamp.desc())
        return list((await session.execute(query)).scalars().all())


ai_analytics_repository = AIAnalyticsRepository()
ai_chat_history_repository = AIChatHistoryRepository()
