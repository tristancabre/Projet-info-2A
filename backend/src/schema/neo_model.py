# schema/neo_model.py
from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from business_object.neo import Neo


def _check_positive(v: float | None) -> float | None:
    if v is not None and v < 0:
        raise ValueError("Value must be positive")
    return v


class NeoModel(BaseModel):
    """Data contract for creating or updating a neo.

    The id is not part of the body, and the rarity is computed by the
    backend from the distance and the diameter."""

    name: str
    diameter: float | None = None
    distance: float
    closest_day: date
    speed: float | None = None

    @field_validator("diameter", "distance", "speed")
    @classmethod
    def check_positive(cls, v: float | None) -> float | None:
        return _check_positive(v)


class NeoReadModel(NeoModel):
    """Public view of a neo, as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id_neo: int
    rarity: int | None = None

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
