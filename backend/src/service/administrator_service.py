from business_object.user import Administrator, User
from service.user_service import UserService
from utils.log_utils import log


class AdministratorService(UserService):
    """Service for administrators : manage accounts, view history"""

    def __init__(self, admin: Administrator):
        super().__init__(self)

        if not admin.is_admin:
            raise PermissionError("Administrators only")
        self.admin = admin

    # Manage accounts with update and delete,

    @log
    def update_account(
        self,
        id_user: int,
        new_username: str | None = None,
        new_email: str | None = None,
        new_password: str | None = None,
    ) -> User:
        """Modify an account (username, email, password)."""
        user = self.find_by_id(id_user)
        if user is None:
            raise ValueError("User not found")

        if new_username is not None:
            user.username = new_username
        if new_email is not None:
            user.email = new_email

        return self.update(user, new_password)

    @log
    def delete_account(self, id_user: int) -> bool:
        """Delete accounts in the app"""
        if id_user == self.admin.id_user:
            raise ValueError("An admin cannot delete their own account")

        user = self.find_by_id(id_user)
        if user is None:
            raise ValueError("User not found")
        return self.delete(user)

    # Special actions for Administrators

    # AdministratorService
    @log
    def view_connection_history(self, id_user: int | None = None, limit: int = 100) -> list[dict]:
        if limit <= 0:
            raise ValueError("limit doit être strictement positif.")
        if id_user is not None and self.find_by_id(id_user) is None:
            raise ValueError("Utilisateur introuvable.")
        return self.user_dao.get_connection_history(id_user, limit)

    def update_nasa(self):
        pass # Voir en groupe façon de faire
