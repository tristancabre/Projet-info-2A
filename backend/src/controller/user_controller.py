# controller/user_controller.py
from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from schema.user_model import UpdateAccountRequest, UserModel, UserReadModel, UserResponse
from service.user_service import UserService
from utils.auth import require_admin, require_self_or_admin
from utils.exceptions import DuplicateUserError, InvalidPasswordError
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_user_service() -> UserService:
    """Dependency Injection provider for UserService."""
    return UserService()


# Droits d'accès :
#   POST /                          : public (inscription). Le rôle n'est jamais choisi par le client.
#   GET /, GET /by-username, DELETE : administrateurs uniquement.
#   GET /{id_user}, PUT /{id_user}  : le titulaire du compte, ou un administrateur.
#
# Les routes sont déclarées avec `def` (et non `async def`) car le service et le
# driver de base de données sont synchrones : FastAPI les exécute alors dans un
# pool de threads au lieu de bloquer la boucle d'événements.

# --- Routes "statiques" déclarées AVANT /{id_user} ---


@router.get(
    "/",
    response_model=list[UserResponse],
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)
def find_all_users(user_service: UserService = Depends(get_user_service)):
    """List all users. Administrators only.
    Returns:
        list[UserResponse]: A list of all registered users.
    """
    logger.info("List all users")
    return user_service.list_all()


@router.get(
    "/by-username/{username}",
    response_model=UserResponse,
    tags=["Users"],
    dependencies=[Depends(require_admin)],
)
def user_by_username(username: str, user_service: UserService = Depends(get_user_service)):
    """Find a user by its username. Administrators only.
    Raises:
        HTTPException: 404 error if the user is not found
    """
    logger.info("Find a user by its username")
    user = user_service.find_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"user (username={username}) not found.")
    return user


@router.post("/", response_model=UserReadModel, status_code=201, tags=["Users"])
def create_user(p: UserModel, user_service: UserService = Depends(get_user_service)):
    """Create a new (regular) user. Public: this is the sign-up route.
    The role is never taken from the request: a new account is never an administrator.
    Returns:
        UserReadModel: The newly created user data.
    Raises:
        HTTPException: 400 error if the username is already taken or the password is invalid.
        HTTPException: 500 error if the creation process fails.
    """
    logger.info("Create a user")
    try:
        user = user_service.create(p.username, p.password, p.email)
    except (DuplicateUserError, InvalidPasswordError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not user:
        raise HTTPException(status_code=500, detail="Error while creating user.")
    return user


# --- Routes dynamiques en dernier ---


@router.get(
    "/{id_user}",
    response_model=UserResponse,
    tags=["Users"],
    dependencies=[Depends(require_self_or_admin)],
)
def user_by_id(id_user: int, user_service: UserService = Depends(get_user_service)):
    """Find a user by their unique ID. The account owner or an administrator.
    Raises:
        HTTPException: 404 error if the user is not found
    """
    logger.info("Find a user by id")
    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail=f"user (id={id_user}) not found.")
    return user


@router.put(
    "/{id_user}",
    response_model=UserResponse,
    tags=["Users"],
    dependencies=[Depends(require_self_or_admin)],
)
def update_user(
    id_user: int,
    p: UpdateAccountRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Update a user's information. The account owner or an administrator.
    The password is optional: if it is omitted, the current one is kept.
    The role cannot be changed here.
    Returns:
        UserResponse: The updated user.
    Raises:
        HTTPException: 400 error if the username is already taken or the password is invalid.
        HTTPException: 404 error if the user is not found.
        HTTPException: 500 error if the update process fails.
    """
    logger.info("Update a user")
    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail=f"user (id={id_user}) not found.")

    user.username = p.username
    user.email = p.email

    # The password is never assigned here: the service validates then hashes it.
    try:
        user = user_service.update(user, new_password=p.password)
    except (DuplicateUserError, InvalidPasswordError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not user:
        raise HTTPException(status_code=500, detail="Error while updating user.")
    return user


@router.delete("/{id_user}", tags=["Users"])
def delete_user(
    id_user: int,
    admin: User = Depends(require_admin),
    user_service: UserService = Depends(get_user_service),
):
    """Delete a user. Administrators only.
    An administrator cannot delete their own account: since only administrators can
    delete accounts, there is therefore always at least one administrator left.
    Raises:
        HTTPException: 403 error if an administrator tries to delete their own account.
        HTTPException: 404 error if the user is not found.
        HTTPException: 500 error if the deletion fails.
    """
    logger.info("Delete a user")
    if admin.id_user == id_user:
        raise HTTPException(
            status_code=403,
            detail="An administrator cannot delete their own account.",
        )

    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail=f"user (id={id_user}) not found.")

    if not user_service.delete(user):
        raise HTTPException(status_code=500, detail="Error while deleting user.")
    return {"message": f"user {user.username} deleted"}
