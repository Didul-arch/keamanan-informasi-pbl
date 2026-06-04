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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


from fastapi import UploadFile, File, Form
import uuid
import os
from backend.app.infrastructure.config.settings import settings
from digital_signature.encryption import encrypt_string, encrypt_bytes

@router.post("/users/", response_model=dict)
async def create_user(
	email: str = Form(...),
	fullname: str = Form(...),
	password: str = Form(...),
	phone_number: str = Form(...),
	identity_number: str | None = Form(None),
	identity_document: UploadFile | None = File(None),
	db: AsyncSession = Depends(get_db)
):
	repo = UserRepository(db)
	service = UserService(repo)

	doc_path = None
	if identity_document:
		file_bytes = await identity_document.read()
		encrypted_bytes = encrypt_bytes(file_bytes)
		
		os.makedirs(settings.IDENTITY_DOCUMENT_UPLOAD_DIR, exist_ok=True)
		ext = os.path.splitext(identity_document.filename)[1] if identity_document.filename else ".jpg"
		unique_name = f"{uuid.uuid4().hex}{ext}.enc"
		file_path = os.path.join(settings.IDENTITY_DOCUMENT_UPLOAD_DIR, unique_name)
		
		with open(file_path, "wb") as f:
			f.write(encrypted_bytes)
			
		doc_path = unique_name

	enc_identity_number = encrypt_string(identity_number)

	user_data = UserEntity(
		email=email,
		fullname=fullname,
		phone_number=phone_number,
		identity_number=enc_identity_number,
		identity_document=doc_path,
		password_hashed=auth_utils.get_password_hash(password),
		is_active=True,
	)
	try:
		created_user = await service.register(user_data)
	except DuplicateUserError as e:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
	return {"message": "User Berhasil Dibuat", "data": {"id": created_user.id, "email": created_user.email}}


from fastapi import Request
from backend.app.infrastructure.config.limiter import limiter
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
	refresh_token: str

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
	repo = UserRepository(db)
	db_user = await repo.get_auth_by_email(form_data.username)
	if not db_user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
	if not auth_utils.verify_password(form_data.password, db_user.password_hash):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

	access_token_expires = timedelta(minutes=60)
	access_token = auth_utils.create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
	refresh_token = auth_utils.create_refresh_token(data={"sub": db_user.email})
	
	request.state.user_id = db_user.id
	
	return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/token/refresh", response_model=Token)
async def refresh_access_token(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
	try:
		token_payload = auth_utils.decode_token(payload.refresh_token)
		if token_payload.get("type") != "refresh":
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
		username = token_payload.get("sub")
		if not username:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
	except Exception:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
	
	repo = UserRepository(db)
	user = await repo.get_by_email(username)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
		
	access_token_expires = timedelta(minutes=60)
	access_token = auth_utils.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
	new_refresh_token = auth_utils.create_refresh_token(data={"sub": user.email})
	
	return Token(access_token=access_token, refresh_token=new_refresh_token)


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
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
	
	request.state.user_id = user.id
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
