import hashlib
from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, username: str, password: str, email: str, id_user: int | None = None):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.email = email
        self.is_admin = None

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return hashlib.sha256(plain_password.encode()).hexdigest()

    def check_password(self, plain_password: str) -> bool:
        return User.hash_password(plain_password) == self.password

    @property
    @abstractmethod
    def is_admin(self) -> bool:
        """True for an administrator, False for a regular user."""


class RegularUser(User):
    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        visitor_name: str,
        id_user: int | None = None,
    ):
        super().__init__(username, password, email, id_user)
        self.visitor_name = visitor_name
        self.is_admin = False


class Administrator(User):
    def __init__(
        self,
        username: str,
        password: str,
        email: str,
        admin_name: str,
        id_user: int | None = None,
    ):
        super().__init__(username, password, email, id_user)
        self.admin_name = admin_name
        self.is_admin = True
