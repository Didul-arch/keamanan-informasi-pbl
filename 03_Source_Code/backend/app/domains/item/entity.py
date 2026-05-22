from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ItemStatus(str, Enum):
    LOST = "lost"
    FOUND = "found"
    CLAIMED = "claimed"


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

    #contoh untuk ubah status dari found -> claimed
    def mark_as_claimed(self):
        if self.status != ItemStatus.FOUND:
            raise ValueError("Item belum ditemukan!")
        self.status = ItemStatus.CLAIMED
