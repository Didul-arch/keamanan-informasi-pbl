from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RequestType(str, Enum):
    CLAIM = "claim"
    FOUND = "found"
   
@dataclass
class ClaimEntity:
    id: int | None
    request_type: RequestType
    proof_text: str
    proof_image: str | None
    status: ClaimStatus
    claimer_id: int
    item_id: int
    reviewer_id: int | None # id reviewer
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    def approve(self, reviewer_id: int):
        if self.status != ClaimStatus.PENDING:
            raise ValueError("Claim yang sudah diproses tidak bisa diubah lagi.")
        self.status = ClaimStatus.APPROVED
        self.reviewer_id = reviewer_id
        self.updated_at = datetime.now()

    def reject(self, reviewer_id: int):
        if self.status != ClaimStatus.PENDING:
            raise ValueError("Claim yang sudah diproses tidak bisa diubah lagi.")
        self.status = ClaimStatus.REJECTED
        self.reviewer_id = reviewer_id
        self.updated_at = datetime.now()