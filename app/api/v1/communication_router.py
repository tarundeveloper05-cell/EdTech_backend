from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth.routes import get_current_user
from app.core.database import get_db
from app.models.communication_model import Announcement, Message, Notification
from app.models.user import User
from app.schemas.communication_schema import AnnouncementCreate, AnnouncementResponse, AnnouncementUpdate, MessageCreate, MessageResponse, NotificationCreate, NotificationResponse, NotificationUpdate
from app.services.communication_service import announcement_service, message_service, notification_service

announcement_router = APIRouter()
notification_router = APIRouter()
message_router = APIRouter()
user_communication_router = APIRouter()
communication_router = APIRouter()


def _ensure_admin(current_user: User) -> None:
    if current_user.role.role_name != "ADMIN":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action",
        )


@communication_router.get("/statistics")
async def get_communication_statistics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ensure_admin(current_user)
    total_messages = await session.scalar(select(func.count(Message.id)))
    unread_messages = await session.scalar(select(func.count(Message.id)).where(Message.is_read.is_(False)))
    total_announcements = await session.scalar(select(func.count(Announcement.id)))
    total_notifications = await session.scalar(select(func.count(Notification.id)))
    unread_notifications = await session.scalar(select(func.count(Notification.id)).where(Notification.is_read.is_(False)))
    total_communications = (total_messages or 0) + (total_announcements or 0) + (total_notifications or 0)

    return {
        "total_communications": total_communications,
        "total_messages": total_messages or 0,
        "unread_messages": unread_messages or 0,
        "total_announcements": total_announcements or 0,
        "total_notifications": total_notifications or 0,
        "unread_notifications": unread_notifications or 0,
        "delivered": total_communications,
        "failed": 0,
        "delivery_rate": 100 if total_communications else 0,
        "channels": [
            {"label": "Messages", "value": total_messages or 0},
            {"label": "Announcements", "value": total_announcements or 0},
            {"label": "Notifications", "value": total_notifications or 0},
        ],
        "audiences": [],
        "delivery": [
            {"label": "Delivered", "value": total_communications},
            {"label": "Failed", "value": 0},
        ],
        "types": [
            {"type": "Messages", "messages": total_messages or 0},
            {"type": "Announcements", "messages": total_announcements or 0},
            {"type": "Notifications", "messages": total_notifications or 0},
        ],
    }


@announcement_router.post("", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(payload: AnnouncementCreate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    return await announcement_service.create_announcement(session, payload.model_dump())
@announcement_router.get("", response_model=list[AnnouncementResponse])
async def get_announcements(session: AsyncSession = Depends(get_db)): return await announcement_service.get_announcements(session)
@announcement_router.get("/{item_id}", response_model=AnnouncementResponse)
async def get_announcement(item_id: UUID, session: AsyncSession = Depends(get_db)): return await announcement_service.get(session, item_id)
@announcement_router.put("/{item_id}", response_model=AnnouncementResponse)
async def update_announcement(item_id: UUID, payload: AnnouncementUpdate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    return await announcement_service.update_announcement(session, item_id, payload.model_dump(exclude_unset=True))
@announcement_router.delete("/{item_id}")
async def delete_announcement(item_id: UUID, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    await announcement_service.delete_announcement(session, item_id)
    return {"message": "Deleted successfully"}

notification_router = APIRouter()
@notification_router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(payload: NotificationCreate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    return await notification_service.create(session, payload.model_dump(exclude_none=True))
@notification_router.get("", response_model=list[NotificationResponse])
async def get_notifications(session: AsyncSession = Depends(get_db)): return await notification_service.list(session)
@notification_router.get("/{item_id}", response_model=NotificationResponse)
async def get_notification(item_id: UUID, session: AsyncSession = Depends(get_db)): return await notification_service.get(session, item_id)
@notification_router.put("/{item_id}", response_model=NotificationResponse)
async def update_notification(item_id: UUID, payload: NotificationUpdate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    return await notification_service.update(session, item_id, payload.model_dump(exclude_unset=True))
@notification_router.delete("/{item_id}")
async def delete_notification(item_id: UUID, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    _ensure_admin(current_user)
    await notification_service.delete(session, item_id)
    return {"message": "Deleted successfully"}
@notification_router.patch("/{item_id}/read", response_model=NotificationResponse)
async def mark_notification_read(item_id: UUID, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await notification_service.mark_as_read(session, item_id)

message_router = APIRouter()
@message_router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(payload: MessageCreate, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await message_service.send_message(session, payload.model_dump(exclude_none=True))
@message_router.get("", response_model=list[MessageResponse])
async def get_messages(session: AsyncSession = Depends(get_db)): return await message_service.list(session)
@message_router.get("/conversation", response_model=list[MessageResponse])
async def get_conversation(sender_id: UUID, receiver_id: UUID, session: AsyncSession = Depends(get_db)): return await message_service.get_conversation(session, sender_id, receiver_id)
@message_router.get("/{item_id}", response_model=MessageResponse)
async def get_message(item_id: UUID, session: AsyncSession = Depends(get_db)): return await message_service.get(session, item_id)
@message_router.delete("/{item_id}")
async def delete_message(item_id: UUID, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await message_service.delete(session, item_id)
    return {"message": "Deleted successfully"}
@message_router.patch("/{item_id}/read", response_model=MessageResponse)
async def mark_message_read(item_id: UUID, session: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await message_service.mark_as_read(session, item_id)

user_communication_router = APIRouter()
@user_communication_router.get("/{user_id}/notifications", response_model=list[NotificationResponse])
async def user_notifications(user_id: UUID, session: AsyncSession = Depends(get_db)): return await notification_service.get_notifications(session, user_id)
@user_communication_router.get("/{user_id}/messages", response_model=list[MessageResponse])
async def user_messages(user_id: UUID, session: AsyncSession = Depends(get_db)): return await message_service.get_user_messages(session, user_id)


teacher_communication_router = APIRouter()
@teacher_communication_router.get("/teacher/{teacher_id}/messages", response_model=list[MessageResponse])
async def teacher_messages(teacher_id: UUID, session: AsyncSession = Depends(get_db)):
    return await message_service.get_user_messages(session, teacher_id)
