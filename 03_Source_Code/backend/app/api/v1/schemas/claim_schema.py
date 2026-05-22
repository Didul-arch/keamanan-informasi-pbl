from pydantic import BaseModel

from backend.app.domains.claim.entity import ClaimStatus


class CreateClaimRequest(BaseModel):
    proof_text: str
    proof_image: str | None = None
    item_id: int


class ReviewClaimRequest(BaseModel):
    status: ClaimStatus