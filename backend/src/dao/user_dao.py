from business_object import User


class UserDao:
    """Data access for users.no hashing of the pwd needed here"""

    def create(self, user: User) -> bool:
        """Saves the user (password already hashed).
        Must fill user.id_user if the database generates it."""
        # To be done late

    def find_by_pseudo(self, pseudo: str) -> User | None:
        """Returns the user (Administrator or Visitor), or None if not found."""
        # To be done late

    def list_all(self) -> list[User]:
        # To be done late

    def update(self, user: User) -> bool:
        # To be done late

    def delete(self, user: User) -> bool:
        # To be done late