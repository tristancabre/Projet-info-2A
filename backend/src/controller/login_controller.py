# controller/login_controller.py
from fastapi import APIRouter, HTTPException, status
from utils.utils_auth import create_token

from business_object.user import Administrator
from dao.user_dao import UserDao
from schema.login_model import ConnectionRequest, ConnectionResponse
from service.user_service import UserService

router = APIRouter()

user_service = UserService(UserDao())


@router.post("", response_model=ConnectionResponse)
def login(request: ConnectionRequest):
    """Checks the credentials and returns the user's information with a token."""
    try:
        user = user_service.login(request.username, request.password)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return ConnectionResponse(
        id_user=user.id_user,
        username=user.username,
        email=user.email,
        is_admin=isinstance(user, Administrator),
        access_token=create_token(user.id_user),
    )
