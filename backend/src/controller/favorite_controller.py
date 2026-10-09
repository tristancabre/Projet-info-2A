# controller/favorite_controller.py
from fastapi import APIRouter, Depends, HTTPException

from schema.favorite_model import FavoriteReadModel
from service.favorite_service import FavoriteService
from utils.exceptions import AlreadyFavoriteError, NeoNotFoundError, UserNotFoundError
from utils.log_utils import get_logger

# À inclure avec un préfixe, par exemple : app.include_router(router, prefix="/favorites")
router = APIRouter()

logger = get_logger(__name__)


def get_favorite_service() -> FavoriteService:
    """Dependency Injection provider for FavoriteService."""
    return FavoriteService()


# ATTENTION : ici l'identifiant de l'utilisateur est lu dans l'URL, donc n'importe
# qui peut consulter ou modifier les favoris de n'importe qui. Une fois
# l'authentification en place, remplacez le paramètre `id_user` par l'utilisateur
# connecté (dépendance du type `current_user = Depends(get_current_user)`).


@router.get("/{id_user}", response_model=list[FavoriteReadModel], tags=["Favorites"])
def list_favorites(id_user: int, favorite_service: FavoriteService = Depends(get_favorite_service)):
    """List the favorite neos of a user, the most recently added first.
    Raises:
        HTTPException: 404 error if the user is not found.
    """
    logger.info("List the favorites of a user")
    try:
        return favorite_service.list_by_user(id_user)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{id_user}/{id_neo}",
    response_model=FavoriteReadModel,
    status_code=201,
    tags=["Favorites"],
)
def add_favorite(
    id_user: int,
    id_neo: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Add a neo to the favorites of a user.
    Raises:
        HTTPException: 404 error if the user or the neo is not found.
        HTTPException: 409 error if the neo is already in the favorites.
    """
    logger.info("Add a favorite")
    try:
        return favorite_service.add(id_user, id_neo)
    except (UserNotFoundError, NeoNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyFavoriteError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{id_user}/{id_neo}", tags=["Favorites"])
def remove_favorite(
    id_user: int,
    id_neo: int,
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    """Remove a neo from the favorites of a user.
    Raises:
        HTTPException: 404 error if the neo is not in the favorites of the user.
    """
    logger.info("Remove a favorite")
    if not favorite_service.remove(id_user, id_neo):
        raise HTTPException(
            status_code=404,
            detail=f"neo (id={id_neo}) is not in the favorites of user (id={id_user}).",
        )
    return {"message": f"neo (id={id_neo}) removed from the favorites"}
