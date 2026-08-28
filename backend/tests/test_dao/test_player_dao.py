import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.player import Player
from dao.player_dao import PlayerDao
from utils.reset_database import ResetDatabase
from utils.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


def test_find_by_id_existing():
    """Find a player by an existing id"""

    # GIVEN
    id_player = 998

    # WHEN
    player = PlayerDao().find_by_id(id_player)

    # THEN
    assert player is not None


def test_find_by_id_non_existing():
    """Find a player by a non-existing id"""

    # GIVEN
    id_player = 9999999999999

    # WHEN
    player = PlayerDao().find_by_id(id_player)

    # THEN
    assert player is None


def test_find_all():
    """Verify the method returns a list of Player objects
    with length >= 2
    """

    # WHEN
    players = PlayerDao().find_all()

    # THEN
    assert isinstance(players, list)
    for p in players:
        assert isinstance(p, Player)
    assert len(players) >= 2


def test_create_ok():
    """Successfully create a Player"""

    # GIVEN
    player = Player(username="gg", elo=1000, email="test@test.io")

    # WHEN
    creation_ok = PlayerDao().create(player)

    # THEN
    assert creation_ok
    assert player.id_player


def test_create_ko():
    """Fail to create a Player (invalid elo and email)"""

    # GIVEN
    player = Player(username="gg", elo="string_value", email=12)

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        PlayerDao().create(player)

    # assert not PlayerDao().create(player)


def test_update_ok():
    """Successfully update a Player"""

    # GIVEN
    new_email = "maurice@mail.com"
    player = Player(id_player=997, username="maurice", elo=1000, email=new_email)

    # WHEN
    update_ok = PlayerDao().update(player)

    # THEN
    assert update_ok


def test_update_ko():
    """Fail to update a Player (unknown id)"""

    # GIVEN
    player = Player(id_player=8888, username="unknown id", elo=1000, email="no@mail.com")

    # WHEN
    update_ok = PlayerDao().update(player)

    # THEN
    assert not update_ok


def test_delete_ok():
    """Successfully delete a Player"""

    # GIVEN
    player = Player(id_player=995, username="miguel", elo=1000, email="miguel@project.io")

    # WHEN
    delete_ok = PlayerDao().delete(player)

    # THEN
    assert delete_ok


def test_delete_ko():
    """Fail to delete a Player (unknown id)"""

    # GIVEN
    player = Player(id_player=8888, username="unknown id", elo=1000, email="no@z.io")

    # WHEN
    delete_ok = PlayerDao().delete(player)

    # THEN
    assert not delete_ok


def test_login_ok():
    """Successfully login a Player"""

    # GIVEN
    username = "batricia"
    password = "9876"

    # WHEN
    player = PlayerDao().login(username, hash_password(password, username))

    # THEN
    assert isinstance(player, Player)


def test_login_ko():
    """Fail login for a Player (wrong username or password)"""

    # GIVEN
    username = "toto"
    password = "poiuytreza"

    # WHEN
    player = PlayerDao().login(username, hash_password(password, username))

    # THEN
    assert not player


if __name__ == "__main__":
    pytest.main([__file__])
