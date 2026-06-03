from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.domains.claim.entity import RequestType
from database.session import Base


class ActivityHistoryKind(str, Enum):
    REPORT = "report"
    REQUEST = "request"


class ActivityHistoryModel(Base):
    __tablename__ = "activity_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    claim_id: Mapped[int | None] = mapped_column(ForeignKey("claim.id"), nullable=True)
    history_type: Mapped[ActivityHistoryKind] = mapped_column(
        SQLEnum(ActivityHistoryKind), nullable=False
    )
    request_type: Mapped[RequestType | None] = mapped_column(
        SQLEnum(RequestType), nullable=True
    )
    item_status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    report_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
