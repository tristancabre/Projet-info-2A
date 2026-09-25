import itertools
from datetime import date


class NeoDistanceHistory:
    """The information about distance for a Neo  at a specific time."""

    _id_counter = itertools.count(1)

    def __init__(self, id_neo: int, observation_date: date, distance: int):
        self.id_history = next(NeoDistanceHistory._id_counter)
        self.id_neo = id_neo
        self.observation_date = observation_date
        self.distance = distance

    def __str__(self) -> str:
        return f"NeoDistanceHistory(id={self.id_history}, neo={self.id_neo}, date={self.observation_date}, distance={self.distance})"

    def as_list(self) -> list:
        return [self.id_history, self.id_neo, str(self.observation_date), self.distance]
