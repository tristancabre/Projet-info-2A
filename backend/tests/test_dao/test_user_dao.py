import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.user import Administrator, RegularUser, User
from dao.user_dao import UserDao
from utils.reset_database import ResetDatabase
from utils.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def test_find_by_id_existing():
    """Find a user by an existing id"""

    # GIVEN
    id_user = 1

    # WHEN
    user = UserDao().find_by_id(id_user)

    # THEN
    assert user is not None
    assert isinstance(user, User)


def test_find_by_id_non_existing():
    """Find a user by a non existing id"""

    # GIVEN
    id_user = 999999

    # WHEN
    user = UserDao().find_by_id(id_user)

    # THEN
    assert user is None


def test_find_by_username_existing():
    """Find a user by its username"""

    # GIVEN
    username = "batricia"

    # WHEN
    user = UserDao().find_by_username(username)

    # THEN
    assert user is not None
    assert user.username == username


def test_find_by_username_non_existing():
    """Find a user by a non existing username"""

    # WHEN
    user = UserDao().find_by_username("imnobody")

    # THEN
    assert user is None


def test_find_by_id_admin_returns_administrator():
    """An admin row must be rebuilt as an Administrator"""

    # GIVEN
    id_admin = 2

    # WHEN
    user = UserDao().find_by_id(id_admin)

    # THEN
    assert isinstance(user, Administrator)


def test_list_all():
    """Verify the method returns a list of User objects with length >= 2"""

    # WHEN
    users = UserDao().list_all()

    # THEN
    assert isinstance(users, list)
    for u in users:
        assert isinstance(u, User)
    assert len(users) >= 2


def test_create_ok():
    """create a User successfully"""

    # GIVEN
    user = RegularUser(
        username="gab",
        password=hash_password("12345", "gab"),
        email="test@test.io",
        visitor_name="gab",
    )

    # WHEN
    creation_ok = UserDao().create(user)

    # THEN
    assert creation_ok
    assert user.id_user


def test_create_ko():
    """Fail to create a User because the username is already used)"""

    # GIVEN
    user = RegularUser(
        username="batricia",  # already exist one with this name
        password=hash_password("1234", "batricia"),
        email="autre_batricia@test.io",
        visitor_name="batricia",
    )

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        UserDao().create(user)


def test_update_ok():
    """Update a User is ok successfully"""

    # GIVEN
    new_email = "maurice@mail.com"
    user = RegularUser(
        id_user=3,
        username="maurice",
        password=hash_password("1234", "maurice"),
        email=new_email,
        visitor_name="maurice",
    )

    # WHEN
    update_ok = UserDao().update(user)

    # THEN
    assert update_ok


def test_update_ko():
    """Fail to update a User (unknown id)"""

    # GIVEN
    user = RegularUser(
        id_user=8888,
        username="unknown",
        password="x",
        email="no@mail.com",
        visitor_name="unknown",
    )

    # WHEN
    update_ok = UserDao().update(user)

    # THEN
    assert not update_ok


def test_delete_ok():
    """Delete a User"""

    # GIVEN
    user = RegularUser(
        id_user=5,
        username="miguel",
        password="x",
        email="miguel@project.io",
        visitor_name="miguel",
    )

    # WHEN
    delete_ok = UserDao().delete(user)

    # THEN
    assert delete_ok


def test_delete_ko():
    """Fail to delete a User because the id is not recognised"""

    # GIVEN
    user = RegularUser(
        id_user=8888,
        username="unknown",
        password="x",
        email="no@z.io",
        visitor_name="unknown",
    )

    # WHEN
    delete_ok = UserDao().delete(user)

    # THEN
    assert not delete_ok


def test_login_ok():
    """login a User ok (succesffuly)"""

    # GIVEN
    username = "batricia"
    password = "9876"

    # WHEN
    user = UserDao().login(username, hash_password(password, username))

    # THEN
    assert isinstance(user, User)


def test_login_ko():
    """Fail login for a User : cause is wrong username or password"""

    # GIVEN
    username = "gabrielle"
    password = "test_log_ko"

    # WHEN
    user = UserDao().login(username, hash_password(password, username))

    # THEN
    assert not user


def test_record_connection_and_history():
    """The history registers connections and works successfully"""

    # GIVEN
    id_user = 3

    # WHEN
    UserDao().record_connection(id_user)
    history = UserDao().get_connection_history(id_user=id_user)

    # THEN
    assert len(history) >= 1
    assert history[0]["id_user"] == id_user


if __name__ == "__main__":
    pytest.main([__file__])
