import string

from business_object import Administrator, User, Visitor
from utils.log_utils import log

MIN_PASSWORD_LENGTH = 10


class UserService:
    """The services for the users."""

    def __init__(self, user_dao):
        self.user_dao = user_dao

    @staticmethod
    def validate_password(password: str) -> None:
        """Raises ValueError if the password does not respect the rules."""
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"The password has to contain minimum {MIN_PASSWORD_LENGTH} characters."
            )
        if not any(c in string.punctuation for c in password):
            raise ValueError("The password has to contain at least one special character.")

    def username_already_used(self, pseudo: str) -> bool:
        """True if a user with this pseudo already exists."""
        return self.user_dao.find_by_pseudo(pseudo) is not None

    @log
    def create(self, pseudo: str, password: str, email: str, is_admin: bool = False) -> User:
        if self.username_already_used(pseudo):
            raise ValueError("pseudo already used")

        self.validate_password(password)
        hashed = User.hash_password(password)  # tackled in the business object part of User

        if is_admin:  # Thanks to the bool (True) in the user.py
            user = Administrator(pseudo, hashed, email, admin_name=pseudo)
        else:
            user = Visitor(pseudo, hashed, email, visitor_name=pseudo)

        self.user_dao.create(user)
        return user

    @log
    def list_all(self) -> list[User]:
        return self.user_dao.list_all()

    @log
    def find_by_pseudo(self, pseudo: str) -> User | None:
        """Returns the user with this pseudo, or None."""
        return self.user_dao.find_by_pseudo(pseudo)

    @log
    def find_by_id(self, id_user: int) -> User | None:
        """Finds a specific user by their unique id.
        Args:
            id_user (int)
        Returns:
            Player object if found, otherwise None.
        """
        return self.user_dao.find_by_id(id_user)

    @log
    def login(self, pseudo: str, password: str) -> User:
        user = self.user_dao.find_by_pseudo(pseudo)
        if user is None or not user.check_password(password):
            raise ValueError("pseudo or password incorrect, try again")
        return user

    @log
    def update(self, user: User, new_password: str | None = None) -> User:
        """Updates a user. If update a password, it is validated then hashed."""
        other = self.user_dao.find_by_pseudo(user.pseudo)
        if other is not None and other.id_user != user.id_user:
            raise ValueError("Pseudo already used, find something else")

        if new_password is not None:
            self.validate_password(new_password)
            user.password = User.hash_password(new_password)

        self.user_dao.update(user)
        return user

    @log
    def delete(self, user: User) -> bool:
        return self.user_dao.delete(user)
