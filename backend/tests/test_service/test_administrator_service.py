import pytest
from unittest.mock import Mock, patch

from business_object.user import Administrator, User
from service.administrator_service import AdministratorService


class TestAdministratorService:

    # =========================================================================
    # __init__
    # =========================================================================

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_init_success_when_user_is_admin(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator)
        mock_admin.is_admin = True

        # WHEN
        service = AdministratorService(admin=mock_admin)

        # THEN
        assert service.admin == mock_admin
        mock_super_init.assert_called_once()

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_init_raises_permission_error_when_user_not_admin(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator)
        mock_admin.is_admin = False

        # WHEN / THEN
        with pytest.raises(PermissionError, match="Administrators only"):
            AdministratorService(admin=mock_admin)

    # =========================================================================
    # update_account
    # =========================================================================

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_update_account_success(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)

        target_user = Mock(spec=User)
        target_user.username = "old_user"
        target_user.email = "old@example.com"

        updated_user = Mock(spec=User)

        service.find_by_id = Mock(return_value=target_user)
        service.update = Mock(return_value=updated_user)

        # WHEN
        result = service.update_account(
            id_user=10,
            new_username="new_user",
            new_email="new@example.com",
            new_password="secret_password",
        )

        # THEN
        assert result == updated_user
        assert target_user.username == "new_user"
        assert target_user.email == "new@example.com"
        service.find_by_id.assert_called_once_with(10)
        service.update.assert_called_once_with(target_user, "secret_password")

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_update_account_partial_fields(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)

        target_user = Mock(spec=User)
        target_user.username = "old_user"
        target_user.email = "keep_email@example.com"

        service.find_by_id = Mock(return_value=target_user)
        service.update = Mock(return_value=target_user)

        # WHEN
        result = service.update_account(id_user=10, new_username="only_new_user")

        # THEN
        assert result == target_user
        assert target_user.username == "only_new_user"
        assert target_user.email == "keep_email@example.com"
        service.update.assert_called_once_with(target_user, None)

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_update_account_raises_value_error_when_user_not_found(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)
        service.find_by_id = Mock(return_value=None)
        service.update = Mock()

        # WHEN / THEN
        with pytest.raises(ValueError, match="User not found"):
            service.update_account(id_user=404, new_username="ghost")

        service.find_by_id.assert_called_once_with(404)
        service.update.assert_not_called()

    # =========================================================================
    # delete_account
    # =========================================================================

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_delete_account_success(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True, id_user=1)
        service = AdministratorService(admin=mock_admin)

        target_user = Mock(spec=User)
        service.find_by_id = Mock(return_value=target_user)
        service.delete = Mock(return_value=True)

        # WHEN
        result = service.delete_account(id_user=2)

        # THEN
        assert result is True
        service.find_by_id.assert_called_once_with(2)
        service.delete.assert_called_once_with(target_user)

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_delete_account_raises_value_error_when_self_deletion(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True, id_user=1)
        service = AdministratorService(admin=mock_admin)
        service.find_by_id = Mock()
        service.delete = Mock()

        # WHEN / THEN
        with pytest.raises(ValueError, match="An admin cannot delete their own account"):
            service.delete_account(id_user=1)

        service.find_by_id.assert_not_called()
        service.delete.assert_not_called()

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_delete_account_raises_value_error_when_user_not_found(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True, id_user=1)
        service = AdministratorService(admin=mock_admin)
        service.find_by_id = Mock(return_value=None)
        service.delete = Mock()

        # WHEN / THEN
        with pytest.raises(ValueError, match="User not found"):
            service.delete_account(id_user=99)

        service.find_by_id.assert_called_once_with(99)
        service.delete.assert_not_called()

    # =========================================================================
    # view_connection_history
    # =========================================================================

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_view_connection_history_all_users_success(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)

        mock_dao = Mock()
        expected_history = [{"log_id": 1, "action": "login"}]
        mock_dao.get_connection_history.return_value = expected_history
        service.user_dao = mock_dao

        # WHEN
        result = service.view_connection_history(id_user=None, limit=50)

        # THEN
        assert result == expected_history
        mock_dao.get_connection_history.assert_called_once_with(None, 50)

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_view_connection_history_specific_user_success(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)

        service.find_by_id = Mock(return_value=Mock(spec=User))
        mock_dao = Mock()
        expected_history = [{"log_id": 2, "action": "logout"}]
        mock_dao.get_connection_history.return_value = expected_history
        service.user_dao = mock_dao

        # WHEN
        result = service.view_connection_history(id_user=5, limit=10)

        # THEN
        assert result == expected_history
        service.find_by_id.assert_called_once_with(5)
        mock_dao.get_connection_history.assert_called_once_with(5, 10)

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_view_connection_history_raises_value_error_when_limit_invalid(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)

        # WHEN / THEN
        with pytest.raises(ValueError, match="limit doit être strictement positif."):
            service.view_connection_history(limit=0)

        with pytest.raises(ValueError, match="limit doit être strictement positif."):
            service.view_connection_history(limit=-5)

    @patch("service.administrator_service.UserService.__init__", return_value=None)
    def test_view_connection_history_raises_value_error_when_user_not_found(self, mock_super_init):
        # GIVEN
        mock_admin = Mock(spec=Administrator, is_admin=True)
        service = AdministratorService(admin=mock_admin)
        service.find_by_id = Mock(return_value=None)

        # WHEN / THEN
        with pytest.raises(ValueError, match="Utilisateur introuvable."):
            service.view_connection_history(id_user=12)

        service.find_by_id.assert_called_once_with(12)