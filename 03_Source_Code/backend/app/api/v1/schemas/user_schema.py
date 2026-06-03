from pydantic import BaseModel

from backend.app.domains.user.entity import Role


class CreateUserRequest(BaseModel):
    email: str
    fullname: str
    password: str
    phone_number: str
    identity_number: str | None = None
    identity_document: str | None = None


class UserPublicResponse(BaseModel):
    id: int
    fullname: str


class UserResponse(BaseModel):
    id: int
    email: str
    fullname: str
    phone_number: str
    is_active: bool
    role: str
    identity_number: str | None = None
    identity_document: str | None = None


class UpdateUserRequest(BaseModel):
    fullname: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    identity_number: str | None = None
    identity_document: str | None = None


class UserInDB(BaseModel):
    id: int
    email: str
    fullname: str
    phone_number: str
    is_active: bool
    password_hash: str
    identity_number: str | None = None
    identity_document: str | None = None
