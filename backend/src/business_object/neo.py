from datetime import date


class Neo:
    """Class that represents Neos"""

    def __init__(
        self, name: str, id_neo: int, size: int, distance: int, closest_day: date,
        speed: float
    ):
        self.name = name
        self.id_neo = id_neo
        self.diameter = diameter
        self.distance = distance
        self.closest_day = closest_day
        self.speed = speed

    def __str__(self):
        return f"Neo({self.name}, id={self.id_neo})"

    def as_list(self) -> list:
        return [self.name, str(self.closest_day)]
