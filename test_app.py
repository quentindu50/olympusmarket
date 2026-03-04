"""
Tests for the ambulance/transport management application.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app import create_app
from models import db, Patient, Driver, Vehicle, Mission, Invoice, Establishment, Prescriber, Message, Incident


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def populated_db(app):
    """Seed the database with sample data."""
    with app.app_context():
        establishment = Establishment(name="CHU Bordeaux", address="1 rue Pellegrin, Bordeaux")
        db.session.add(establishment)
        db.session.flush()

        prescriber = Prescriber(
            first_name="Jean", last_name="Dupont", specialty="Cardiologie",
            establishment_id=establishment.id
        )
        db.session.add(prescriber)

        patient = Patient(
            first_name="Marie", last_name="Martin",
            establishment_id=establishment.id
        )
        db.session.add(patient)
        db.session.flush()

        driver = Driver(
            first_name="Pierre", last_name="Bernard",
            license_number="AB123456", dea_certificate="DEA2020"
        )
        db.session.add(driver)

        vehicle = Vehicle(
            registration="AB-123-CD", vehicle_type="Ambulance",
            brand="Mercedes", model="Sprinter"
        )
        db.session.add(vehicle)
        db.session.flush()

        from datetime import datetime
        mission = Mission(
            patient_id=patient.id,
            driver_id=driver.id,
            vehicle_id=vehicle.id,
            pickup_address="1 rue de la Paix, Bordeaux",
            dropoff_address="2 avenue Gambetta, Bordeaux",
            scheduled_at=datetime(2026, 6, 1, 10, 0),
            mission_type="aller",
            distance_km=12.5,
        )
        db.session.add(mission)
        db.session.commit()

        return {
            "establishment_id": establishment.id,
            "patient_id": patient.id,
            "driver_id": driver.id,
            "vehicle_id": vehicle.id,
            "mission_id": mission.id,
        }


# --- Dashboard ---

def test_dashboard_loads(client, populated_db):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Tableau de bord" in rv.data


def test_dashboard_shows_stats(client, populated_db):
    rv = client.get("/")
    assert rv.status_code == 200
    # Check that key stat labels appear
    assert b"Missions" in rv.data or b"Patients" in rv.data


# --- Missions ---

def test_missions_list(client, populated_db):
    rv = client.get("/missions/")
    assert rv.status_code == 200
    assert b"Missions" in rv.data


def test_missions_list_filter(client, populated_db):
    rv = client.get("/missions/?status=pending")
    assert rv.status_code == 200


def test_mission_detail(client, populated_db):
    rv = client.get(f"/missions/{populated_db['mission_id']}")
    assert rv.status_code == 200
    assert b"Martin" in rv.data


def test_mission_not_found(client, app):
    with app.app_context():
        rv = client.get("/missions/9999")
        assert rv.status_code == 404


def test_new_mission_form(client, populated_db):
    rv = client.get("/missions/new")
    assert rv.status_code == 200
    assert b"Nouvelle mission" in rv.data


def test_create_mission(client, app, populated_db):
    rv = client.post(
        "/missions/new",
        data={
            "patient_id": populated_db["patient_id"],
            "driver_id": populated_db["driver_id"],
            "vehicle_id": populated_db["vehicle_id"],
            "pickup_address": "10 rue Victor Hugo",
            "dropoff_address": "20 avenue Mériadeck",
            "scheduled_at": "2026-07-01T09:00",
            "mission_type": "aller",
            "auto_dropoff_delay": "30",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert Mission.query.count() == 2


def test_update_mission_status(client, app, populated_db):
    rv = client.post(
        f"/missions/{populated_db['mission_id']}/status",
        data={"status": "in_progress"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        mission = Mission.query.get(populated_db["mission_id"])
        assert mission.status == Mission.STATUS_IN_PROGRESS
        assert mission.started_at is not None


def test_complete_mission_sets_completed_at(client, app, populated_db):
    client.post(
        f"/missions/{populated_db['mission_id']}/status",
        data={"status": "completed"},
    )
    with app.app_context():
        mission = Mission.query.get(populated_db["mission_id"])
        assert mission.status == Mission.STATUS_COMPLETED
        assert mission.completed_at is not None


# --- Patients ---

def test_patients_list(client, populated_db):
    rv = client.get("/patients/")
    assert rv.status_code == 200
    assert b"Martin" in rv.data


def test_patients_search(client, populated_db):
    rv = client.get("/patients/?q=Martin")
    assert rv.status_code == 200
    assert b"Martin" in rv.data


def test_patient_detail(client, populated_db):
    rv = client.get(f"/patients/{populated_db['patient_id']}")
    assert rv.status_code == 200
    assert b"Marie" in rv.data


def test_new_patient_form(client, app):
    with app.app_context():
        rv = client.get("/patients/new")
        assert rv.status_code == 200


def test_create_patient(client, app, populated_db):
    rv = client.post(
        "/patients/new",
        data={
            "first_name": "Alice",
            "last_name": "Dupont",
            "phone": "0612345678",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert Patient.query.filter_by(last_name="Dupont").first() is not None


# --- Drivers ---

def test_drivers_list(client, populated_db):
    rv = client.get("/drivers/")
    assert rv.status_code == 200
    assert b"Bernard" in rv.data


def test_driver_detail(client, populated_db):
    rv = client.get(f"/drivers/{populated_db['driver_id']}")
    assert rv.status_code == 200


def test_create_driver(client, app, populated_db):
    rv = client.post(
        "/drivers/new",
        data={
            "first_name": "Lucas",
            "last_name": "Moreau",
            "license_number": "XY789012",
            "dea_certificate": "CCA2022",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert Driver.query.filter_by(last_name="Moreau").first() is not None


def test_toggle_driver_availability(client, app, populated_db):
    with app.app_context():
        driver = Driver.query.get(populated_db["driver_id"])
        initial = driver.is_available
    client.post(f"/drivers/{populated_db['driver_id']}/toggle_availability")
    with app.app_context():
        driver = Driver.query.get(populated_db["driver_id"])
        assert driver.is_available != initial


# --- Vehicles ---

def test_vehicles_list(client, populated_db):
    rv = client.get("/vehicles/")
    assert rv.status_code == 200
    assert b"AB-123-CD" in rv.data


def test_vehicle_detail(client, populated_db):
    rv = client.get(f"/vehicles/{populated_db['vehicle_id']}")
    assert rv.status_code == 200


def test_create_vehicle(client, app, populated_db):
    rv = client.post(
        "/vehicles/new",
        data={
            "registration": "ZZ-999-ZZ",
            "vehicle_type": "VSL",
            "brand": "Renault",
            "model": "Trafic",
            "capacity": "2",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert Vehicle.query.filter_by(registration="ZZ-999-ZZ").first() is not None


def test_toggle_vehicle_availability(client, app, populated_db):
    with app.app_context():
        vehicle = Vehicle.query.get(populated_db["vehicle_id"])
        initial = vehicle.is_available
    client.post(f"/vehicles/{populated_db['vehicle_id']}/toggle_availability")
    with app.app_context():
        vehicle = Vehicle.query.get(populated_db["vehicle_id"])
        assert vehicle.is_available != initial


# --- Billing ---

def test_billing_list(client, populated_db):
    rv = client.get("/billing/")
    assert rv.status_code == 200


def test_create_invoice(client, app, populated_db):
    rv = client.post(
        f"/billing/new/{populated_db['mission_id']}",
        data={"amount_base": "45.50", "amount_surcharges": "5.00"},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        inv = Invoice.query.filter_by(mission_id=populated_db["mission_id"]).first()
        assert inv is not None
        assert inv.amount_total == pytest.approx(50.50)
        assert inv.invoice_number.startswith("FAC-")


def test_invoice_status_update(client, app, populated_db):
    with app.app_context():
        inv = Invoice(
            mission_id=populated_db["mission_id"],
            invoice_number="FAC-00001",
            amount_base=40.0,
            amount_total=40.0,
        )
        db.session.add(inv)
        db.session.commit()
        inv_id = inv.id

    client.post(f"/billing/{inv_id}/status", data={"status": "paid"})
    with app.app_context():
        inv = Invoice.query.get(inv_id)
        assert inv.status == Invoice.STATUS_PAID
        assert inv.paid_at is not None


# --- Messaging ---

def test_messaging_list(client, populated_db):
    rv = client.get("/messaging/")
    assert rv.status_code == 200


def test_send_message(client, app, populated_db):
    rv = client.post(
        "/messaging/new",
        data={
            "sender_id": populated_db["driver_id"],
            "content": "Arrivée imminente",
            "mission_id": populated_db["mission_id"],
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        msg = Message.query.filter_by(content="Arrivée imminente").first()
        assert msg is not None
        assert not msg.is_read


def test_mark_message_read(client, app, populated_db):
    with app.app_context():
        msg = Message(content="Test message")
        db.session.add(msg)
        db.session.commit()
        msg_id = msg.id

    client.post(f"/messaging/{msg_id}/read")
    with app.app_context():
        msg = Message.query.get(msg_id)
        assert msg.is_read


# --- Admin ---

def test_admin_index(client, populated_db):
    rv = client.get("/admin/")
    assert rv.status_code == 200
    assert b"Administration" in rv.data


def test_create_establishment(client, app):
    with app.app_context():
        rv = client.post(
            "/admin/establishments/new",
            data={"name": "Clinique du Sport", "address": "5 avenue du Médoc"},
            follow_redirects=True,
        )
        assert rv.status_code == 200
        assert Establishment.query.filter_by(name="Clinique du Sport").first() is not None


def test_create_prescriber(client, app, populated_db):
    rv = client.post(
        "/admin/prescribers/new",
        data={
            "first_name": "Sophie",
            "last_name": "Leroy",
            "specialty": "Neurologie",
            "establishment_id": populated_db["establishment_id"],
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert Prescriber.query.filter_by(last_name="Leroy").first() is not None


def test_report_incident(client, app, populated_db):
    rv = client.post(
        "/admin/incidents/new",
        data={
            "driver_id": populated_db["driver_id"],
            "mission_id": populated_db["mission_id"],
            "description": "Panne mécanique en route",
            "severity": "medium",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        inc = Incident.query.filter_by(description="Panne mécanique en route").first()
        assert inc is not None
        assert not inc.resolved


def test_resolve_incident(client, app, populated_db):
    with app.app_context():
        inc = Incident(
            description="Test incident",
            severity=Incident.SEVERITY_LOW,
            driver_id=populated_db["driver_id"],
        )
        db.session.add(inc)
        db.session.commit()
        inc_id = inc.id

    client.post(
        f"/admin/incidents/{inc_id}/resolve",
        data={"resolution_notes": "Problème réglé"},
    )
    with app.app_context():
        inc = Incident.query.get(inc_id)
        assert inc.resolved


# --- Model repr ---

def test_model_reprs(app):
    with app.app_context():
        e = Establishment(name="Test", address="addr")
        assert "Test" in repr(e)

        p = Patient(first_name="Jean", last_name="Valjean")
        assert "Valjean" in repr(p)

        d = Driver(first_name="A", last_name="B", license_number="X")
        assert "B" in repr(d)

        v = Vehicle(registration="AA-00-BB", vehicle_type="VSL")
        assert "AA-00-BB" in repr(v)
