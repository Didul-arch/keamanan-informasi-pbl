from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ClaimStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
   
@dataclass
class ClaimEntity:
    id: int | None
    proof_text: str
    proof_image: str | None
    status: ClaimStatus
    claimer_id: int
    item_id: int
    reviewer_id: int | None # id reviewer
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    def update_status(self, new_status: ClaimStatus, reviewer_id: int):
        if self.status != ClaimStatus.PENDING:
            raise ValueError("Claim yang sudah diproses tidak bisa diubah lagi.")

        if new_status not in {ClaimStatus.APPROVED, ClaimStatus.REJECTED}:
            raise ValueError("Status claim hanya boleh diubah ke approved atau rejected.")

        self.status = new_status
        self.reviewer_id = reviewer_id
        self.updated_at = datetime.now()