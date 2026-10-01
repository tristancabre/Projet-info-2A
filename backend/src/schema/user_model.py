# schema/user_schema.py
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from business_object.user import User

MIN_PASSWORD_LENGTH = 10


def _check_password_length(v: str) -> str:
    if len(v) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")
    return v


class UserModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange user information,
    ensuring data consistency and validation during API requests and responses."""

    username: str
    password: str
    email: EmailStr

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str) -> str:
        return _check_password_length(v)


class UserLoginModel(BaseModel):
    username: str
    password: str


class UserReadModel(BaseModel):
    """Public view of a user. Never exposes the password hash."""

    username: str
    email: EmailStr


class UserResponse(UserReadModel):
    """User as returned by the admin endpoints."""

    id_user: int
    is_admin: bool

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id_user=user.id_user,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
        )


class UpdateAccountRequest(BaseModel):
    """Body of PUT /admin/users/{id_user}. Password is optional (None = unchanged)."""

    username: str
    email: EmailStr
    password: str | None = None

    @field_validator("password")
    @classmethod
    def check_password_length(cls, v: str | None) -> str | None:
        return v if v is None else _check_password_length(v)


class ConnectionLogResponse(BaseModel):
    id_connection: int
    id_user: int
    username: str
    connection_moment: datetime | None