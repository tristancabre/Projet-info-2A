# controller/user_controller.py


from fastapi import APIRouter, Depends, HTTPException

from schema.user_model import UserModel, UserReadModel
from service.user_service import UserService
from utils.log_utils import get_logger

router = APIRouter()

logger = get_logger(__name__)


def get_user_service():
    """Dependency Injection provider for UserService."""
    return UserService()


@router.get("/", response_model=list[UserReadModel], tags=["Users"])
async def find_all_users(user_service=Depends(get_user_service)):
    """List all users.
    Returns:
        list[UserReadModel]: A list of all registered users.
    """
    logger.info("List all users")
    users_list = user_service.find_all()
    return users_list


@router.get("/{id_user}", response_model=UserReadModel, tags=["Users"])
async def user_by_id(id_user: int, user_service=Depends(get_user_service)):
    """Find a user by their unique ID.
    Args:
        id_user (int)
        user_service (UserService): The service used to interact with user data
    Returns:
        UserReadModel: The user data if found
    Raises:
        HTTPException: 404 error if the user is not found
    """
    logger.info("Find a user by id")
    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail="user (id={id_user}) not found.")
    return user


@router.post("/", response_model=UserReadModel, tags=["users"])
async def create_user(p: UserModel, user_service=Depends(get_user_service)):
    """Create a new user.
    Args:
        p (UserModel): The user data to create.
        user_service (UserService): The service used to interact with user data.
    Returns:
        UserReadModel: The newly created user data.
    Raises:
        HTTPException: 400 error if the username is already taken.
        HTTPException: 500 error if the creation process fails.
    """
    logger.info("Create a user")
    if user_service.username_already_used(p.username):
        raise HTTPException(status_code=400, detail="Username already used.")

    user = user_service.create(p.username, p.password, p.email)
    if not user:
        raise HTTPException(status_code=500, detail="Error while creating user.")

    return user


@router.put("/{id_user}", response_model=UserReadModel, tags=["users"])
async def update_user(id_user: int, p: UserModel, user_service=Depends(get_user_service)):
    """Update an existing user's information.
    Args:
        id_user (int)
        p (UserModel): The new data for the user.
        user_service (UserService): The service used to interact with user data.
    Returns:
        str: A confirmation message indicating the user was updated.
    Raises:
        HTTPException: 404 error if the user is not found.
        HTTPException: 500 error if the update process fails.
    """
    logger.info("Update a user")
    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail="user (id={id_user}) not found.")

    user.username = p.username
    user.password = p.password
    user.email = p.email

    user = user_service.update(user)
    if not user:
        raise HTTPException(status_code=500, detail="Error while updating user.")

    return user


@router.delete("/{id_user}", tags=["Users"])
async def delete_user(id_user: int, user_service=Depends(get_user_service)):
    """Delete a user from the system.
    Args:
        id_user (int)
        user_service (UserService): The service used to interact with user data.
    Returns:
        str: A confirmation message indicating the user was deleted.
    Raises:
        HTTPException: 404 error if the user is not found.
    """
    logger.info("Delete a user")
    user = user_service.find_by_id(id_user)
    if not user:
        raise HTTPException(status_code=404, detail="user (id={id_user}) not found.")

    user_service.delete(user)
    return f"user {user.username} deleted"
