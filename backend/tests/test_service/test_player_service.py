from unittest.mock import MagicMock

from business_object.player import Player
from dao.player_dao import PlayerDao
from service.player_service import PlayerService

player_list = [
    Player(username="jp", elo="1000", email="jp@mail.fr", password="1234"),
    Player(username="lea", elo="1000", email="lea@mail.fr", password="0000"),
    Player(username="gg", elo="1000", email="gg@mail.fr", password="abcd"),
]


def test_create_ok():
    """Successfully create a Player"""

    # GIVEN
    username, password, elo, email, pokemon_fan = "jp", "1234", 1500, "z@mail.oo", True
    PlayerDao().create = MagicMock(return_value=True)

    # WHEN
    player = PlayerService().create(username, password, elo, email, pokemon_fan)

    # THEN
    assert player.username == username


def test_create_fail():
    """Fail to create a Player because PlayerDao().create returns False"""

    # GIVEN
    username, password, elo, email, pokemon_fan = "jp", "1234", 1500, "z@mail.oo", True
    PlayerDao().create = MagicMock(return_value=False)

    # WHEN
    player = PlayerService().create(username, password, elo, email, pokemon_fan)

    # THEN
    assert player is None


def test_find_all():
    """List Players"""

    # GIVEN
    PlayerDao().find_all = MagicMock(return_value=player_list)

    # WHEN
    res = PlayerService().find_all()

    # THEN
    assert len(res) == 3


def test_username_already_used_yes():
    """The username is already used in player_list"""

    # GIVEN
    username = "lea"

    # WHEN
    PlayerDao().find_all = MagicMock(return_value=player_list)
    res = PlayerService().username_already_used(username)

    # THEN
    assert res


def test_username_already_used_no():
    """The username is not used in player_list"""

    # GIVEN
    username = "kitten"

    # WHEN
    PlayerDao().find_all = MagicMock(return_value=player_list)
    res = PlayerService().username_already_used(username)

    # THEN
    assert not res


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
