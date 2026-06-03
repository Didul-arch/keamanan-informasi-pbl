from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.domains.claim.entity import ClaimEntity, ClaimStatus, RequestType
from sqlalchemy import select
from datetime import date, datetime, time, timedelta
from database.models.claim_model import ClaimModel
from backend.app.infrastructure.storage.file_storage import get_accessible_file_url

class ClaimRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_entity(self, claim: ClaimModel) -> ClaimEntity:
        return ClaimEntity(
            id=claim.id,
            request_type=claim.request_type,
            proof_text=claim.proof_text,
            proof_image=get_accessible_file_url(claim.proof_image),
            status=claim.status,
            claimer_id=claim.claimer_id,
            item_id=claim.item_id,
            reviewer_id=claim.reviewer_id,
            reviewed_at=claim.reviewed_at,
            created_at=claim.created_at,
            updated_at=claim.updated_at
        )

    # 1. Save new claim
    async def save(self, claim: ClaimEntity) -> ClaimEntity:
        db_claim = ClaimModel(
            request_type=claim.request_type,
            proof_text=claim.proof_text,
            proof_image=claim.proof_image,
            status=claim.status,
            claimer_id=claim.claimer_id,
            item_id=claim.item_id,
            reviewer_id=claim.reviewer_id,
            reviewed_at=claim.reviewed_at,
            created_at=claim.created_at,
            updated_at=claim.updated_at
        )
        self.db.add(db_claim)
        await self.db.commit()
        await self.db.refresh(db_claim)

        return self._to_entity(db_claim)

    # 2. Cari Semua Klaim 
    async def get_all(self, limit: int = 20) -> list[ClaimEntity]:
        query = select(ClaimModel).order_by(ClaimModel.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        db_claims = result.scalars().all()

        # Balikin dalam bentuk list of Entities (Mapping massal)
        return [self._to_entity(claim) for claim in db_claims]

    # 3. Cari Klaim Berdasarkan ID 
    async def get_by_id(self, claim_id: int) -> ClaimEntity | None:
        result = await self.db.execute(select(ClaimModel).where(ClaimModel.id == claim_id))
        claim = result.scalars().first()
        
        if not claim: return None
        
        return self._to_entity(claim)

    # 4. Cari Klaim dengan filter opsional
    async def get_filtered_claims(
        self,
        claim_date: date | None = None,
        reviewer_id: int | None = None,
        claimer_id: int | None = None,
        status: ClaimStatus | None = None,
    ) -> list[ClaimEntity]:
        query = select(ClaimModel)

        if claim_date is not None:
            start_of_day = datetime.combine(claim_date, time.min)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.where(
                (ClaimModel.created_at >= start_of_day) & (ClaimModel.created_at < end_of_day)
            )

        if reviewer_id is not None:
            query = query.where(ClaimModel.reviewer_id == reviewer_id)

        if claimer_id is not None:
            query = query.where(ClaimModel.claimer_id == claimer_id)

        if status is not None:
            query = query.where(ClaimModel.status == status)

        query = query.order_by(ClaimModel.created_at.desc())
        result = await self.db.execute(query)
        db_claims = result.scalars().all()
        return [self._to_entity(claim) for claim in db_claims]

    # 5. Update status claim
    async def update_status(self, claim_id: int, claim: ClaimEntity) -> ClaimEntity | None:
        db_claim = await self.get_by_id(claim_id)
        if not db_claim:
            return None

        result = await self.db.execute(select(ClaimModel).where(ClaimModel.id == claim_id))
        db_claim_model = result.scalars().first()

        db_claim_model.status = claim.status
        db_claim_model.reviewer_id = claim.reviewer_id
        db_claim_model.updated_at = datetime.now()
        if claim.status != ClaimStatus.PENDING:
            db_claim_model.reviewed_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(db_claim_model)
        return self._to_entity(db_claim_model)