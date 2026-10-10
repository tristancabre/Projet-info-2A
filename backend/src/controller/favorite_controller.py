# controller/favorite_controller.py
from fastapi import APIRouter, Depends, HTTPException

from business_object.user import User
from schema.favorite_model import FavoriteReadModel
from service.favorite_service import FavoriteService
from utils.auth import get_current_user
from utils.exceptions import AlreadyFavoriteError, NeoNotFoundError, UserNotFoundError
from utils.log_utils import get_logger

# À inclure avec le préfixe : app.include_router(router, prefix="/favorites", tags=["Favorites"])
router = APIRouter()

logger = get_logger(__name__)


def get_favorite_service() -> FavoriteService:
    """Dependency Injection provider for FavoriteService."""
    return FavoriteService()


# Chaque utilisateur ne gère que SES favoris : l'identifiant vient du token (utilisateur
# connecté) et non plus de l'URL, donc personne ne peut agir sur les favoris d'un autre.


@router.get("/", response_model=list[FavoriteReadModel], tags=["Favorites"])
def list_favorites(
    current_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """List the favorite neos of the connected user, the most recently added first.
    Raises:
        HTTPException: 404 error if the user no longer exists.
    """
    logger.info("List the favorites of the connected user")
    try:
        return favorite_service.list_by_user(current_user.id_user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{id_neo}",
    response_model=FavoriteReadModel,
    status_code=201,
    tags=["Favorites"],
)
def add_favorite(
    id_neo: int,
    current_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Add a neo to the favorites of the connected user.
    Raises:
        HTTPException: 404 error if the neo is not found.
        HTTPException: 409 error if the neo is already in the favorites.
    """
    logger.info("Add a favorite")
    try:
        return favorite_service.add(current_user.id_user, id_neo)
    except (UserNotFoundError, NeoNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyFavoriteError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{id_neo}", tags=["Favorites"])
def remove_favorite(
    id_neo: int,
    current_user: User = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Remove a neo from the favorites of the connected user.
    Raises:
        HTTPException: 404 error if the neo is not in the favorites of the user.
    """
    logger.info("Remove a favorite")
    if not favorite_service.remove(current_user.id_user, id_neo):
        raise HTTPException(
            status_code=404,
            detail=f"neo (id={id_neo}) is not in your favorites.",
        )
    return {"message": f"neo (id={id_neo}) removed from the favorites"}
