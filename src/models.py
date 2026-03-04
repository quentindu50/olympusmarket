import enum
from datetime import datetime
from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    ADMIN = "admin"
    REGULATOR = "regulator"
    DRIVER = "driver"
    SECRETARY = "secretary"


class TransportType(enum.Enum):
    AMBULANCE = "ambulance"
    VSL = "vsl"
    TAXI = "taxi"


class MissionStatus(enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    STARTED = "started"        # Début mission
    ON_SITE = "on_site"        # Arrivée sur place
    PATIENT_ONBOARD = "patient_onboard"  # PEC
    DROPPED = "dropped"        # Déposé
    FINISHED = "finished"      # Terminé
    CANCELLED = "cancelled"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role.value,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_active": self.is_active,
        }


class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    social_security_number = db.Column(db.String(20), unique=True)
    birth_date = db.Column(db.Date)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    amo = db.Column(db.String(100))   # Assurance Maladie Obligatoire
    amc = db.Column(db.String(100))   # Assurance Maladie Complémentaire
    has_ald = db.Column(db.Boolean, default=False)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)
    prescriber_name = db.Column(db.String(200))
    prescriber_phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    missions = db.relationship("Mission", backref="patient", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "social_security_number": self.social_security_number,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "phone": self.phone,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "amo": self.amo,
            "amc": self.amc,
            "has_ald": self.has_ald,
            "allergies": self.allergies,
            "notes": self.notes,
            "prescriber_name": self.prescriber_name,
        }


class Driver(db.Model):
    __tablename__ = "drivers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    license_number = db.Column(db.String(50))
    vsl_card_number = db.Column(db.String(50))
    ambulance_card_number = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="driver_profile")
    missions = db.relationship("Mission", backref="driver", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "license_number": self.license_number,
            "vsl_card_number": self.vsl_card_number,
            "ambulance_card_number": self.ambulance_card_number,
            "is_available": self.is_available,
            "user": self.user.to_dict() if self.user else None,
        }


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    transport_type = db.Column(db.Enum(TransportType), nullable=False)
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    mileage = db.Column(db.Float, default=0)
    insurance_expiry = db.Column(db.Date)
    technical_control_expiry = db.Column(db.Date)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    missions = db.relationship("Mission", backref="vehicle", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "license_plate": self.license_plate,
            "transport_type": self.transport_type.value,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "mileage": self.mileage,
            "insurance_expiry": self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            "technical_control_expiry": self.technical_control_expiry.isoformat() if self.technical_control_expiry else None,
            "is_available": self.is_available,
        }


class Establishment(db.Model):
    __tablename__ = "establishments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    establishment_type = db.Column(db.String(50))  # hospital, clinic, dialysis, ehpad
    address = db.Column(db.String(255))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "establishment_type": self.establishment_type,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "phone": self.phone,
            "email": self.email,
        }


class Mission(db.Model):
    __tablename__ = "missions"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    transport_type = db.Column(db.Enum(TransportType), nullable=False)
    status = db.Column(db.Enum(MissionStatus), default=MissionStatus.PENDING)
    pickup_address = db.Column(db.String(255), nullable=False)
    pickup_city = db.Column(db.String(100))
    destination_address = db.Column(db.String(255), nullable=False)
    destination_city = db.Column(db.String(100))
    scheduled_pickup_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly
    distance_km = db.Column(db.Float)
    # Status timestamps
    started_at = db.Column(db.DateTime)
    on_site_at = db.Column(db.DateTime)
    patient_onboard_at = db.Column(db.DateTime)
    dropped_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    # GPS coordinates
    started_lat = db.Column(db.Float)
    started_lon = db.Column(db.Float)
    on_site_lat = db.Column(db.Float)
    on_site_lon = db.Column(db.Float)
    dropped_lat = db.Column(db.Float)
    dropped_lon = db.Column(db.Float)
    # Billing
    has_transport_slip = db.Column(db.Boolean, default=False)
    has_prescription = db.Column(db.Boolean, default=False)
    is_billing_ready = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "driver_id": self.driver_id,
            "vehicle_id": self.vehicle_id,
            "transport_type": self.transport_type.value,
            "status": self.status.value,
            "pickup_address": self.pickup_address,
            "pickup_city": self.pickup_city,
            "destination_address": self.destination_address,
            "destination_city": self.destination_city,
            "scheduled_pickup_time": self.scheduled_pickup_time.isoformat(),
            "reason": self.reason,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "distance_km": self.distance_km,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "on_site_at": self.on_site_at.isoformat() if self.on_site_at else None,
            "patient_onboard_at": self.patient_onboard_at.isoformat() if self.patient_onboard_at else None,
            "dropped_at": self.dropped_at.isoformat() if self.dropped_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "has_transport_slip": self.has_transport_slip,
            "has_prescription": self.has_prescription,
            "is_billing_ready": self.is_billing_ready,
            "notes": self.notes,
        }


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "mission_id": self.mission_id,
            "content": self.content,
            "is_read": self.is_read,
            "is_urgent": self.is_urgent,
            "created_at": self.created_at.isoformat(),
        }


class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    amount_total = db.Column(db.Float, default=0)
    amount_amo = db.Column(db.Float, default=0)   # Part Assurance Maladie
    amount_amc = db.Column(db.Float, default=0)   # Part Mutuelle
    amount_patient = db.Column(db.Float, default=0)  # Part patient
    is_paid = db.Column(db.Boolean, default=False)
    is_transmitted = db.Column(db.Boolean, default=False)  # Télétransmission CPAM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    mission = db.relationship("Mission", backref="invoice")

    def to_dict(self):
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "invoice_number": self.invoice_number,
            "amount_total": self.amount_total,
            "amount_amo": self.amount_amo,
            "amount_amc": self.amount_amc,
            "amount_patient": self.amount_patient,
            "is_paid": self.is_paid,
            "is_transmitted": self.is_transmitted,
            "created_at": self.created_at.isoformat(),
        }
