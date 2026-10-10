from dao.favorite_dao import FavoriteDao
from utils.exceptions import AlreadyFavoriteError, NeoNotFoundError, UserNotFoundError

from business_object.favorite import Favorite
from dao.neo_dao import NeoDao
from dao.user_dao import UserDao
from utils.log_utils import log


class FavoriteService:
    """Business logic for the favorites of the users.

    Business errors (unknown user, unknown neo, already a favorite) raise an
    exception, which the controller turns into a 4xx response."""

    @staticmethod
    def _check_user_exists(id_user: int) -> None:
        if UserDao().find_by_id(id_user) is None:
            raise UserNotFoundError(f"user (id={id_user}) not found.")

    @log
    def add(self, id_user: int, id_neo: int) -> Favorite:
        """Adds a neo to the favorites of a user.

        Raises:
            UserNotFoundError: if the user does not exist.
            NeoNotFoundError: if the neo does not exist.
            AlreadyFavoriteError: if the neo is already in the favorites of the user.
        """
        self._check_user_exists(id_user)
        neo = NeoDao().find_by_id(id_neo)
        if neo is None:
            raise NeoNotFoundError(f"neo (id={id_neo}) not found.")

        favorite = FavoriteDao().add(id_user, neo)
        if favorite is None:
            raise AlreadyFavoriteError(f"neo (id={id_neo}) is already in the favorites.")
        return favorite

    @log
    def remove(self, id_user: int, id_neo: int) -> bool:
        """Removes a neo from the favorites of a user.
        Returns True if it was removed, False if it was not a favorite."""
        return FavoriteDao().remove(id_user, id_neo)

    @log
    def list_by_user(self, id_user: int) -> list[Favorite]:
        """Returns the favorites of a user.

        Raises:
            UserNotFoundError: if the user does not exist.
        """
        self._check_user_exists(id_user)
        return FavoriteDao().find_by_user(id_user)
