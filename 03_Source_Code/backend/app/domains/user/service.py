from backend.app.domains.user.entity import UserEntity
from backend.app.infrastructure.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: int) -> UserEntity | None:
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> UserEntity | None:
        return await self.user_repo.get_by_email(email)

    async def get_all_users(self) -> list[UserEntity]:
        return await self.user_repo.get_all()

    async def create_user(self, user: UserEntity) -> UserEntity:
        if len(user.fullname.strip()) < 3:
            raise ValueError("Nama user minimal 3 karakter.")
        if "@" not in user.email:
            raise ValueError("Format email tidak valid.")
        if not user.password_hashed.strip():
            raise ValueError("Password wajib diisi.")

        return await self.user_repo.create(user)
