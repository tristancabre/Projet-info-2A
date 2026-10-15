import pytest
from unittest.mock import Mock, patch

from business_object.alert import Alert
from service.alert_service import AlertService, AlertNotFoundError


class TestAlertService:

    @pytest.fixture
    def service(self):
        """Instancie AlertService en mockant ses dépendances directes."""
        with patch("service.alert_service.AlertDao"), \
             patch("service.alert_service.NeoService"):
            srv = AlertService()
            srv.alert_dao = Mock()
            srv.neo_service = Mock()
            srv.notification_service = Mock()
            return srv

    # =========================================================================
    # _validate
    # =========================================================================

    def test_validate_raises_value_error_when_number_days_not_positive(self, service):
        # GIVEN
        invalid_days = 0

        # WHEN / THEN
        with pytest.raises(ValueError, match="number_days must be positive"):
            service._validate(
                number_days=invalid_days,
                earth_max_distance=100.0,
                min_diameter=None,
                min_speed=None,
                targeted_neo_id=None,
            )

    def test_validate_raises_value_error_when_no_criteria_provided(self, service):
        # GIVEN
        all_criteria_none = (None, None, None, None)

        # WHEN / THEN
        with pytest.raises(ValueError, match="An alert needs at least one parameter"):
            service._validate(5, *all_criteria_none)

    @pytest.mark.parametrize(
        "distance, diameter, speed, expected_message",
        [
            (-1.0, None, None, "earth_max_distance cannot be negative"),
            (None, -0.5, None, "min_diameter cannot be negative"),
            (None, None, -10.0, "min_speed cannot be negative"),
        ],
    )
    def test_validate_raises_value_error_when_criterion_is_negative(
        self, service, distance, diameter, speed, expected_message
    ):
        # GIVEN (Paramètres invalides négatifs)

        # WHEN / THEN
        with pytest.raises(ValueError, match=expected_message):
            service._validate(
                number_days=7,
                earth_max_distance=distance,
                min_diameter=diameter,
                min_speed=speed,
                targeted_neo_id=None,
            )

    # =========================================================================
    # _get_owned_alert
    # =========================================================================

    def test_get_owned_alert_success(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert, id_user=42)
        service.alert_dao.get_by_id.return_value = mock_alert

        # WHEN
        result = service._get_owned_alert(id_alert=1, id_user=42)

        # THEN
        assert result == mock_alert
        service.alert_dao.get_by_id.assert_called_once_with(1)

    def test_get_owned_alert_raises_error_when_alert_does_not_exist(self, service):
        # GIVEN
        service.alert_dao.get_by_id.return_value = None

        # WHEN / THEN
        with pytest.raises(AlertNotFoundError, match="Alert 999 not found"):
            service._get_owned_alert(id_alert=999, id_user=42)

    def test_get_owned_alert_raises_error_when_alert_owned_by_another_user(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert, id_user=99)
        service.alert_dao.get_by_id.return_value = mock_alert

        # WHEN / THEN
        with pytest.raises(AlertNotFoundError, match="Alert 1 not found"):
            service._get_owned_alert(id_alert=1, id_user=42)

    # =========================================================================
    # create_alert
    # =========================================================================

    @patch("service.alert_service.Alert")
    def test_create_alert_success(self, mock_alert_class, service):
        # GIVEN
        service._validate = Mock()
        service._check_alert_now = Mock()

        mock_alert_instance = Mock(spec=Alert)
        mock_alert_class.return_value = mock_alert_instance

        created_alert = Mock(spec=Alert)
        service.alert_dao.create.return_value = created_alert

        # WHEN
        result = service.create_alert(
            id_user=1,
            number_days=5,
            earth_max_distance=50000.0,
            min_diameter=120.0,
            min_speed=25.0,
            targeted_neo_id=123,
        )

        # THEN
        assert result == created_alert
        service._validate.assert_called_once_with(5, 50000.0, 120.0, 25.0, 123)
        mock_alert_class.assert_called_once_with(
            id_user=1,
            number_days=5,
            earth_max_distance=50000.0,
            min_diameter=120.0,
            min_speed=25.0,
            targeted_neo_id=123,
        )
        service.alert_dao.create.assert_called_once_with(mock_alert_instance)
        service._check_alert_now.assert_called_once_with(created_alert)

    # =========================================================================
    # get_alert & list_user_alerts
    # =========================================================================

    def test_get_alert_calls_get_owned_alert(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert)
        service._get_owned_alert = Mock(return_value=mock_alert)

        # WHEN
        result = service.get_alert(id_alert=10, id_user=5)

        # THEN
        assert result == mock_alert
        service._get_owned_alert.assert_called_once_with(10, 5)

    def test_list_user_alerts_returns_dao_result(self, service):
        # GIVEN
        expected_alerts = [Mock(spec=Alert), Mock(spec=Alert)]
        service.alert_dao.get_by_user.return_value = expected_alerts

        # WHEN
        result = service.list_user_alerts(id_user=3)

        # THEN
        assert result == expected_alerts
        service.alert_dao.get_by_user.assert_called_once_with(3)

    # =========================================================================
    # update_alert
    # =========================================================================

    def test_update_alert_success(self, service):
        # GIVEN
        service._validate = Mock()
        service._check_alert_now = Mock()

        mock_alert = Mock(spec=Alert)
        service._get_owned_alert = Mock(return_value=mock_alert)

        # WHEN
        result = service.update_alert(
            id_alert=1,
            id_user=10,
            number_days=14,
            earth_max_distance=2000.0,
            min_diameter=50.0,
            min_speed=15.0,
            targeted_neo_id=999,
        )

        # THEN
        assert result == mock_alert
        assert mock_alert.number_days == 14
        assert mock_alert.earth_max_distance == 2000.0
        assert mock_alert.min_diameter == 50.0
        assert mock_alert.min_speed == 15.0
        assert mock_alert.targeted_neo_id == 999
        service._validate.assert_called_once_with(14, 2000.0, 50.0, 15.0, 999)
        service._get_owned_alert.assert_called_once_with(1, 10)
        service.alert_dao.update.assert_called_once_with(mock_alert)
        service._check_alert_now.assert_called_once_with(mock_alert)

    # =========================================================================
    # set_active
    # =========================================================================

    def test_set_active_true_triggers_check_now(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert)
        service._get_owned_alert = Mock(return_value=mock_alert)
        service._check_alert_now = Mock()

        # WHEN
        result = service.set_active(id_alert=1, id_user=10, is_active=True)

        # THEN
        assert result == mock_alert
        assert mock_alert.is_active is True
        service.alert_dao.update.assert_called_once_with(mock_alert)
        service._check_alert_now.assert_called_once_with(mock_alert)

    def test_set_active_false_does_not_trigger_check_now(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert)
        service._get_owned_alert = Mock(return_value=mock_alert)
        service._check_alert_now = Mock()

        # WHEN
        result = service.set_active(id_alert=1, id_user=10, is_active=False)

        # THEN
        assert result == mock_alert
        assert mock_alert.is_active is False
        service.alert_dao.update.assert_called_once_with(mock_alert)
        service._check_alert_now.assert_not_called()

    # =========================================================================
    # delete_alert
    # =========================================================================

    def test_delete_alert_success(self, service):
        # GIVEN
        service._get_owned_alert = Mock()
        service.alert_dao.delete.return_value = True

        # WHEN
        result = service.delete_alert(id_alert=7, id_user=12)

        # THEN
        assert result is True
        service._get_owned_alert.assert_called_once_with(7, 12)
        service.alert_dao.delete.assert_called_once_with(7)

    # =========================================================================
    # _check_alert_now
    # =========================================================================

    def test_check_alert_now_ignores_inactive_alert(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert, is_active=False)

        # WHEN
        service._check_alert_now(mock_alert)

        # THEN
        service.neo_service.get_upcoming_neos.assert_not_called()
        service.notification_service.generate.assert_not_called()

    def test_check_alert_now_ignores_when_services_none(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert, is_active=True)
        service.notification_service = None

        # WHEN
        service._check_alert_now(mock_alert)

        # THEN
        service.neo_service.get_upcoming_neos.assert_not_called()

    def test_check_alert_now_generates_notifications_when_active(self, service):
        # GIVEN
        mock_alert = Mock(spec=Alert, is_active=True)
        mock_neos = [{"id": "neo1"}, {"id": "neo2"}]
        service.neo_service.get_upcoming_neos.return_value = mock_neos

        # WHEN
        service._check_alert_now(mock_alert)

        # THEN
        service.neo_service.get_upcoming_neos.assert_called_once()
        service.notification_service.generate.assert_called_once_with([mock_alert], mock_neos)