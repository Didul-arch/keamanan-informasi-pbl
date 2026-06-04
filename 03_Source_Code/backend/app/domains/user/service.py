from backend.app.domains.user.entity import UserEntity, Role
from backend.app.infrastructure.repositories.user_repository import UserRepository


class DuplicateUserError(ValueError):
    pass


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, user: UserEntity) -> UserEntity:
        if len(user.fullname.strip()) < 3:
            raise ValueError("Nama user minimal 3 karakter.")
        if "@" not in user.email:
            raise ValueError("Format email tidak valid.")
        if not user.password_hashed.strip():
            raise ValueError("Password wajib diisi.")
        if not (user.phone_number or "").strip():
            raise ValueError("Nomor telepon wajib diisi.")

        existing_user = await self.user_repo.get_by_email(user.email)
        if existing_user:
            raise DuplicateUserError("Email sudah terdaftar.")

        if user.is_ipb_student():
            user.role = Role.CIVITAS
        else:
            user.role = Role.UMUM

        user.phone_number = user.phone_number.strip()
        if user.identity_number is not None:
            user.identity_number = user.identity_number.strip() or None
        if user.identity_document is not None:
            user.identity_document = user.identity_document.strip() or None

        self._ensure_identity(user.identity_number, user.identity_document)

        return await self.user_repo.create(user)

    async def edit_profile(
        self,
        current_user: UserEntity,
        fullname: str | None = None,
        phone_number: str | None = None,
        identity_number: str | None = None,
        identity_document: str | None = None,
    ) -> UserEntity:
        if current_user.id is None:
            raise ValueError("User id missing.")
        return await self.update_user_profile(
            user_id=current_user.id,
            fullname=fullname,
            phone_number=phone_number,
            identity_number=identity_number,
            identity_document=identity_document,
        )

    async def view_history(self, user_id: int, activity_history_repo):
        user = await self.get_user_or_raise(user_id)
        if not user.is_active:
            raise ValueError("User tidak aktif.")
        return await activity_history_repo.get_by_user_id(user_id)

    async def view_notifications(self, user_id: int, notification_repo):
        user = await self.get_user_or_raise(user_id)
        if not user.is_active:
            raise ValueError("User tidak aktif.")
        return await notification_repo.get_for_user(user_id)

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        return await self.user_repo.get_by_email(email)

    async def get_all_users(self) -> list[UserEntity]:
        return await self.user_repo.get_all()

    async def get_user_or_raise(self, user_id: int) -> UserEntity:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User tidak ditemukan")
        return user

    async def delete_user(self, user_id: int) -> bool:
        return await self.user_repo.delete(user_id)

    async def update_user_profile(
        self,
        user_id: int,
        fullname: str | None = None,
        phone_number: str | None = None,
        role: Role | None = None,
        is_active: bool | None = None,
        identity_number: str | None = None,
        identity_document: str | None = None,
    ) -> UserEntity:
        current_user = await self.get_user_or_raise(user_id)
        if fullname is None or not fullname.strip():
            raise ValueError("Nama user wajib diisi")

        target_role = role or current_user.role
        resolved_identity_document = self._normalize_identity_document(identity_document)

        if target_role == Role.CIVITAS:
            has_identity = any([
                (identity_number or current_user.identity_number or "").strip(),
                (resolved_identity_document or current_user.identity_document or "").strip(),
            ])
            if not has_identity:
                raise ValueError("Civitas users must provide either identity_number or identity_document")

        from digital_signature.encryption import encrypt_string
        if identity_number is not None:
            identity_number = encrypt_string(identity_number.strip() or None)

        updated_user = await self.user_repo.update(
            user_id,
            fullname=fullname,
            phone_number=phone_number,
            role=role,
            is_active=is_active,
            identity_number=identity_number,
            identity_document=resolved_identity_document,
        )

        if not updated_user:
            raise ValueError("User tidak ditemukan")

        return updated_user

    # --- update_own_profile tetap ada sebagai alias internal ---
    async def update_own_profile(
        self,
        current_user: UserEntity,
        fullname: str | None = None,
        phone_number: str | None = None,
        identity_number: str | None = None,
        identity_document: str | None = None,
    ) -> UserEntity:
        if current_user.id is None:
            raise ValueError("User id missing")
        return await self.update_user_profile(
            user_id=current_user.id,
            fullname=fullname,
            phone_number=phone_number,
            identity_number=identity_number,
            identity_document=identity_document,
        )

    def _normalize_identity_document(self, identity_document: str | None) -> str | None:
        if identity_document is None:
            return None
        cleaned = identity_document.strip()
        return cleaned or None

    def _ensure_identity(
        self,
        identity_number: str | None,
        identity_document: str | None,
    ) -> None:
        has_identity = any([
            (identity_number or "").strip(),
            (identity_document or "").strip(),
        ])
        if not has_identity:
            raise ValueError("User harus mengisi identity_number atau identity_document")