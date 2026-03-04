import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
import pytest

from src.models.vehicle import VehicleType
from src.models.mission import MissionStatus
from src.services.mission_service import MissionService


def make_service():
    return MissionService()


def base_time():
    return datetime(2024, 6, 10, 10, 0, 0)


def test_create_mission():
    svc = make_service()
    t = base_time()
    mission = svc.create_mission(
        patient_id="p1",
        driver_id="d1",
        vehicle_id="v1",
        vehicle_type=VehicleType.AMBULANCE,
        pickup_time=t,
        destination="Hospital A",
        reason="dialysis",
        prescriber_id="pr1",
    )
    assert mission.id is not None
    assert mission.patient_id == "p1"
    assert mission.driver_id == "d1"
    assert mission.vehicle_id == "v1"
    assert mission.vehicle_type == VehicleType.AMBULANCE
    assert mission.status == MissionStatus.PENDING
    assert len(mission.status_events) == 1
    assert mission.status_events[0].status == MissionStatus.PENDING


def test_status_transitions():
    svc = make_service()
    t = base_time()
    m = svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")

    svc.update_status(m.id, MissionStatus.STARTED, "d1", "v1")
    assert m.status == MissionStatus.STARTED

    svc.update_status(m.id, MissionStatus.ARRIVED_ON_SITE, "d1", "v1")
    assert m.status == MissionStatus.ARRIVED_ON_SITE

    svc.update_status(m.id, MissionStatus.PICKED_UP, "d1", "v1")
    assert m.status == MissionStatus.PICKED_UP

    svc.update_status(m.id, MissionStatus.DROPPED, "d1", "v1")
    assert m.status == MissionStatus.DROPPED

    svc.update_status(m.id, MissionStatus.COMPLETED, "d1", "v1")
    assert m.status == MissionStatus.COMPLETED
    assert len(m.status_events) == 6  # PENDING + 5 transitions


def test_invalid_status_transition():
    svc = make_service()
    t = base_time()
    m = svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    with pytest.raises(ValueError):
        svc.update_status(m.id, MissionStatus.COMPLETED, "d1", "v1")


def test_get_missions_for_driver():
    svc = make_service()
    t = base_time()
    m = svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    missions = svc.get_missions_for_driver("d1")
    assert m in missions

    # Simulate an old completed mission
    m2 = svc.create_mission("p2", "d1", "v2", VehicleType.VSL, t, "Clinic", "reason", "pr1")
    # Manually push all its events to 25h ago and complete it
    old_time = datetime.utcnow() - timedelta(hours=25)
    for e in m2.status_events:
        e.timestamp = old_time
    m2.status = MissionStatus.COMPLETED
    from src.models.mission import MissionStatusEvent
    completed_event = MissionStatusEvent(
        status=MissionStatus.COMPLETED,
        timestamp=old_time,
        driver_id="d1",
        vehicle_id="v2",
    )
    m2.status_events.append(completed_event)

    missions = svc.get_missions_for_driver("d1")
    assert m in missions
    assert m2 not in missions


def test_vehicle_conflict_detection():
    svc = make_service()
    t = base_time()
    svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    # Same vehicle, overlapping time
    end = t + timedelta(hours=1)
    conflict = svc.check_vehicle_conflict("v1", t, end)
    assert conflict is True


def test_driver_conflict_detection():
    svc = make_service()
    t = base_time()
    svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital", "reason", "pr1")
    end = t + timedelta(hours=1)
    conflict = svc.check_driver_conflict("d1", t, end)
    assert conflict is True
