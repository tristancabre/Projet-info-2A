from fastapi import APIRouter, HTTPException, status

from schema.login_model import ConnectionRequest, ConnectionResponse
from service.user_service import UserService
from utils.auth import create_token
from utils.exceptions import InvalidCredentialsError

router = APIRouter()

user_service = UserService()


@router.post("", response_model=ConnectionResponse)
def login(request: ConnectionRequest):
    """Checks the credentials and returns the user's information with a token."""
    try:
        user = user_service.login(request.username, request.password)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return ConnectionResponse(
        id_user=user.id_user,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        access_token=create_token(user.id_user),
    )
