import pytest
from unittest.mock import Mock, patch

from business_object.alert import Alert
from business_object.neo import Neo
from business_object.notification import Notification
from service.notification_service import NotificationService


class TestNotificationService:

    @pytest.fixture
    def service(self):
        """Instancie NotificationService en mockant NotificationDao."""
        with patch("service.notification_service.NotificationDao"):
            srv = NotificationService()
            srv.notification_dao = Mock()
            return srv

    # =========================================================================
    # generate
    # =========================================================================

    @patch("service.notification_service.Notification.from_alert_and_neo")
    def test_generate_creates_and_saves_notifications_for_matching_neos(
        self, mock_from_alert_and_neo, service
    ):
        # GIVEN
        service.notification_dao.get_sent_pairs.return_value = set()

        alert1 = Mock(spec=Alert, id_alert=1)
        alert1.check_neo.side_effect = lambda neo: neo.id_neo == 100

        neo1 = Mock(spec=Neo, id_neo=100)
        neo2 = Mock(spec=Neo, id_neo=200)

        created_notif = Mock(spec=Notification)
        mock_from_alert_and_neo.return_value = created_notif

        # WHEN
        result = service.generate(alerts=[alert1], neos=[neo1, neo2])

        # THEN
        assert result == [created_notif]
        service.notification_dao.get_sent_pairs.assert_called_once()
        alert1.check_neo.assert_any_call(neo1)
        alert1.check_neo.assert_any_call(neo2)
        mock_from_alert_and_neo.assert_called_once_with(alert1, neo1)
        service.notification_dao.save_many.assert_called_once_with([created_notif])

    @patch("service.notification_service.Notification.from_alert_and_neo")
    def test_generate_skips_already_sent_pairs(
        self, mock_from_alert_and_neo, service
    ):
        # GIVEN
        service.notification_dao.get_sent_pairs.return_value = {(1, 100)}

        alert1 = Mock(spec=Alert, id_alert=1)
        neo1 = Mock(spec=Neo, id_neo=100)

        # WHEN
        result = service.generate(alerts=[alert1], neos=[neo1])

        # THEN
        assert result == []
        alert1.check_neo.assert_not_called()
        mock_from_alert_and_neo.assert_not_called()
        service.notification_dao.save_many.assert_not_called()

    @patch("service.notification_service.Notification.from_alert_and_neo")
    def test_generate_does_not_call_save_many_when_no_notifications(
        self, mock_from_alert_and_neo, service
    ):
        # GIVEN
        service.notification_dao.get_sent_pairs.return_value = set()

        alert1 = Mock(spec=Alert, id_alert=1)
        alert1.check_neo.return_value = False
        neo1 = Mock(spec=Neo, id_neo=100)

        # WHEN
        result = service.generate(alerts=[alert1], neos=[neo1])

        # THEN
        assert result == []
        mock_from_alert_and_neo.assert_not_called()
        service.notification_dao.save_many.assert_not_called()

    # =========================================================================
    # get_user_notifications
    # =========================================================================

    def test_get_user_notifications_delegates_to_dao(self, service):
        # GIVEN
        expected_notifications = [Mock(spec=Notification), Mock(spec=Notification)]
        service.notification_dao.get_by_user.return_value = expected_notifications

        # WHEN
        result = service.get_user_notifications(id_user=42)

        # THEN
        assert result == expected_notifications
        service.notification_dao.get_by_user.assert_called_once_with(42)

    # =========================================================================
    # check_all_alerts
    # =========================================================================

    def test_check_all_alerts_calls_dependencies_and_returns_count(self, service):
        # GIVEN
        mock_alert_dao = Mock()
        mock_neo_service = Mock()

        mock_alerts = [Mock(spec=Alert), Mock(spec=Alert)]
        mock_neos = [Mock(spec=Neo), Mock(spec=Neo)]

        mock_alert_dao.get_all_active.return_value = mock_alerts
        mock_neo_service.get_upcoming_neos.return_value = mock_neos

        generated_notifications = [Mock(spec=Notification), Mock(spec=Notification), Mock(spec=Notification)]
        service.generate = Mock(return_value=generated_notifications)

        # WHEN
        result = service.check_all_alerts(alert_dao=mock_alert_dao, neo_service=mock_neo_service)

        # THEN
        assert result == 3
        mock_neo_service.get_upcoming_neos.assert_called_once()
        mock_alert_dao.get_all_active.assert_called_once()
        service.generate.assert_called_once_with(mock_alerts, mock_neos)