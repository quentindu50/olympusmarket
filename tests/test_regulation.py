import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta

from src.models.vehicle import VehicleType
from src.models.mission import MissionStatus
from src.services.mission_service import MissionService
from src.services.regulation_service import RegulationService


def make_services():
    ms = MissionService()
    rs = RegulationService(ms)
    return ms, rs


def test_dashboard_returns_data():
    ms, rs = make_services()
    today = datetime(2024, 6, 10, 10, 0, 0)
    ms.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, today, "Hospital", "reason", "pr1")
    ms.create_mission("p2", "d2", "v2", VehicleType.VSL, today, "Clinic", "check-up", "pr2")
    dashboard = rs.get_dashboard(date=today)
    assert "missions_today" in dashboard
    assert len(dashboard["missions_today"]) == 2
    assert "late_missions" in dashboard
    assert "ambulances_on_site" in dashboard


def test_create_mission_no_conflict():
    ms, rs = make_services()
    t = datetime(2024, 6, 10, 10, 0, 0)
    mission, errors = rs.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    assert errors == []
    assert mission is not None
    assert mission.driver_id == "d1"


def test_create_mission_vehicle_conflict():
    ms, rs = make_services()
    t = datetime(2024, 6, 10, 10, 0, 0)
    # First mission
    rs.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    # Second mission with same vehicle at the same time
    mission2, errors = rs.create_mission("p2", "d2", "v1", VehicleType.AMBULANCE, t, "Clinic", "reason", "pr1")
    assert mission2 is None
    assert len(errors) > 0
    assert any("v1" in e for e in errors)


def test_create_mission_driver_conflict():
    ms, rs = make_services()
    t = datetime(2024, 6, 10, 10, 0, 0)
    rs.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    mission2, errors = rs.create_mission("p2", "d1", "v2", VehicleType.AMBULANCE, t, "Clinic", "reason", "pr1")
    assert mission2 is None
    assert any("d1" in e for e in errors)


def test_get_real_time_tracking():
    ms, rs = make_services()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m = ms.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    ms.update_status(m.id, MissionStatus.STARTED, "d1", "v1", gps_lat=48.85, gps_lon=2.35)
    tracking = rs.get_real_time_tracking(m.id)
    assert tracking["mission_id"] == m.id
    assert tracking["current_status"] == MissionStatus.STARTED.value
    assert tracking["last_gps_position"] is not None
    assert tracking["last_gps_position"]["latitude"] == 48.85
    assert len(tracking["status_events"]) == 2
