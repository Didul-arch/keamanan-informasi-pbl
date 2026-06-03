from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    CLAIM_SUBMITTED = "claim_submitted"
    CLAIM_APPROVED = "claim_approved"
    CLAIM_REJECTED = "claim_rejected"

@dataclass
class NotificationEntity:
    id: int | None
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    is_read: bool = False
    created_at: datetime | None = None
    read_at: datetime | None = None
    related_item_id: int | None = None
    related_claim_id: int | None = None

    def mark_as_read(self):
        if self.is_read:
            return  
        self.is_read = True
        self.read_at = datetime.now()