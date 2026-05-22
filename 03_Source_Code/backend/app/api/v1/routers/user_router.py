from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from digital_signature.auth_router import get_current_user
from backend.app.api.v1.schemas.user_schema import UserResponse
from backend.app.domains.user.entity import UserEntity
from backend.app.domains.user.service import UserService
from backend.app.infrastructure.repositories.user_repository import UserRepository
from database.session import get_db

router = APIRouter()


def to_user_response(user: UserEntity) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        fullname=user.fullname,
        is_active=user.is_active,
    )


@router.get("/users/", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    service = UserService(repo)
    users = await service.get_all_users()
    return [to_user_response(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    service = UserService(repo)
    user = await service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    return to_user_response(user)


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserEntity = Depends(get_current_user)):
    return to_user_response(current_user)
