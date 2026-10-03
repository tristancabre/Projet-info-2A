# utils/auth.py
import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from business_object.user import Administrator, User
from service.user_service import UserService

ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

bearer = HTTPBearer()
user_service = UserService()


def _secret_key() -> str:
    """Read lazily: the .env is loaded in main.py AFTER the controllers are imported."""
    key = os.getenv("JWT_SECRET")
    if not key:
        raise RuntimeError("JWT_SECRET is not defined in the environment")
    return key


def create_token(id_user: int) -> str:
    payload = {
        "sub": str(id_user),
        "exp": datetime.now(UTC) + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> int:
    """Extracts the user id from the token (authentication only)."""
    try:
        payload = jwt.decode(credentials.credentials, _secret_key(), algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")


def get_current_user(id_user: int = Depends(get_current_user_id)) -> User:
    """Reloads the user from the database on every request."""
    user = user_service.find_by_id(id_user)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Authorization: only administrators pass."""
    if not isinstance(user, Administrator):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrator rights required")
    return user
