from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.schemas.user_schema import CreateUserRequest, UserResponse
from digital_signature.auth_schema import Token
from backend.app.domains.user.entity import UserEntity
from backend.app.domains.user.service import UserService, DuplicateUserError
from database.session import get_db
from backend.app.infrastructure.repositories.user_repository import UserRepository
from digital_signature import utils as auth_utils

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post("/users/", response_model=dict)
async def create_user(payload: CreateUserRequest, db: AsyncSession = Depends(get_db)):
	repo = UserRepository(db)
	service = UserService(repo)

	user_data = UserEntity(
		email=payload.email,
		fullname=payload.fullname,
		phone_number=payload.phone_number,
		identity_number=payload.identity_number,
		identity_document=payload.identity_document,
		password_hashed=auth_utils.get_password_hash(payload.password),
		is_active=True,
	)
	try:
		created_user = await service.register(user_data)
	except DuplicateUserError as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
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
		phone_number=current_user.phone_number,
		is_active=current_user.is_active,
		role=current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role),
		identity_number=current_user.identity_number,
		identity_document=current_user.identity_document,
	)
