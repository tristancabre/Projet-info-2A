from datetime import date

from business_object import Neo


class Favorites:
    """A collection of favorited Neo objects."""

    def __init__(self):
        self.neos = []
        self.date_added = {}
        self.distance_history = {}

    def add_neo(self, neo: Neo) -> bool:
        """Add a Neo to favorites. Returns False if already present."""
        if neo in self.neos:
            return False
        self.neos.append(neo)
        self.date_added[neo.id_neo] = date.today()
        self.distance_history[neo.id_neo] = [neo.distance]
        return True

    def remove_neo(self, neo: Neo) -> bool:
        """Remove a Neo from favorites. Returns False if not present."""
        if neo not in self.neos:
            return False
        self.neos.remove(neo)
        self.date_added.pop(neo.id_neo, None)
        self.distance_history.pop(neo.id_neo, None)
        return True

    def get_distance_history(self, neo: Neo = None) -> list:
        """Return distance history for a specific Neo, or the whole mapping if none given."""
        if neo is not None:
            return self.distance_history.get(neo.id_neo, [])
        return self.distance_history
