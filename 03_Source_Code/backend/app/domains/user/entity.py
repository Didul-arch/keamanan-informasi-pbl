from dataclasses import dataclass
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    CIVITAS = "civitas"
    UMUM = "umum"

@dataclass
class UserEntity:
    email: str
    fullname: str
    phone_number: str
    identity_number: str | None
    identity_document: str | None
    password_hashed: str
    id: int | None = None
    role: Role = Role.UMUM
    is_active: bool = True

    def is_ipb_student(self) -> bool:
        return self.email.endswith("@apps.ipb.ac.id")

    def can_report_item(self) -> bool:
        return self.is_active

    def can_submit_claim(self) -> bool:
        return self.is_active

    def can_mark_item_returned(self) -> bool:
        return self.is_active


@dataclass
class AdminEntity(UserEntity):
    role: Role = Role.ADMIN

    def can_review_claim(self) -> bool:
        return self.is_active and self.role == Role.ADMIN

    def can_manage_users(self) -> bool:
        return self.is_active and self.role == Role.ADMIN