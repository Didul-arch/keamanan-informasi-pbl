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
    password_hashed: str
    id: int | None = None
    role: Role = Role.UMUM
    is_active: bool = True

    def is_ipb_student(self) -> bool:
        return self.email.endswith("@apps.ipb.ac.id")

    def can_report_item(self) -> bool:
        return self.is_active
