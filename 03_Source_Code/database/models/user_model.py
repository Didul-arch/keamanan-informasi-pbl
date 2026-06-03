from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.domains.user.entity import Role
from database.session import Base

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    identity_number: Mapped[str | None] = mapped_column(String, nullable=True)
    identity_document: Mapped[str | None] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.UMUM)

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": Role.UMUM,
    }


class AdminModel(UserModel):
    __mapper_args__ = {
        "polymorphic_identity": Role.ADMIN,
    }


class CivitasModel(UserModel):
    __mapper_args__ = {
        "polymorphic_identity": Role.CIVITAS,
    }
