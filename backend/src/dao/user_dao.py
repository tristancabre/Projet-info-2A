from business_object import User
from dao.db_connection import DBConnection
from utils.log_utils import log


class UserDao:
    """Data access for users.no hashing of the pwd needed here"""

    @log
    def create(self, user: User) -> bool:
        """Saves the user (password already hashed).
        Must fill user.id_user if the database generates it."""
        res = None
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO user(username, password, email) VALUES"
                        "(%(username)s, %(password)s, %(email)s)"
                        "RETURNING id_user;",
                        {
                            "username": user.username,
                            "password": user.password,
                            "email": user.email,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        created = False
        if res:
            user.id_user = res["id_user"]

    def find_by_username(self, username: str) -> User | None:
        """Find a user by their username.
        Args:
            username (str): The username of the user to find
        Returns:
            User matching the given username
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM user                       "
                        " WHERE username = %(username)s;   ",
                        {"username": username},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        user = None
        if res:
            user = User(
                id_player=res["id_player"],
                username=res["username"],
                email=res["email"],
                password=res["password"],
            )

        return user

    def list_all(self) -> list[User]:
        pass
        # To be done late

    def update(self, user: User) -> bool:
        pass
        # To be done late

    def delete(self, user: User) -> bool:
        pass
        # To be done late

    @log
    def find_by_id(self, id_user: int) -> User:
        """Find a user by their id.
        Args:
            id_user (int): The ID of the user to find
        Returns:
            User matching the given id
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                            "
                        "  FROM user                       "
                        " WHERE id_user = %(id_user)s;   ",
                        {"id_user": id_user},
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise

        user = None
        if res:
            user = User(
                id_player=res["id_player"],
                username=res["username"],
                email=res["email"],
                password=res["password"],
            )

        return user
