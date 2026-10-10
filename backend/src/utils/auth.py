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

# auto_error=False : c'est nous qui levons le 401. Selon la version de FastAPI, un en-tête
# absent donne sinon un 403 (ancien comportement) ou un 401.
bearer = HTTPBearer(auto_error=False)
user_service = UserService()


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


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
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> int:
    """Extracts the user id from the token (authentication only)."""
    if credentials is None:
        raise _unauthorized("Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials,
            _secret_key(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        # `raise` était absent : l'exception était créée puis ignorée, et la fonction
        # renvoyait None au lieu de rejeter un token invalide.
        raise _unauthorized("Invalid or expired token")


def get_current_user(id_user: int = Depends(get_current_user_id)) -> User:
    """Reloads the user from the database on every request."""
    user = user_service.find_by_id(id_user)
    if user is None:
        raise _unauthorized("User no longer exists")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Authorization: only administrators pass."""
    if not isinstance(user, Administrator):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrator rights required")
    return user


def require_self_or_admin(id_user: int, user: User = Depends(get_current_user)) -> User:
    """Authorization: the owner of the account (path parameter `id_user`) or an administrator."""
    if user.id_user != id_user and not isinstance(user, Administrator):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only access your own account")
    return user
