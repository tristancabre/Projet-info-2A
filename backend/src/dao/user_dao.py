from business_object.user import User
from dao.db_connection import DBConnection
from utils.log_utils import get_logger, log
from utils.singleton import Singleton

logger = get_logger(__name__)


class UserDao(metaclass=Singleton):
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
            created = True
        return created

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
                id_user=res["id_user"],
                username=res["username"],
                email=res["email"],
                password=res["password"],
            )

        return user

    def list_all(self) -> list[User]:
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT *                                "
                        "  FROM user                           "
                        " ORDER BY username;                     "
                    )
                    res = cursor.fetchall()
        except Exception as e:
            logger.error(e)
            raise

        users_list = []

        if res:
            for row in res:
                user = User(
                    id_user=row["id_user"],
                    username=row["username"],
                    password=row["password"],
                    email=row["email"],
                )

                users_list.append(user)

        return users_list

    @log
    def update(self, user: User) -> bool:
        """Update a user in the database.
        Args:
            user to be updated
        Returns:
            True if update is successful, False if unsuccessful
        """
        nb_affected_rows = 0

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE user                                                  "
                        "   SET username = %(username)s,                                "
                        "       password = COALESCE(%(password)s, password),            "
                        "       email = %(email)s,                                      "
                        " WHERE id_user = %(id_user)s;                              ",
                        {
                            "username": user.username,
                            "password": user.password,
                            "email": user.email,
                            "id_user": user.id_user,
                        },
                    )
                    nb_affected_rows = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return nb_affected_rows == 1

    @log
    def delete(self, user: User) -> bool:
        """Delete a user from the database.
        Args:
            User to delete from the database
        Returns:
            True if the user was successfully deleted, False if unsuccessfully
        """
        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM user                               "
                        " WHERE id_user = %(id_user)s                 ",
                        {"id_user": user.id_user},
                    )
                    res = cursor.rowcount
        except Exception as e:
            logger.error(e)
            raise

        return res > 0

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
                id_user=res["id_user"],
                username=res["username"],
                email=res["email"],
                password=res["password"],
            )

        return user
