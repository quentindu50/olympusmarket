# Main application for the ambulance/medical transport management system

from datetime import datetime

from src.models.vehicle import VehicleType
from src.models.patient import Patient
from src.models.prescriber import Prescriber, PrescriberType
from src.models.driver import Driver
from src.models.mission import MissionStatus
from src.services.mission_service import MissionService
from src.services.billing_service import BillingService
from src.services.regulation_service import RegulationService
from src.services.alert_service import AlertService, AlertType
from src.services.document_service import DocumentService
from src.models.document import DocumentType


def main():
    print("=== Ambulance Transport Management System ===")

    # Setup services
    mission_svc = MissionService()
    billing_svc = BillingService()
    regulation_svc = RegulationService(mission_svc)
    alert_svc = AlertService()
    doc_svc = DocumentService()

    # Create sample data
    patient = Patient(
        id="p1",
        last_name="Dupont",
        first_name="Jean",
        social_security_number="1234567890123",
        amo="AMO001",
        postal_code="75001",
        city="Paris",
    )
    prescriber = Prescriber(
        id="pr1",
        type=PrescriberType.DOCTOR,
        name="Dr. Martin",
        address="1 rue de la Paix, Paris",
        phone="0123456789",
    )
    driver = Driver(id="d1", first_name="Pierre", last_name="Leblanc", vehicle_type=VehicleType.AMBULANCE)
    print(f"Driver identifier: {driver.identifier}")

    # Create a mission via regulation
    pickup_time = datetime(2024, 6, 10, 9, 0, 0)
    mission, errors = regulation_svc.create_mission(
        patient_id=patient.id,
        driver_id=driver.id,
        vehicle_id="v1",
        vehicle_type=VehicleType.AMBULANCE,
        pickup_time=pickup_time,
        destination="Hôpital Lariboisière",
        reason="dialysis",
        prescriber_id=prescriber.id,
    )
    if errors:
        print(f"Mission creation failed: {errors}")
        return
    print(f"Mission created: {mission.id}, status={mission.status.value}")

    # Progress through statuses
    mission_svc.update_status(mission.id, MissionStatus.STARTED, driver.id, "v1")
    mission_svc.update_status(mission.id, MissionStatus.ARRIVED_ON_SITE, driver.id, "v1", gps_lat=48.88, gps_lon=2.36)
    mission_svc.update_status(mission.id, MissionStatus.PICKED_UP, driver.id, "v1")
    mission_svc.update_status(mission.id, MissionStatus.DROPPED, driver.id, "v1")
    mission_svc.update_status(mission.id, MissionStatus.COMPLETED, driver.id, "v1")
    print(f"Mission completed: status={mission.status.value}")

    # Add documents
    doc_svc.add_document(DocumentType.BON_TRANSPORT, patient_id=patient.id, mission_id=mission.id)
    doc_svc.add_document(DocumentType.ORDONNANCE, patient_id=patient.id, mission_id=mission.id)
    complete, missing = doc_svc.check_mission_documents_complete(mission.id)
    print(f"Documents complete: {complete}, missing: {missing}")

    # Billing
    mission.transport_document_present = True
    mission.prescription_validated = True
    mission.distance_km = 12.5
    ready, missing_billing = billing_svc.check_mission_ready_for_billing(mission)
    print(f"Billing ready: {ready}")
    if ready:
        invoice = billing_svc.calculate_invoice(mission, patient, distance_km=12.5)
        print(f"Invoice: base={invoice.base_amount:.2f}€, surcharge={invoice.surcharge_amount:.2f}€, total={invoice.total_amount:.2f}€")

    # Real-time tracking
    tracking = regulation_svc.get_real_time_tracking(mission.id)
    print(f"Tracking: status={tracking['current_status']}, events={len(tracking['status_events'])}")

    # Alert example
    alert = alert_svc.create_alert(AlertType.MISSING_DOCUMENT, "Missing transport document", mission_id=mission.id)
    alert_svc.resolve_alert(alert.id)
    print(f"Open alerts: {len(alert_svc.get_open_alerts())}")


if __name__ == "__main__":
    main()