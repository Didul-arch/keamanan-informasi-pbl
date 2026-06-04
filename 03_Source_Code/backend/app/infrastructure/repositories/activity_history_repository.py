from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domains.claim.entity import ClaimEntity, RequestType
from backend.app.domains.item.entity import ItemEntity, ItemStatus
from database.models.activity_history_model import (
    ActivityHistoryKind,
    ActivityHistoryModel,
)
from backend.app.infrastructure.storage.file_storage import get_accessible_file_url, get_storage_reference


class ActivityHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_payload(self, history: ActivityHistoryModel) -> dict:
        return {
            "id": history.id,
            "kind": history.history_type.value if hasattr(history.history_type, "value") else str(history.history_type),
            "request_type": history.request_type.value if history.request_type and hasattr(history.request_type, "value") else (str(history.request_type) if history.request_type else None),
            "item_id": history.item_id,
            "claim_id": history.claim_id,
            "title": history.title,
            "description": history.description,
            "location": history.location,
            "category": history.category,
            "image": get_accessible_file_url(history.image),
            "report_type": history.report_type,
            "item_status": history.item_status,
            "request_status": history.request_status,
            "created_at": history.created_at.isoformat() if history.created_at else None,
            "updated_at": history.updated_at.isoformat() if history.updated_at else None,
            "completed_at": history.completed_at.isoformat() if history.completed_at else None,
            "can_mark_returned": (
                (history.history_type == ActivityHistoryKind.REQUEST and history.request_type == "claim" and history.request_status == "approved" and history.item_status == ItemStatus.NOT_RETURNED.value)
                or
                (history.history_type == ActivityHistoryKind.REPORT and history.report_type == "lost" and history.item_status == ItemStatus.NOT_RETURNED.value)
            ),
        }

    async def create_report_entry(self, user_id: int, item: ItemEntity) -> ActivityHistoryModel:
        history = ActivityHistoryModel(
            user_id=user_id,
            item_id=item.id,
            claim_id=None,
            history_type=ActivityHistoryKind.REPORT,
            request_type=None,
            item_status=item.status.value if hasattr(item.status, "value") else str(item.status),
            request_status=None,
            report_type=item.report_type.value if hasattr(item.report_type, "value") else str(item.report_type),
            title=item.title,
            description=item.description,
            location=item.location,
            category=item.category,
            image=get_storage_reference(item.image),
            created_at=item.created_at,
            updated_at=None,
            completed_at=None,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def create_request_entry(self, user_id: int, claim: ClaimEntity, item: ItemEntity) -> ActivityHistoryModel:
        history = ActivityHistoryModel(
            user_id=user_id,
            item_id=item.id,
            claim_id=claim.id,
            history_type=ActivityHistoryKind.REQUEST,
            request_type=claim.request_type,
            item_status=item.status.value if hasattr(item.status, "value") else str(item.status),
            request_status=claim.status.value if hasattr(claim.status, "value") else str(claim.status),
            report_type=item.report_type.value if hasattr(item.report_type, "value") else str(item.report_type),
            title=item.title,
            description=item.description,
            location=item.location,
            category=item.category,
            image=get_storage_reference(item.image),
            created_at=claim.created_at,
            updated_at=claim.updated_at,
            completed_at=claim.reviewed_at,
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_for_user(self, user_id: int) -> list[dict]:
        result = await self.db.execute(
            select(ActivityHistoryModel)
            .where(ActivityHistoryModel.user_id == user_id)
            .order_by(ActivityHistoryModel.created_at.desc())
        )
        histories = result.scalars().all()
        return [self._to_payload(history) for history in histories]

    async def update_request_status_by_claim_id(self, claim_id: int, status: str) -> None:
        result = await self.db.execute(
            select(ActivityHistoryModel).where(ActivityHistoryModel.claim_id == claim_id)
        )
        history = result.scalars().first()
        if not history:
            return

        history.request_status = status
        history.updated_at = datetime.now()
        if status in {"approved", "rejected", ItemStatus.RETURNED.value}:
            history.completed_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(history)

    async def mark_user_item_returned(self, user_id: int, item_id: int) -> list[dict]:
        result = await self.db.execute(
            select(ActivityHistoryModel)
            .where(ActivityHistoryModel.user_id == user_id)
            .where(ActivityHistoryModel.item_id == item_id)
        )
        histories = result.scalars().all()
        if not histories:
            return []

        now = datetime.now()
        for history in histories:
            history.item_status = ItemStatus.RETURNED.value
            history.updated_at = now
            history.completed_at = now

        await self.db.commit()
        for history in histories:
            await self.db.refresh(history)

        return [self._to_payload(history) for history in histories]
