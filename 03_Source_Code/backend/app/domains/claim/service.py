from datetime import date

from backend.app.domains.claim.entity import ClaimEntity, ClaimStatus
from backend.app.infrastructure.repositories.claim_repository import ClaimRepository


class ClaimService:
    def __init__(self, claim_repo: ClaimRepository):
        self.claim_repo = claim_repo

    async def submit_claim(self, claim: ClaimEntity) -> ClaimEntity:
        if len(claim.proof_text.strip()) < 5:
            raise ValueError("Bukti klaim minimal 5 karakter.")
        if not claim.proof_image:
            raise ValueError("Bukti gambar klaim wajib diunggah.")

        return await self.claim_repo.save(claim)

    async def get_by_id(self, claim_id: int) -> ClaimEntity | None:
        return await self.claim_repo.get_by_id(claim_id)

    async def get_all(
        self,
        claim_date: date | None = None,
        reviewer_id: int | None = None,
        claimer_id: int | None = None,
        status: ClaimStatus | None = None,
        limit: int = 20,
    ) -> list[ClaimEntity]:
        if claim_date is None and reviewer_id is None and claimer_id is None and status is None:
            return await self.claim_repo.get_all(limit=limit)

        return await self.claim_repo.get_filtered_claims(
            claim_date=claim_date,
            reviewer_id=reviewer_id,
            claimer_id=claimer_id,
            status=status,
        )

    async def review_claim(self, claim_id: int, new_status, reviewer_id: int):
        claim = await self.claim_repo.get_by_id(claim_id)
        if not claim:
            return None
        if new_status == ClaimStatus.APPROVED:
            claim.approve(reviewer_id)
        else:
            claim.reject(reviewer_id)
        return await self.claim_repo.update_status(claim_id, claim)