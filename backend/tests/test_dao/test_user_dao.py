import os
from unittest.mock import patch

import pytest

from business_object.user import User
from dao.user_dao import UserDao
from utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def test_find_by_id_existing():
    """Test the method Find a User by its id"""
    # Given (id_user = 1 is admin in our table in data)
    id_user = 1
    # When
    user = UserDao().find_by_id(id_user)
    # then
    assert user is not None


def test_find_by_id_non_existing():
    """Test the method to find a user by its id if it doesn't exist"""
    id_user = 9999  # given
    user = UserDao().find_by_id(id_user)  # when
    assert user is None  # Then


def test_list_all():
    """Test the method to list all users, check whether it returns a list of Users
    objects with length >= 2"""
    # when
    users = UserDao().list_all()
    # then
    assert isinstance(users, list)
    for u in users:
        assert isinstance(u, User)
    assert (len(users)) >= 2
