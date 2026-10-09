# schema/neo_schema.py
from datetime import date

from pydantic import BaseModel, field_validator

from business_object.neo import Neo


def _check_positive(v: float | None) -> float | None:
    if v is not None and v < 0:
        raise ValueError("Value must be positive")
    return v


class NeoModel(BaseModel):
    """Acts as the data contract between the frontend and the backend.

    It defines the JSON structure used to exchange neo information
    when creating or updating a neo (the id is not part of the body)."""

    name: str
    diameter: float | None = None
    distance: float
    closest_day: date
    speed: float | None = None
    rarity: int

    @field_validator("diameter", "distance", "speed")
    @classmethod
    def check_positive(cls, v: float | None) -> float | None:
        return _check_positive(v)


class NeoReadModel(NeoModel):
    """Public view of a neo, as returned by the API."""

    id_neo: int

    @classmethod
    def from_neo(cls, neo: Neo) -> "NeoReadModel":
        return cls(
            id_neo=neo.id_neo,
            name=neo.name,
            diameter=neo.diameter,
            distance=neo.distance,
            closest_day=neo.closest_day,
            speed=neo.speed,
            rarity=neo.rarity,
        )
