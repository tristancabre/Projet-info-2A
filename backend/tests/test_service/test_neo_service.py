import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from business_object.neo import Neo
from service.neo_service import NeoService


class TestNeoService:

    @pytest.fixture
    def service(self):
        return NeoService()

    # =========================================================================
    # search_by_id
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_search_by_id_returns_neo(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        expected_neo = Mock(spec=Neo)
        mock_dao.find_by_id.return_value = expected_neo

        # WHEN
        result = service.search_by_id(id_neo=42)

        # THEN
        assert result == expected_neo
        mock_dao.find_by_id.assert_called_once_with(42)

    @patch("service.neo_service.NeoDao")
    def test_search_by_id_returns_none_when_not_found(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.find_by_id.return_value = None

        # WHEN
        result = service.search_by_id(id_neo=999)

        # THEN
        assert result is None
        mock_dao.find_by_id.assert_called_once_with(999)

    # =========================================================================
    # search_by_name
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_search_by_name_strips_input_and_calls_dao(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        expected_list = [Mock(spec=Neo)]
        mock_dao.find_by_name.return_value = expected_list

        # WHEN
        result = service.search_by_name("  Apophis  ")

        # THEN
        assert result == expected_list
        mock_dao.find_by_name.assert_called_once_with("Apophis")

    # =========================================================================
    # find_all
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_find_all_calls_list_all(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        expected_neos = [Mock(spec=Neo), Mock(spec=Neo)]
        mock_dao.list_all.return_value = expected_neos

        # WHEN
        result = service.find_all()

        # THEN
        assert result == expected_neos
        mock_dao.list_all.assert_called_once()

    # =========================================================================
    # search_by_diameter & search_by_speed & search_by_closest_day
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_search_by_diameter_calls_dao(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        expected_neos = [Mock(spec=Neo)]
        mock_dao.find_by_diameter.return_value = expected_neos

        # WHEN
        result = service.search_by_diameter(min_diameter=10.0, max_diameter=50.0)

        # THEN
        assert result == expected_neos
        mock_dao.find_by_diameter.assert_called_once_with(10.0, 50.0)

    @patch("service.neo_service.NeoDao")
    def test_search_by_speed_calls_dao(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        expected_neos = [Mock(spec=Neo)]
        mock_dao.find_by_speed.return_value = expected_neos

        # WHEN
        result = service.search_by_speed(min_speed=5.0, max_speed=20.0)

        # THEN
        assert result == expected_neos
        mock_dao.find_by_speed.assert_called_once_with(5.0, 20.0)

    @patch("service.neo_service.NeoDao")
    def test_search_by_closest_day_calls_dao(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        target_day = date(2026, 10, 20)
        expected_neos = [Mock(spec=Neo)]
        mock_dao.find_by_closest_day.return_value = expected_neos

        # WHEN
        result = service.search_by_closest_day(target_day)

        # THEN
        assert result == expected_neos
        mock_dao.find_by_closest_day.assert_called_once_with(target_day)

    # =========================================================================
    # get_approaching
    # =========================================================================

    @patch("service.neo_service.date")
    @patch("service.neo_service.NeoDao")
    def test_get_approaching_queries_expected_interval(self, mock_neo_dao_cls, mock_date, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_date.today.return_value = date(2026, 10, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

        expected_neos = [Mock(spec=Neo)]
        mock_dao.find_between_days.return_value = expected_neos

        # WHEN
        result = service.get_approaching(days=5)

        # THEN
        assert result == expected_neos
        mock_dao.find_between_days.assert_called_once_with(
            date(2026, 10, 15),
            date(2026, 10, 20),
        )

    # =========================================================================
    # create
    # =========================================================================

    @patch("service.neo_service.Neo")
    @patch("service.neo_service.NeoDao")
    def test_create_success(self, mock_neo_dao_cls, mock_neo_cls, service):
        # GIVEN
        mock_neo_dao_cls.calcul_rarity.return_value = "COMMON"
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.create.return_value = True

        mock_neo_instance = Mock(spec=Neo)
        mock_neo_cls.return_value = mock_neo_instance

        # WHEN
        result = service.create(
            name="Apophis",
            diameter=340.0,
            distance=31000.0,
            speed=30.0,
            closest_day=date(2029, 4, 13),
        )

        # THEN
        assert result == mock_neo_instance
        mock_neo_dao_cls.calcul_rarity.assert_called_once_with(31000.0, 340.0)
        mock_neo_cls.assert_called_once_with(
            name="Apophis",
            diameter=340.0,
            distance=31000.0,
            closest_day=date(2029, 4, 13),
            speed=30.0,
            rarity="COMMON",
        )
        mock_dao.create.assert_called_once_with(mock_neo_instance)

    @patch("service.neo_service.Neo")
    @patch("service.neo_service.NeoDao")
    def test_create_returns_none_when_dao_returns_false(self, mock_neo_dao_cls, mock_neo_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.create.return_value = False
        mock_neo_cls.return_value = Mock(spec=Neo)

        # WHEN
        result = service.create("Apophis", 340.0, 31000.0, 30.0, date(2029, 4, 13))

        # THEN
        assert result is None

    @patch("service.neo_service.logger")
    @patch("service.neo_service.Neo")
    @patch("service.neo_service.NeoDao")
    def test_create_catches_exception_and_logs(self, mock_neo_dao_cls, mock_neo_cls, mock_logger, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.create.side_effect = Exception("DB error")
        mock_neo_cls.return_value = Mock(spec=Neo)

        # WHEN
        result = service.create("Apophis", 340.0, 31000.0, 30.0, date(2029, 4, 13))

        # THEN
        assert result is None
        mock_logger.exception.assert_called_once_with("Error while creating neo")

    # =========================================================================
    # update
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_update_success(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_neo_dao_cls.calcul_rarity.return_value = "RARE"
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.update.return_value = True

        mock_neo = Mock(spec=Neo, distance=5000.0, diameter=120.0)

        # WHEN
        result = service.update(mock_neo)

        # THEN
        assert result == mock_neo
        assert mock_neo.rarity == "RARE"
        mock_neo_dao_cls.calcul_rarity.assert_called_once_with(5000.0, 120.0)
        mock_dao.update.assert_called_once_with(mock_neo)

    @patch("service.neo_service.NeoDao")
    def test_update_returns_none_when_dao_fails(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.update.return_value = False
        mock_neo = Mock(spec=Neo, distance=5000.0, diameter=120.0)

        # WHEN
        result = service.update(mock_neo)

        # THEN
        assert result is None

    @patch("service.neo_service.logger")
    @patch("service.neo_service.NeoDao")
    def test_update_catches_exception_and_logs(self, mock_neo_dao_cls, mock_logger, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.update.side_effect = Exception("DB update failed")
        mock_neo = Mock(spec=Neo, distance=5000.0, diameter=120.0)

        # WHEN
        result = service.update(mock_neo)

        # THEN
        assert result is None
        mock_logger.exception.assert_called_once_with("Error while updating neo")

    # =========================================================================
    # delete
    # =========================================================================

    @patch("service.neo_service.NeoDao")
    def test_delete_success(self, mock_neo_dao_cls, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.delete.return_value = True
        mock_neo = Mock(spec=Neo)

        # WHEN
        result = service.delete(mock_neo)

        # THEN
        assert result is True
        mock_dao.delete.assert_called_once_with(mock_neo)

    @patch("service.neo_service.logger")
    @patch("service.neo_service.NeoDao")
    def test_delete_catches_exception_and_logs(self, mock_neo_dao_cls, mock_logger, service):
        # GIVEN
        mock_dao = Mock()
        mock_neo_dao_cls.return_value = mock_dao
        mock_dao.delete.side_effect = Exception("Delete failed")
        mock_neo = Mock(spec=Neo)

        # WHEN
        result = service.delete(mock_neo)

        # THEN
        assert result is False
        mock_logger.exception.assert_called_once_with("Error while deleting neo")

    # =========================================================================
    # refresh_from_nasa
    # =========================================================================

    @patch("service.neo_service.NasaDao")
    @patch("service.neo_service.NeoDao")
    def test_refresh_from_nasa_calls_daos_and_returns_count(
        self, mock_neo_dao_cls, mock_nasa_dao_cls, service
    ):
        # GIVEN
        mock_nasa_dao = Mock()
        mock_nasa_dao_cls.return_value = mock_nasa_dao
        raw_nasa_data = [{"id": 1, "name": "Asteroid"}]
        mock_nasa_dao.recuperer_donnees_nasa.return_value = raw_nasa_data

        mock_neo_dao = Mock()
        mock_neo_dao_cls.return_value = mock_neo_dao
        mock_neo_dao.inserer_donnees_sql.return_value = 15

        # WHEN
        result = service.refresh_from_nasa()

        # THEN
        assert result == 15
        mock_nasa_dao.recuperer_donnees_nasa.assert_called_once()
        mock_neo_dao.inserer_donnees_sql.assert_called_once_with(raw_nasa_data)