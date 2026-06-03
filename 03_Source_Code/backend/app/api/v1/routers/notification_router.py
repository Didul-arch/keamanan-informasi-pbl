from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from digital_signature.auth_router import get_current_user
from backend.app.api.v1.schemas.notification_schema import NotificationListResponse
from backend.app.domains.notification.service import NotificationService
from backend.app.domains.user.entity import UserEntity
from database.session import get_db
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=NotificationListResponse)
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    service = NotificationService(NotificationRepository(db))
    notifications = await service.get_my_notifications(current_user.id)
    unread_count = await service.get_unread_count(current_user.id)
    return {"data": notifications, "unread_count": unread_count}


@router.patch("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    service = NotificationService(NotificationRepository(db))
    notification = await service.mark_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification tidak ditemukan")

    return {"status": "success", "data": notification}


@router.patch("/me/read-all", response_model=dict)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    service = NotificationService(NotificationRepository(db))
    total = await service.mark_all_read(current_user.id)
    return {"status": "success", "updated_count": total}