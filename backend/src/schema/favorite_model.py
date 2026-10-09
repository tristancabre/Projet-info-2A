# schema/favorite_model.py
from datetime import date

from pydantic import BaseModel, ConfigDict

from schema.neo_model import NeoReadModel


class FavoriteReadModel(BaseModel):
    """A favorite as returned by the API: the neo and the date it was added."""

    model_config = ConfigDict(from_attributes=True)

    id_favorite: int
    date_added: date
    neo: NeoReadModel
