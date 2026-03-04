import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime

from src.models.vehicle import VehicleType
from src.models.mission import MissionStatus, MissionStatusEvent
from src.models.patient import Patient
from src.services.mission_service import MissionService
from src.services.billing_service import BillingService, BASE_RATE_PER_KM


def make_completed_mission(svc, pickup_time):
    m = svc.create_mission(
        "p1", "d1", "v1", VehicleType.AMBULANCE, pickup_time, "Hospital", "reason", "pr1"
    )
    m.transport_document_present = True
    m.prescription_validated = True
    m.distance_km = 10.0
    # Add terminal status event
    m.status_events.append(
        MissionStatusEvent(
            status=MissionStatus.COMPLETED,
            timestamp=pickup_time,
            driver_id="d1",
            vehicle_id="v1",
        )
    )
    m.status = MissionStatus.COMPLETED
    return m


def make_patient():
    return Patient(
        id="p1",
        last_name="Martin",
        first_name="Sophie",
        social_security_number="123456789",
        amo="AMO123",
        postal_code="75001",
        city="Paris",
    )


def test_billing_ready_when_all_present():
    svc = MissionService()
    bsvc = BillingService()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m = make_completed_mission(svc, t)
    ready, missing = bsvc.check_mission_ready_for_billing(m)
    assert ready is True
    assert missing == []


def test_billing_not_ready_missing_transport_doc():
    svc = MissionService()
    bsvc = BillingService()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m = make_completed_mission(svc, t)
    m.transport_document_present = False
    ready, missing = bsvc.check_mission_ready_for_billing(m)
    assert ready is False
    assert "transport_document" in missing


def test_billing_not_ready_missing_prescription():
    svc = MissionService()
    bsvc = BillingService()
    t = datetime(2024, 6, 10, 10, 0, 0)
    m = make_completed_mission(svc, t)
    m.prescription_validated = False
    ready, missing = bsvc.check_mission_ready_for_billing(m)
    assert ready is False
    assert "prescription" in missing


def test_night_surcharge():
    svc = MissionService()
    bsvc = BillingService()
    # 23:00 is night time
    t = datetime(2024, 6, 10, 23, 0, 0)
    m = make_completed_mission(svc, t)
    patient = make_patient()
    invoice = bsvc.calculate_invoice(m, patient, distance_km=10.0)
    assert invoice.has_night_surcharge is True
    assert invoice.surcharge_amount > 0


def test_sunday_surcharge():
    svc = MissionService()
    bsvc = BillingService()
    # Find a Sunday: 2024-06-09 is a Sunday
    t = datetime(2024, 6, 9, 10, 0, 0)
    assert t.weekday() == 6, "Expected Sunday"
    m = make_completed_mission(svc, t)
    patient = make_patient()
    invoice = bsvc.calculate_invoice(m, patient, distance_km=10.0)
    assert invoice.has_sunday_surcharge is True
    assert invoice.surcharge_amount > 0


def test_no_surcharge_day_mission():
    svc = MissionService()
    bsvc = BillingService()
    # Monday at 10:00
    t = datetime(2024, 6, 10, 10, 0, 0)
    assert t.weekday() == 0, "Expected Monday"
    m = make_completed_mission(svc, t)
    patient = make_patient()
    invoice = bsvc.calculate_invoice(m, patient, distance_km=10.0)
    assert invoice.has_night_surcharge is False
    assert invoice.has_sunday_surcharge is False
    assert invoice.surcharge_amount == 0.0


def test_calculate_invoice_base():
    svc = MissionService()
    bsvc = BillingService()
    t = datetime(2024, 6, 10, 10, 0, 0)  # Monday daytime
    m = make_completed_mission(svc, t)
    patient = make_patient()
    invoice = bsvc.calculate_invoice(m, patient, distance_km=10.0)
    assert invoice.base_amount == 10.0 * BASE_RATE_PER_KM
    assert invoice.total_amount == invoice.base_amount  # no surcharges
