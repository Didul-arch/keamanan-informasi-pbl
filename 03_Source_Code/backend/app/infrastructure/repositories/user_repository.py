from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database.models.user_model import UserModel
from backend.app.domains.user.entity import UserEntity, Role

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_entity(self, db_user: UserModel) -> UserEntity:
        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            phone_number=db_user.phone_number,
            identity_number=db_user.identity_number,
            identity_document=db_user.identity_document,
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

    async def update(
        self,
        user_id: int,
        fullname: str | None = None,
        role: Role | None = None,
        is_active: bool | None = None,
        phone_number: str | None = None,
        identity_number: str | None = None,
        identity_document: str | None = None,
    ) -> UserEntity | None:
        db_user = await self.db.get(UserModel, user_id)

        if not db_user:
            return None

        if fullname is not None:
            db_user.full_name = fullname
        if role is not None:
            db_user.role = role
        if is_active is not None:
            db_user.is_active = is_active
        if phone_number is not None:
            db_user.phone_number = phone_number
        if identity_number is not None:
            db_user.identity_number = identity_number
        if identity_document is not None:
            db_user.identity_document = identity_document

        try:
            await self.db.commit()
            await self.db.refresh(db_user)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Gagal memperbarui user.")

        return self._to_entity(db_user)

    async def delete(self, user_id: int) -> bool:
        db_user = await self.db.get(UserModel, user_id)

        if not db_user:
            return False

        await self.db.delete(db_user)
        await self.db.commit()
        return True

    async def create(self, user: UserEntity) -> UserEntity:
        if not user.password_hashed.strip():
            raise ValueError("password_hash tidak boleh kosong.")

        new_user = UserModel(
            email=user.email,
            full_name=user.fullname,
            phone_number=user.phone_number,
            identity_number=user.identity_number,
            identity_document=user.identity_document,
            is_active=user.is_active,
            password_hash=user.password_hashed,
            role=user.role or Role.UMUM,
        )
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Email sudah terdaftar.")

        return self._to_entity(new_user)

    async def get_auth_by_email(self, email: str):
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()
