import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

from src.models.driver import Driver
from src.models.vehicle import VehicleType
from src.models.message import Message
from src.services.mission_service import MissionService


def test_driver_identifier():
    driver = Driver(id="d1", first_name="Jean", last_name="Dupont", vehicle_type=VehicleType.AMBULANCE)
    assert driver.identifier == "DJ"


def test_driver_identifier_various():
    driver = Driver(id="d2", first_name="Marie", last_name="Curie", vehicle_type=VehicleType.VSL)
    assert driver.identifier == "CM"


def test_driver_mission_list():
    svc = MissionService()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m1 = svc.create_mission("p1", "d1", "v1", VehicleType.AMBULANCE, t, "Hospital A", "reason", "pr1")
    m2 = svc.create_mission("p2", "d1", "v2", VehicleType.VSL, t, "Clinic B", "reason", "pr2")
    svc.create_mission("p3", "d2", "v3", VehicleType.TAXI, t, "Home", "reason", "pr3")

    missions = svc.get_missions_for_driver("d1")
    ids = [m.id for m in missions]
    assert m1.id in ids
    assert m2.id in ids
    # d2 mission should not appear
    assert len([m for m in missions if m.driver_id != "d1"]) == 0


def test_message_acknowledgement():
    msg = Message(
        id="msg1",
        sender_id="d1",
        recipient_id="reg1",
        content="En route",
        sent_at=datetime.utcnow(),
    )
    assert msg.acknowledged is False
    assert msg.acknowledged_at is None

    # Acknowledge the message
    msg.acknowledged = True
    msg.acknowledged_at = datetime.utcnow()

    assert msg.acknowledged is True
    assert msg.acknowledged_at is not None
