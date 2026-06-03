from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domains.notification.entity import NotificationEntity, NotificationType
from database.models.notification_model import NotificationModel


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_entity(self, notification: NotificationModel) -> NotificationEntity:
        notification_type = notification.notification_type
        if not isinstance(notification_type, NotificationType):
            notification_type = NotificationType(notification_type)

        return NotificationEntity(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            notification_type=notification_type,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at,
            related_item_id=notification.related_item_id,
            related_claim_id=notification.related_claim_id,
        )

    async def create(
        self,
        notification: NotificationEntity,
    ) -> NotificationEntity:
        notification = NotificationModel(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            notification_type=notification.notification_type.value,
            is_read=notification.is_read,
            created_at=notification.created_at or datetime.now(),
            read_at=notification.read_at,
            related_item_id=notification.related_item_id,
            related_claim_id=notification.related_claim_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return self._to_entity(notification)

    async def get_for_user(self, user_id: int) -> list[NotificationEntity]:
        result = await self.db.execute(
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
        )
        notifications = result.scalars().all()
        return [self._to_entity(notification) for notification in notifications]

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read.is_(False))
        )
        return int(result.scalar_one())

    async def mark_read(self, notification_id: int, user_id: int) -> NotificationEntity | None:
        result = await self.db.execute(
            select(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
        )
        notification = result.scalars().first()
        if not notification:
            return None

        notification.is_read = True
        notification.read_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(notification)
        return self._to_entity(notification)

    async def mark_all_read(self, user_id: int) -> int:
        result = await self.db.execute(
            select(NotificationModel).where(NotificationModel.user_id == user_id).where(NotificationModel.is_read.is_(False))
        )
        notifications = result.scalars().all()
        now = datetime.now()

        for notification in notifications:
            notification.is_read = True
            notification.read_at = now

        await self.db.commit()
        return len(notifications)

    async def get_by_id(self, notification_id: int, user_id: int) -> NotificationEntity | None:
        result = await self.db.execute(
            select(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
        )
        notification = result.scalars().first()
        if not notification:
            return None
        return self._to_entity(notification)