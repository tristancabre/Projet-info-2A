from datetime import date

from pydantic import BaseModel


class NeoReadModel(BaseModel):
    """Data contract used to send a NEO from the backend to the frontend."""

    id_neo: int
    name: str
    size: int
    distance: int
    composition: list[str]
    closest_day: date

    # Allows building the model directly from a Neo business object
    model_config = {"from_attributes": True}