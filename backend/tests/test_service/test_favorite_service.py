import pytest
from unittest.mock import Mock, patch

from business_object.favorite import Favorite
from service.favorite_service import FavoriteService
from utils.exceptions import AlreadyFavoriteError, NeoNotFoundError, UserNotFoundError


class TestFavoriteService:

    @pytest.fixture
    def service(self):
        return FavoriteService()

    # =========================================================================
    # _check_user_exists
    # =========================================================================

    @patch("service.favorite_service.UserDao")
    def test_check_user_exists_success_when_user_exists(self, mock_user_dao_cls, service):
        # GIVEN
        mock_user_dao_instance = Mock()
        mock_user_dao_cls.return_value = mock_user_dao_instance
        mock_user_dao_instance.find_by_id.return_value = {"id_user": 1}

        # WHEN
        service._check_user_exists(id_user=1)

        # THEN
        mock_user_dao_cls.assert_called_once()
        mock_user_dao_instance.find_by_id.assert_called_once_with(1)

    @patch("service.favorite_service.UserDao")
    def test_check_user_exists_raises_user_not_found_error_when_none(self, mock_user_dao_cls, service):
        # GIVEN
        mock_user_dao_instance = Mock()
        mock_user_dao_cls.return_value = mock_user_dao_instance
        mock_user_dao_instance.find_by_id.return_value = None

        # WHEN / THEN
        with pytest.raises(UserNotFoundError, match="user \\(id=99\\) not found."):
            service._check_user_exists(id_user=99)

        mock_user_dao_instance.find_by_id.assert_called_once_with(99)

    # =========================================================================
    # add
    # =========================================================================

    @patch("service.favorite_service.FavoriteDao")
    @patch("service.favorite_service.NeoDao")
    def test_add_success(self, mock_neo_dao_cls, mock_favorite_dao_cls, service):
        # GIVEN
        service._check_user_exists = Mock()

        mock_neo_dao = Mock()
        mock_neo_dao_cls.return_value = mock_neo_dao
        mock_neo = Mock()
        mock_neo_dao.find_by_id.return_value = mock_neo

        mock_fav_dao = Mock()
        mock_favorite_dao_cls.return_value = mock_fav_dao
        expected_favorite = Mock(spec=Favorite)
        mock_fav_dao.add.return_value = expected_favorite

        # WHEN
        result = service.add(id_user=1, id_neo=101)

        # THEN
        assert result == expected_favorite
        service._check_user_exists.assert_called_once_with(1)
        mock_neo_dao.find_by_id.assert_called_once_with(101)
        mock_fav_dao.add.assert_called_once_with(1, mock_neo)

    @patch("service.favorite_service.FavoriteDao")
    @patch("service.favorite_service.NeoDao")
    def test_add_raises_user_not_found_error(self, mock_neo_dao_cls, mock_favorite_dao_cls, service):
        # GIVEN
        service._check_user_exists = Mock(side_effect=UserNotFoundError("User missing"))

        # WHEN / THEN
        with pytest.raises(UserNotFoundError, match="User missing"):
            service.add(id_user=1, id_neo=101)

        service._check_user_exists.assert_called_once_with(1)
        mock_neo_dao_cls.assert_not_called()
        mock_favorite_dao_cls.assert_not_called()

    @patch("service.favorite_service.FavoriteDao")
    @patch("service.favorite_service.NeoDao")
    def test_add_raises_neo_not_found_error(self, mock_neo_dao_cls, mock_favorite_dao_cls, service):
        # GIVEN
        service._check_user_exists = Mock()

        mock_neo_dao = Mock()
        mock_neo_dao_cls.return_value = mock_neo_dao
        mock_neo_dao.find_by_id.return_value = None

        # WHEN / THEN
        with pytest.raises(NeoNotFoundError, match="neo \\(id=404\\) not found."):
            service.add(id_user=1, id_neo=404)

        service._check_user_exists.assert_called_once_with(1)
        mock_neo_dao.find_by_id.assert_called_once_with(404)
        mock_favorite_dao_cls.assert_not_called()

    @patch("service.favorite_service.FavoriteDao")
    @patch("service.favorite_service.NeoDao")
    def test_add_raises_already_favorite_error_when_add_returns_none(
        self, mock_neo_dao_cls, mock_favorite_dao_cls, service
    ):
        # GIVEN
        service._check_user_exists = Mock()

        mock_neo_dao = Mock()
        mock_neo_dao_cls.return_value = mock_neo_dao
        mock_neo = Mock()
        mock_neo_dao.find_by_id.return_value = mock_neo

        mock_fav_dao = Mock()
        mock_favorite_dao_cls.return_value = mock_fav_dao
        mock_fav_dao.add.return_value = None

        # WHEN / THEN