import pytest
from unittest.mock import Mock, patch

from business_object.user import Administrator, RegularUser, User
from service.user_service import UserService


class TestUserService:

    @pytest.fixture
    def service(self):
        return UserService()

    # =========================================================================
    # validate_password
    # =========================================================================

    def test_validate_password_success(self, service):
        # GIVEN
        valid_password = "ValidPassword123!"

        # WHEN / THEN
        service.validate_password(valid_password)

    def test_validate_password_raises_value_error_when_too_short(self, service):
        # GIVEN
        short_password = "Pass1!"

        # WHEN / THEN
        with pytest.raises(
            ValueError,
            match="The password has to contain minimum 10 characters.",
        ):
            service.validate_password(short_password)

    def test_validate_password_raises_value_error_when_no_special_char(self, service):
        # GIVEN
        password_without_special = "ValidPassword123"

        # WHEN / THEN
        with pytest.raises(
            ValueError,
            match="The password has to contain at least one special character.",
        ):
            service.validate_password(password_without_special)

    # =========================================================================
    # username_already_used
    # =========================================================================

    @patch("service.user_service.UserDao")
    def test_username_already_used_returns_true_when_user_exists(
        self, mock_user_dao_cls, service
    ):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        mock_dao.find_by_username.return_value = Mock(spec=User)

        # WHEN
        result = service.username_already_used("john_doe")

        # THEN
        assert result is True
        mock_dao.find_by_username.assert_called_once_with("john_doe")

    @patch("service.user_service.UserDao")
    def test_username_already_used_returns_false_when_user_not_found(
        self, mock_user_dao_cls, service
    ):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        mock_dao.find_by_username.return_value = None

        # WHEN
        result = service.username_already_used("unknown_user")

        # THEN
        assert result is False
        mock_dao.find_by_username.assert_called_once_with("unknown_user")

    # =========================================================================
    # create
    # =========================================================================

    @patch("service.user_service.UserDao")
    @patch("service.user_service.User.hash_password", return_value="hashed_pwd")
    @patch("service.user_service.RegularUser")
    def test_create_regular_user_success(
        self, mock_regular_cls, mock_hash, mock_user_dao_cls, service
    ):
        # GIVEN
        service.username_already_used = Mock(return_value=False)
        service.validate_password = Mock()

        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        mock_created_user = Mock(spec=RegularUser)
        mock_regular_cls.return_value = mock_created_user

        # WHEN
        result = service.create("alice", "Password123!", "alice@test.com", is_admin=False)

        # THEN
        assert result == mock_created_user
        service.username_already_used.assert_called_once_with("alice")
        service.validate_password.assert_called_once_with("Password123!")
        mock_hash.assert_called_once_with("Password123!")
        mock_regular_cls.assert_called_once_with(
            "alice", "hashed_pwd", "alice@test.com", visitor_name="alice"
        )
        mock_dao.create.assert_called_once_with(mock_created_user)

    @patch("service.user_service.UserDao")
    @patch("service.user_service.User.hash_password", return_value="hashed_pwd")
    @patch("service.user_service.Administrator")
    def test_create_admin_user_success(
        self, mock_admin_cls, mock_hash, mock_user_dao_cls, service
    ):
        # GIVEN
        service.username_already_used = Mock(return_value=False)
        service.validate_password = Mock()

        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        mock_created_admin = Mock(spec=Administrator)
        mock_admin_cls.return_value = mock_created_admin

        # WHEN
        result = service.create("admin_bob", "AdminPass123!", "admin@test.com", is_admin=True)

        # THEN
        assert result == mock_created_admin
        mock_admin_cls.assert_called_once_with(
            "admin_bob", "hashed_pwd", "admin@test.com", admin_name="admin_bob"
        )
        mock_dao.create.assert_called_once_with(mock_created_admin)

    def test_create_raises_value_error_when_username_taken(self, service):
        # GIVEN
        service.username_already_used = Mock(return_value=True)

        # WHEN / THEN
        with pytest.raises(ValueError, match="username already used"):
            service.create("taken_user", "Valid1234!", "email@test.com")

        service.username_already_used.assert_called_once_with("taken_user")

    # =========================================================================
    # list_all & find_by_*
    # =========================================================================

    @patch("service.user_service.UserDao")
    def test_list_all_calls_dao(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        expected_users = [Mock(spec=User), Mock(spec=User)]
        mock_dao.list_all.return_value = expected_users

        # WHEN
        result = service.list_all()

        # THEN
        assert result == expected_users
        mock_dao.list_all.assert_called_once()

    @patch("service.user_service.UserDao")
    def test_find_by_username_calls_dao(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        expected_user = Mock(spec=User)
        mock_dao.find_by_username.return_value = expected_user

        # WHEN
        result = service.find_by_username("alice")

        # THEN
        assert result == expected_user
        mock_dao.find_by_username.assert_called_once_with("alice")

    @patch("service.user_service.UserDao")
    def test_find_by_id_calls_dao(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        expected_user = Mock(spec=User)
        mock_dao.find_by_id.return_value = expected_user

        # WHEN
        result = service.find_by_id(42)

        # THEN
        assert result == expected_user
        mock_dao.find_by_id.assert_called_once_with(42)

    # =========================================================================
    # login
    # =========================================================================

    @patch("service.user_service.UserDao")
    def test_login_success(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        mock_user = Mock(spec=User, id_user=10)
        mock_user.check_password.return_value = True
        mock_dao.find_by_username.return_value = mock_user

        # WHEN
        result = service.login("alice", "RightPassword123!")

        # THEN
        assert result == mock_user
        mock_dao.find_by_username.assert_called_once_with("alice")
        mock_user.check_password.assert_called_once_with("RightPassword123!")
        mock_dao.record_connection.assert_called_once_with(10)

    @patch("service.user_service.UserDao")
    def test_login_raises_value_error_when_user_not_found(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        mock_dao.find_by_username.return_value = None

        # WHEN / THEN
        with pytest.raises(ValueError, match="username or password incorrect, try again"):
            service.login("ghost_user", "AnyPassword123!")

        mock_dao.record_connection.assert_not_called()

    @patch("service.user_service.UserDao")
    def test_login_raises_value_error_when_password_incorrect(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        mock_user = Mock(spec=User)
        mock_user.check_password.return_value = False
        mock_dao.find_by_username.return_value = mock_user

        # WHEN / THEN
        with pytest.raises(ValueError, match="username or password incorrect, try again"):
            service.login("alice", "WrongPassword123!")

        mock_dao.record_connection.assert_not_called()

    # =========================================================================
    # update
    # =========================================================================

    @patch("service.user_service.UserDao")
    @patch("service.user_service.User.hash_password", return_value="new_hashed_pwd")
    def test_update_success_with_new_password(self, mock_hash, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        mock_dao.find_by_username.return_value = None

        service.validate_password = Mock()
        user_to_update = Mock(spec=User, id_user=1, username="alice", password="old_hashed_pwd")

        # WHEN
        result = service.update(user_to_update, new_password="NewSecret123!")

        # THEN
        assert result == user_to_update
        assert user_to_update.password == "new_hashed_pwd"
        service.validate_password.assert_called_once_with("NewSecret123!")
        mock_hash.assert_called_once_with("NewSecret123!")
        mock_dao.update.assert_called_once_with(user_to_update)

    @patch("service.user_service.UserDao")
    def test_update_success_without_password_change(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        user_to_update = Mock(spec=User, id_user=1, username="alice", password="current_pwd")
        mock_dao.find_by_username.return_value = user_to_update

        # WHEN
        result = service.update(user_to_update, new_password=None)

        # THEN
        assert result == user_to_update
        assert user_to_update.password == "current_pwd"
        mock_dao.update.assert_called_once_with(user_to_update)

    @patch("service.user_service.UserDao")
    def test_update_raises_value_error_when_username_conflict(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao

        other_user = Mock(spec=User, id_user=2, username="alice")
        mock_dao.find_by_username.return_value = other_user

        user_to_update = Mock(spec=User, id_user=1, username="alice")

        # WHEN / THEN
        with pytest.raises(ValueError, match="username already used, find something else"):
            service.update(user_to_update)

        mock_dao.update.assert_not_called()

    # =========================================================================
    # delete
    # =========================================================================

    @patch("service.user_service.UserDao")
    def test_delete_calls_dao(self, mock_user_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_user_dao_cls.return_value = mock_dao
        mock_dao.delete.return_value = True
        user_to_delete = Mock(spec=User)

        # WHEN
        result = service.delete(user_to_delete)

        # THEN
        assert result is True
        mock_dao.delete.assert_called_once_with(user_to_delete)