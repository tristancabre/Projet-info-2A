import hashlib
from abc import ABC, abstractmethod


class User(ABC):
    def __init__(self, id_user: int, username: str, password: str, email: str):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.email = email

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
    def __init__(self, id_user: int, username: str, password: str, email: str, visitor_name: str):
        super().__init__(id_user, username, password, email)
        self.visitor_name = visitor_name

    @property
    def is_admin(self) -> bool:
        """Distinguish roles for different Users : Fase pour Visitors"""
        return False


class Administrator(User):
    def __init__(self, id_user: int, username: str, password: str, email: str, admin_name: str):
        super().__init__(id_user, username, password, email)
        self.admin_name = admin_name

    @property
    def is_admin(self) -> bool:
        """Distinguish roles for different Users : Fase pour Administrators."""

        return True
