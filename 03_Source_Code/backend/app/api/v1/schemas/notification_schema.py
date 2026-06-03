from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None
    related_item_id: int | None = None
    related_claim_id: int | None = None


class MarkNotificationReadRequest(BaseModel):
    notification_id: int


class NotificationListResponse(BaseModel):
    data: list[NotificationResponse]
    unread_count: int