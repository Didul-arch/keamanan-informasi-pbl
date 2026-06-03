from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ItemStatus(str, Enum):
    NOT_RETURNED = "not-returned"
    RETURNED = "returned"

class ReportType(str, Enum):
    LOST = "lost"
    FOUND = "found"

@dataclass
class ItemEntity:
    id: int | None
    title: str
    description: str
    location: str
    image: str | None
    latitude: float | None
    longitude: float | None
    category: str | None
    report_type: ReportType
    status: ItemStatus
    reporter_id: int
    created_at: datetime

    def mark_as_returned(self):
        if self.status != ItemStatus.NOT_RETURNED:
            raise ValueError("Item sudah returned atau statusnya tidak valid.")
        self.status = ItemStatus.RETURNED

    def update_status(self, new_status: ItemStatus):
        if new_status == ItemStatus.RETURNED and self.status != ItemStatus.NOT_RETURNED:
            raise ValueError("Item sudah returned atau statusnya tidak valid.")
        self.status = new_status