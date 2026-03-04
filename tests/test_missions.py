from datetime import datetime, timedelta
from src.models import Mission, MissionStatus, TransportType
from src.database import db
from src.services.mission_service import (
    update_mission_status,
    check_ambulance_auto_drop,
    get_dashboard_stats,
)


def _create_mission(client, auth_headers, patient_id, driver_id=None, vehicle_id=None):
    pickup_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    return client.post("/api/missions", json={
        "patient_id": patient_id,
        "driver_id": driver_id,
        "vehicle_id": vehicle_id,
        "transport_type": "ambulance",
        "pickup_address": "10 rue de la Paix, Paris",
        "destination_address": "Hôpital Lariboisière, Paris",
        "scheduled_pickup_time": pickup_time,
        "reason": "Dialyse",
        "distance_km": 15.5,
    }, headers=auth_headers)


def test_create_mission(client, auth_headers, sample_patient):
    response = _create_mission(client, auth_headers, sample_patient)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "pending"
    assert data["transport_type"] == "ambulance"


def test_create_mission_missing_fields(client, auth_headers, sample_patient):
    response = client.post("/api/missions", json={"patient_id": sample_patient}, headers=auth_headers)
    assert response.status_code == 400


def test_list_missions(client, auth_headers, sample_patient):
    _create_mission(client, auth_headers, sample_patient)
    response = client.get("/api/missions", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.get_json()) >= 1


def test_status_transition_valid(client, auth_headers, sample_patient, sample_driver, sample_vehicle):
    resp = _create_mission(client, auth_headers, sample_patient, sample_driver, sample_vehicle)
    mission_id = resp.get_json()["id"]

    for status in ["assigned", "started", "on_site", "patient_onboard", "dropped", "finished"]:
        r = client.put(f"/api/missions/{mission_id}/status", json={"status": status}, headers=auth_headers)
        assert r.status_code == 200, f"Failed at {status}: {r.get_json()}"


def test_status_transition_invalid(client, auth_headers, sample_patient):
    resp = _create_mission(client, auth_headers, sample_patient)
    mission_id = resp.get_json()["id"]
    r = client.put(f"/api/missions/{mission_id}/status", json={"status": "finished"}, headers=auth_headers)
    assert r.status_code == 422


def test_ambulance_auto_drop(app, sample_patient, sample_driver, sample_vehicle):
    with app.app_context():
        mission = Mission(
            patient_id=sample_patient,
            driver_id=sample_driver,
            vehicle_id=sample_vehicle,
            transport_type=TransportType.AMBULANCE,
            status=MissionStatus.ON_SITE,
            pickup_address="10 rue Test",
            destination_address="Hôpital Test",
            scheduled_pickup_time=datetime.utcnow(),
            on_site_at=datetime.utcnow() - timedelta(minutes=25),
        )
        db.session.add(mission)
        db.session.commit()
        mission_id = mission.id

        result, auto_dropped = check_ambulance_auto_drop(mission_id, delay_minutes=20)
        assert auto_dropped is True
        assert result.status == MissionStatus.DROPPED


def test_ambulance_no_auto_drop_too_soon(app, sample_patient, sample_driver, sample_vehicle):
    with app.app_context():
        mission = Mission(
            patient_id=sample_patient,
            driver_id=sample_driver,
            vehicle_id=sample_vehicle,
            transport_type=TransportType.AMBULANCE,
            status=MissionStatus.ON_SITE,
            pickup_address="10 rue Test",
            destination_address="Hôpital Test",
            scheduled_pickup_time=datetime.utcnow(),
            on_site_at=datetime.utcnow() - timedelta(minutes=5),
        )
        db.session.add(mission)
        db.session.commit()
        mission_id = mission.id

        result, auto_dropped = check_ambulance_auto_drop(mission_id, delay_minutes=20)
        assert auto_dropped is False
        assert result.status == MissionStatus.ON_SITE


def test_billing_readiness_after_finish(app, sample_patient, sample_driver, sample_vehicle):
    with app.app_context():
        mission = Mission(
            patient_id=sample_patient,
            driver_id=sample_driver,
            vehicle_id=sample_vehicle,
            transport_type=TransportType.AMBULANCE,
            status=MissionStatus.DROPPED,
            pickup_address="10 rue Test",
            destination_address="Hôpital Test",
            scheduled_pickup_time=datetime.utcnow(),
            has_transport_slip=True,
            has_prescription=True,
            distance_km=12.0,
        )
        db.session.add(mission)
        db.session.commit()
        mission_id = mission.id

        result, error = update_mission_status(mission_id, MissionStatus.FINISHED)
        assert error is None
        assert result.is_billing_ready is True


def test_dashboard_stats(app):
    with app.app_context():
        stats = get_dashboard_stats()
        assert "missions_today" in stats
        assert "pending" in stats
        assert "finished" in stats
