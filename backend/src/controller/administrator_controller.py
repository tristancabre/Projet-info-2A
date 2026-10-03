# controller/admin_controller.py
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from schema.user_schema import ConnectionLogResponse, UpdateAccountRequest, UserResponse

from business_object.user import Administrator
from service.administrator_service import AdministratorService
from utils.auth import require_admin

router = APIRouter()


def get_admin_service(admin: Administrator = Depends(require_admin)) -> AdministratorService:
    """Builds the service for the authenticated administrator."""
    return AdministratorService(admin)


def http_error(e: ValueError) -> HTTPException:
    """Translates a service ValueError into an HTTP error."""
    message = str(e)
    if "not found" in message.lower():
        return HTTPException(status.HTTP_404_NOT_FOUND, detail=message)
    if "already used" in message.lower():
        return HTTPException(status.HTTP_409_CONFLICT, detail=message)
    return HTTPException(status.HTTP_400_BAD_REQUEST, detail=message)


@router.get("/users", response_model=list[UserResponse])
def list_users(service: AdministratorService = Depends(get_admin_service)):
    """Lists every account."""
    return [UserResponse.from_user(u) for u in service.list_all()]


@router.get("/users/{id_user}", response_model=UserResponse)
def get_user(id_user: int, service: AdministratorService = Depends(get_admin_service)):
    user = service.find_by_id(id_user)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.from_user(user)


@router.put("/users/{id_user}", response_model=UserResponse)
def update_user(
    id_user: int,
    request: UpdateAccountRequest,
    service: AdministratorService = Depends(get_admin_service),
):
    """Updates any account. The password is changed only if provided."""
    try:
        user = service.update_account(
            id_user,
            new_username=request.username,
            new_email=request.email,
            new_password=request.password,
        )
    except ValueError as e:
        http_error(e)
    return UserResponse.from_user(user)


@router.delete("/users/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id_user: int, service: AdministratorService = Depends(get_admin_service)):
    """Deletes any account except the admin's own."""
    try:
        service.delete_account(id_user)
    except ValueError as e:
        http_error(e)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/connection-history", response_model=list[ConnectionLogResponse])
def connection_history(
    id_user: int | None = None,
    limit: int = Query(100, gt=0, le=1000),
    service: AdministratorService = Depends(get_admin_service),
):
    """Connection history of everybody, or of one user with ?id_user=."""
    try:
        return service.view_connection_history(id_user, limit)
    except ValueError as e:
        http_error(e)
