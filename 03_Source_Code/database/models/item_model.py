from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
from backend.app.domains.item.entity import ItemStatus, ReportType


class ItemModel(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False) # judul misalnya "Tumbler Tuku"
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType), default=ReportType.LOST, nullable=False
    )
    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.NOT_RETURNED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    #ForeignKey
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
