from datetime import datetime, timedelta
from src.models import Mission, MissionStatus, TransportType
from src.database import db


def _finish_mission(app, sample_patient, sample_driver, sample_vehicle):
    with app.app_context():
        mission = Mission(
            patient_id=sample_patient,
            driver_id=sample_driver,
            vehicle_id=sample_vehicle,
            transport_type=TransportType.VSL,
            status=MissionStatus.FINISHED,
            pickup_address="1 rue Test",
            destination_address="Clinique Test",
            scheduled_pickup_time=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            distance_km=10.0,
        )
        db.session.add(mission)
        db.session.commit()
        return mission.id


def test_create_invoice(client, auth_headers, app, sample_patient, sample_driver, sample_vehicle):
    mission_id = _finish_mission(app, sample_patient, sample_driver, sample_vehicle)
    response = client.post("/api/invoices", json={
        "mission_id": mission_id,
        "amount_total": 45.5,
        "amount_amo": 36.4,
        "amount_amc": 5.0,
        "amount_patient": 4.1,
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["amount_total"] == 45.5
    assert data["invoice_number"].startswith("INV-")


def test_create_invoice_not_finished(client, auth_headers, sample_patient):
    from src.database import db
    from src.models import Mission, TransportType
    with client.application.app_context():
        mission = Mission(
            patient_id=sample_patient,
            transport_type=TransportType.TAXI,
            status=MissionStatus.PENDING,
            pickup_address="A",
            destination_address="B",
            scheduled_pickup_time=datetime.utcnow(),
        )
        db.session.add(mission)
        db.session.commit()
        mid = mission.id
    response = client.post("/api/invoices", json={"mission_id": mid}, headers=auth_headers)
    assert response.status_code == 422


def test_transmit_invoice(client, auth_headers, app, sample_patient, sample_driver, sample_vehicle):
    mission_id = _finish_mission(app, sample_patient, sample_driver, sample_vehicle)
    create_resp = client.post("/api/invoices", json={"mission_id": mission_id, "amount_total": 30},
                              headers=auth_headers)
    invoice_id = create_resp.get_json()["id"]
    response = client.put(f"/api/invoices/{invoice_id}/transmit", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["is_transmitted"] is True
