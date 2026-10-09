from datetime import date


class Neo:
    """Class that represents Neos"""

    def __init__(
        self,
        name: str,
        diameter: float | None,
        distance: float,
        closest_day: date,
        speed: float | None,
        rarity: int | None,
        id_neo: int | None = None
    ):
        self.id_neo = id_neo
        self.name = name
        self.diameter = diameter
        self.distance = distance
        self.closest_day = closest_day
        self.speed = speed
        self.rarity = rarity

    def __str__(self):
        return f"Neo({self.name}, id={self.id_neo})"

    def as_list(self) -> list:
        return [self.name, str(self.closest_day)]
