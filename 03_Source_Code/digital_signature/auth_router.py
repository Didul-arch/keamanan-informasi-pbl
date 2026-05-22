from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.schemas.auth_schema import Token
from backend.app.api.v1.schemas.user_schema import CreateUserRequest, UserResponse
from backend.app.domains.user.entity import Role, UserEntity
from backend.app.domains.user.service import UserService
from backend.app.infrastructure.repositories.user_repository import UserRepository
from database.session import get_db

from digital_signature import utils as auth_utils

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post("/users/", response_model=dict)
async def create_user(payload: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    service = UserService(repo)

    resolved_role = Role.UMUM
    if payload.email.strip().lower().endswith(("@apps.ipb.ac.id", "@ipb.ac.id")):
        resolved_role = Role.CIVITAS

    user_data = UserEntity(
        email=payload.email,
        fullname=payload.fullname,
        password_hashed=auth_utils.get_password_hash(payload.password),
        role=resolved_role,
        is_active=True,
    )
    created_user = await service.create_user(user_data)
    return {"message": "User Berhasil Dibuat", "data": {"id": created_user.id, "email": created_user.email}}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    db_user = await repo.get_auth_by_email(form_data.username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not auth_utils.verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=60)
    access_token = auth_utils.create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = auth_utils.decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    repo = UserRepository(db)
    user = await repo.get_by_email(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserEntity = Depends(get_current_user)):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        fullname=current_user.fullname,
        is_active=current_user.is_active,
        role=current_user.role,
    )
