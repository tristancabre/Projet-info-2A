import os
from unittest.mock import patch

import psycopg2
import pytest

from business_object.alert import Alert
from dao.alert_dao import AlertDao
from utils.reset_database import ResetDatabase

# Adding two cases to tthe test to help organise all of it
ID_USER = 1
ID_USER_WITHOUT_ALERT = 999


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize test data"""
    with patch.dict(os.environ, {"SCHEMA": "project_test_dao"}):
        ResetDatabase().run(test_dao=True)
        yield


# we havent created tests yet so : exemple to use is below


def make_alert(id_user=ID_USER, is_active=True, **kwargs) -> Alert:
    """Build an Alert with sensible defaults"""
    params = dict(
        id_user=id_user,
        number_days=7,
        earth_max_distance=1_000_000.0,
        min_diameter=50.0,
        min_speed=10.0,
        targeted_neo_id="2000433",
        is_active=is_active,
    )
    params.update(kwargs)
    return Alert(**params)


def test_create_ok():
    """Successfully create an alert on a Neo"""

    # GIVEN
    alert = make_alert()

    # WHEN
    created = AlertDao().create(alert)

    # THEN
    assert created is alert
    assert created.id_alert is not None
    assert created.id_alert > 0


def test_create_ko():
    """Fail to create an alert (missing user)"""

    # GIVEN
    alert = make_alert(id_user=None)

    # WHEN / THEN
    with pytest.raises(psycopg2.Error):
        AlertDao().create(alert)


def test_get_by_id_existing():
    """Find an alert by an existing id"""

    # GIVEN
    alert = AlertDao().create(make_alert(number_days=3, min_speed=42.5))

    # WHEN
    alert_found = AlertDao().get_by_id(alert.id_alert)

    # THEN
    assert isinstance(alert_found, Alert)
    assert alert_found.id_alert == alert.id_alert
    assert alert_found.id_user == ID_USER
    assert alert_found.number_days == 3
    assert alert_found.min_speed == 42.5
    assert alert_found.is_active is True


def test_get_by_id_non_existing():
    """Find an alert by a non-existing id"""

    # GIVEN
    id_alert = 111111111

    # WHEN
    found = AlertDao().get_by_id(id_alert)

    # THEN
    assert found is None


# ---------- get_by_user ----------


def test_get_by_user_existing():
    """Verify the method get by user returns the alerts of a user"""

    # GIVEN
    a1 = AlertDao().create(make_alert())
    a2 = AlertDao().create(make_alert(is_active=False))

    # WHEN
    alerts = AlertDao().get_by_user(ID_USER)  # The one with alerts already

    # THEN
    assert isinstance(alerts, list)
    assert all(isinstance(a, Alert) for a in alerts)
    assert all(a.id_user == ID_USER for a in alerts)
    ids = [a.id_alert for a in alerts]
    assert a1.id_alert in ids
    assert a2.id_alert in ids


def test_get_by_user_no_alert():
    """A user without alerts gets an empty list"""

    # GIVEN
    id_user = 999  # the id of the user that has no alerts yet.

    # WHEN
    alerts = AlertDao().get_by_user(id_user)

    # THEN
    assert alerts == []


def test_get_all_active():
    """Only active alerts are returned"""

    # GIVEN
    active = AlertDao().create(make_alert(is_active=True))
    inactive = AlertDao().create(make_alert(is_active=False))

    # WHEN
    alerts = AlertDao().get_all_active()

    # THEN
    assert isinstance(alerts, list)
    assert all(isinstance(a, Alert) for a in alerts)
    assert all(a.is_active for a in alerts)
    ids = [a.id_alert for a in alerts]
    assert active.id_alert in ids
    assert inactive.id_alert not in ids


def test_update_ok():
    """Update an alert successfully"""

    # GIVEN
    alert = AlertDao().create(make_alert())
    alert.number_days = 30
    alert.min_diameter = 200.0
    alert.is_active = False

    # WHEN
    update_ok = AlertDao().update(alert)

    # THEN
    assert update_ok
    reloaded = AlertDao().get_by_id(alert.id_alert)
    assert reloaded.number_days == 30
    assert reloaded.min_diameter == 200.0
    assert reloaded.is_active is False


def test_update_ko():
    """Fail to update an alert, the id of the alert is not recognised"""

    # GIVEN
    alert = make_alert()
    alert.id_alert = 9999999999999  # unknown

    # WHEN
    update_ok = AlertDao().update(alert)

    # THEN
    assert not update_ok


def test_delete_ok():
    """Delete an alert ok"""

    # GIVEN
    alert = AlertDao().create(make_alert())

    # WHEN
    delete_ok = AlertDao().delete(alert.id_alert)

    # THEN
    assert delete_ok
    assert AlertDao().get_by_id(alert.id_alert) is None


def test_delete_ko():
    """Fail to delete an alert : cannot find the alert"""

    # GIVEN
    id_alert = 9999999999999

    # WHEN
    delete_ok = AlertDao().delete(id_alert)

    # THEN
    assert not delete_ok


if __name__ == "__main__":
    pytest.main([__file__])
