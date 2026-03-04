import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, timezone

from src.models.vehicle import VehicleType
from src.models.mission import MissionStatus, MissionStatusEvent
from src.services.mission_service import MissionService


def make_ambulance_mission(svc, pickup_time=None):
    t = pickup_time or datetime(2024, 6, 10, 10, 0, 0)
    m = svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    svc.update_status(m.id, MissionStatus.STARTED, "d1", "v1")
    svc.update_status(m.id, MissionStatus.ARRIVED_ON_SITE, "d1", "v1")
    return m


def test_auto_drop_not_triggered_before_delay():
    svc = MissionService()
    m = make_ambulance_mission(svc)
    # Arrived 5 minutes ago — below 20-minute default delay
    arrived_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    svc._auto_drop_timers[m.id] = arrived_time
    result = svc.check_auto_drop(m.id, current_time=datetime.now(timezone.utc))
    assert result is False
    assert m.status == MissionStatus.ARRIVED_ON_SITE


def test_auto_drop_triggered_after_delay():
    svc = MissionService()
    m = make_ambulance_mission(svc)
    # Arrived 25 minutes ago — above 20-minute default delay
    arrived_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    svc._auto_drop_timers[m.id] = arrived_time
    result = svc.check_auto_drop(m.id, current_time=datetime.now(timezone.utc))
    assert result is True
    assert m.status == MissionStatus.AUTO_DROPPED


def test_auto_drop_not_triggered_for_vsl():
    svc = MissionService()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m = svc.create_mission("p1", "d1", "v1", VehicleType.VSL, t, "Hospital", "reason", "pr1")
    svc.update_status(m.id, MissionStatus.STARTED, "d1", "v1")
    svc.update_status(m.id, MissionStatus.ARRIVED_ON_SITE, "d1", "v1")
    arrived_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    svc._auto_drop_timers[m.id] = arrived_time
    result = svc.check_auto_drop(m.id, current_time=datetime.now(timezone.utc))
    assert result is False
    assert m.status == MissionStatus.ARRIVED_ON_SITE


def test_auto_drop_not_triggered_if_already_dropped():
    svc = MissionService()
    m = make_ambulance_mission(svc)
    arrived_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    svc._auto_drop_timers[m.id] = arrived_time
    # Manually advance to PICKED_UP then DROPPED
    svc.update_status(m.id, MissionStatus.PICKED_UP, "d1", "v1")
    svc.update_status(m.id, MissionStatus.DROPPED, "d1", "v1")
    result = svc.check_auto_drop(m.id, current_time=datetime.now(timezone.utc))
    assert result is False
    assert m.status == MissionStatus.DROPPED


def test_auto_drop_records_automatic_flag():
    svc = MissionService()
    m = make_ambulance_mission(svc)
    arrived_time = datetime.now(timezone.utc) - timedelta(minutes=25)
    svc._auto_drop_timers[m.id] = arrived_time
    svc.check_auto_drop(m.id, current_time=datetime.now(timezone.utc))
    auto_event = next(
        (e for e in m.status_events if e.status == MissionStatus.AUTO_DROPPED), None
    )
    assert auto_event is not None
    assert auto_event.is_automatic is True
