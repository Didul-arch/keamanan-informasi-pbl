from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from digital_signature.auth_router import get_current_user
from backend.app.api.v1.schemas.user_schema import UserResponse, UserPublicResponse
from backend.app.domains.user.entity import UserEntity, Role
from backend.app.domains.user.service import UserService
from database.session import get_db
from backend.app.infrastructure.repositories.user_repository import UserRepository
from backend.app.infrastructure.storage.file_storage import save_upload_file, get_accessible_file_url

router = APIRouter()


def build_user_response(user: UserEntity) -> UserResponse:
    if user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    return UserResponse(
        id=user.id,
        email=user.email,
        fullname=user.fullname,
        phone_number=user.phone_number,
        is_active=user.is_active,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        identity_number=getattr(user, 'identity_number', None),
        identity_document=get_accessible_file_url(getattr(user, 'identity_document', None)),
    )


def build_user_public_response(user: UserEntity) -> UserPublicResponse:
    if user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    return UserPublicResponse(
        id=user.id,
        fullname=user.fullname,
    )


def require_admin(current_user: UserEntity) -> None:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")


def save_identity_document(upload_file: UploadFile) -> str:
    return save_upload_file(upload_file, subdir="identity-documents", default_extension=".pdf")


@router.get("/users/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    require_admin(current_user)
    service = UserService(UserRepository(db))
    users = await service.get_all_users()
    return [build_user_response(user) for user in users]


@router.patch("/users/me", response_model=UserResponse)
async def update_current_user(
    fullname: str | None = Form(None),
    phone_number: str | None = Form(None),
    identity_number: str | None = Form(None),
    identity_document: str | None = Form(None),
    identity_document_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="User id missing")

    service = UserService(UserRepository(db))
    try:
        updated_user = await service.update_own_profile(
            current_user=current_user,
            fullname=fullname,
            phone_number=phone_number,
            identity_number=identity_number,
            identity_document=save_identity_document(identity_document_file) if identity_document_file else identity_document,
        )
    except ValueError as exc:
        if str(exc) == "User tidak ditemukan":
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    return build_user_response(updated_user)


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserEntity = Depends(get_current_user)):
    return build_user_response(current_user)


@router.get("/users/{user_id}", response_model=UserPublicResponse)
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(UserRepository(db))
    try:
        user = await service.get_user_or_raise(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_user_public_response(user)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    fullname: str | None = Form(None),
    phone_number: str | None = Form(None),
    role: Role | None = Form(None),
    is_active: bool | None = Form(None),
    identity_number: str | None = Form(None),
    identity_document: str | None = Form(None),
    identity_document_file: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    require_admin(current_user)
    service = UserService(UserRepository(db))
    try:
        updated_user = await service.update_user_profile(
            user_id=user_id,
            fullname=fullname,
            phone_number=phone_number,
            role=role,
            is_active=is_active,
            identity_number=identity_number,
            identity_document=save_identity_document(identity_document_file) if identity_document_file else identity_document,
        )
    except ValueError as exc:
        if str(exc) == "User tidak ditemukan":
            raise HTTPException(status_code=404, detail=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    return build_user_response(updated_user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    require_admin(current_user)
    service = UserService(UserRepository(db))
    deleted = await service.delete_user(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    return {"message": "User berhasil dihapus"}


@router.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_detail_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
):
    require_admin(current_user)
    service = UserService(UserRepository(db))
    try:
        user = await service.get_user_or_raise(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return build_user_response(user)
