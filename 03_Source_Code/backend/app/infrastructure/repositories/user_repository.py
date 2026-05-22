from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.domains.user.entity import Role, UserEntity
from database.models.user_model import UserModel

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_entity(self, db_user: UserModel) -> UserEntity:
        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            fullname=db_user.full_name,
            password_hashed=db_user.password_hash,
            role=db_user.role,
            is_active=db_user.is_active,
        )

    async def get_by_id(self, user_id: int) -> UserEntity | None:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.db.execute(query)
        db_user = result.scalars().first()

        if not db_user:
            return None

        return self._to_entity(db_user)

    async def get_by_email(self, email: str) -> UserEntity | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        db_user = result.scalars().first()

        if not db_user:
            return None

        return self._to_entity(db_user)

    async def get_all(self) -> list[UserEntity]:
        query = select(UserModel).order_by(UserModel.id.asc())
        result = await self.db.execute(query)
        db_users = result.scalars().all()
        return [self._to_entity(db_user) for db_user in db_users]

    async def create(self, user: UserEntity) -> UserEntity:
        if not user.password_hashed.strip():
            raise ValueError("password_hash tidak boleh kosong.")

        new_user = UserModel(
            email=user.email,
            full_name=user.fullname,
            is_active=user.is_active,
            password_hash=user.password_hashed,
            role=user.role or Role.UMUM,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return self._to_entity(new_user)

    async def get_auth_by_email(self, email: str):
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
