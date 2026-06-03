
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from database.session import Base
from backend.app.domains.claim.entity import ClaimStatus, RequestType


class ClaimModel(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_type: Mapped[RequestType] = mapped_column(Enum(RequestType), nullable=False, default=RequestType.CLAIM)
    proof_text: Mapped[str] = mapped_column(Text, nullable=False)
    proof_image: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus), nullable=False, default=ClaimStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    #ForeignKey
    claimer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
