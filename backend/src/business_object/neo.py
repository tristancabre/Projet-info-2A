from datetime import date


class Neo:
    """Class that represents Neos"""

    def __init__(
        self, name: str, id_neo: int, diameter: int, distance: int, composition: list, closest_day: date
    ):
        self.name = name
        self.id_neo = id_neo
        self.diameter = diameter
        self.distance = distance
        self.composition = composition
        self.closest_day = closest_day

    def __str__(self):
        return f"Neo({self.name}, id={self.id_neo})"

    def as_list(self) -> list:
        return [self.name, str(self.closest_day)]
