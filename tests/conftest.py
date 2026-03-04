import pytest
from src.main import create_app
from src.database import db as _db
from src.models import User, UserRole, Patient, Driver, Vehicle, TransportType


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Create an admin user and return JWT auth headers."""
    with client.application.app_context():
        user = User(username="admin", role=UserRole.ADMIN, first_name="Admin", last_name="Test")
        user.set_password("password")
        _db.session.add(user)
        _db.session.commit()

    response = client.post("/api/auth/login", json={"username": "admin", "password": "password"})
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_patient(app):
    with app.app_context():
        patient = Patient(first_name="Jean", last_name="Dupont", phone="0612345678")
        _db.session.add(patient)
        _db.session.commit()
        return patient.id


@pytest.fixture
def sample_driver(app):
    with app.app_context():
        user = User(username="driver1", role=UserRole.DRIVER, first_name="Pierre", last_name="Martin")
        user.set_password("pass")
        _db.session.add(user)
        _db.session.flush()
        driver = Driver(user_id=user.id, license_number="AB123456")
        _db.session.add(driver)
        _db.session.commit()
        return driver.id


@pytest.fixture
def sample_vehicle(app):
    with app.app_context():
        vehicle = Vehicle(license_plate="AA-001-BB", transport_type=TransportType.AMBULANCE, brand="Renault")
        _db.session.add(vehicle)
        _db.session.commit()
        return vehicle.id
