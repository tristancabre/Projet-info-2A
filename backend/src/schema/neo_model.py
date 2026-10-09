from datetime import date

from pydantic import BaseModel


class NeoReadModel(BaseModel):
    """Data contract used to send a NEO from the backend to the frontend."""

    name: str
    diameter: float | None
    distance: float | None
    speed: float | None
    closest_day: date
    rarity: int
    # Allows building the model directly from a Neo business object
    model_config = {"from_attributes": True}
