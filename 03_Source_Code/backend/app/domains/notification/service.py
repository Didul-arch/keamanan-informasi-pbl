from backend.app.domains.claim.entity import ClaimEntity, ClaimStatus
from backend.app.domains.notification.entity import NotificationEntity, NotificationType
from backend.app.infrastructure.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo

    async def create_for_claim_submission(self, claim: ClaimEntity, reporter_user_id: int, item_title: str) -> NotificationEntity:
        notification = NotificationEntity(
            id=None,
            user_id=reporter_user_id,
            title="Ada klaim baru",
            message=f"Item '{item_title}' baru saja diklaim.",
            notification_type=NotificationType.CLAIM_SUBMITTED,
            related_item_id=claim.item_id,
            related_claim_id=claim.id,
        )
        return await self.notification_repo.create(notification)

    async def create_for_claim_review(self, claim: ClaimEntity) -> NotificationEntity:
        if claim.status == ClaimStatus.APPROVED:
            notification_type = NotificationType.CLAIM_APPROVED
            title = "Claim disetujui"
        else:
            notification_type = NotificationType.CLAIM_REJECTED
            title = "Claim ditolak"

        notification = NotificationEntity(
            id=None,
            user_id=claim.claimer_id,
            title=title,
            message=f"Claim untuk item ID {claim.item_id} telah {claim.status.value}.",
            notification_type=notification_type,
            related_item_id=claim.item_id,
            related_claim_id=claim.id,
        )
        return await self.notification_repo.create(notification)

    async def get_my_notifications(self, user_id: int) -> list[NotificationEntity]:
        return await self.notification_repo.get_for_user(user_id)

    async def get_unread_count(self, user_id: int) -> int:
        return await self.notification_repo.get_unread_count(user_id)

    async def mark_read(self, notification_id: int, user_id: int) -> NotificationEntity | None:
        notification = await self.notification_repo.get_by_id(notification_id, user_id)
        if not notification:
            return None

        notification.mark_as_read()
        return await self.notification_repo.mark_read(notification_id, user_id)

    async def mark_all_read(self, user_id: int) -> int:
        return await self.notification_repo.mark_all_read(user_id)
