from datetime import date

from pydantic import BaseModel


class NeoReadModel(BaseModel):
    """Data contract used to send a NEO from the backend to the frontend."""

    id_neo: int
    name: str
    diameter: float | None
    distance: float | None
    closest_day: date
    speed: float | None

    # Allows building the model directly from a Neo business object
    model_config = {"from_attributes": True}
