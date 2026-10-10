# business_object/favorite.py
from datetime import date

from business_object.neo import Neo


class Favorite:
    """A neo added to the favorites of a user."""

    def __init__(
        self,
        id_user: int,
        neo: Neo,
        date_added: date | None = None,
        id_favorite: int | None = None,
    ):
        self.id_favorite = id_favorite
        self.id_user = id_user
        self.neo = neo
        self.date_added = date_added

    def __str__(self):
        return f"Favorite(user={self.id_user}, {self.neo})"
