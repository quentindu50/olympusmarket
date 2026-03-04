"""
Data models for the ambulance/transport management application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Establishment(db.Model):
    __tablename__ = "establishments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patients = db.relationship("Patient", backref="establishment", lazy=True)
    missions = db.relationship("Mission", backref="establishment", lazy=True)

    def __repr__(self):
        return f"<Establishment {self.name}>"


class Prescriber(db.Model):
    __tablename__ = "prescribers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    rpps = db.Column(db.String(20), unique=True)
    specialty = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    establishment_id = db.Column(db.Integer, db.ForeignKey("establishments.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    missions = db.relationship("Mission", backref="prescriber", lazy=True)

    def __repr__(self):
        return f"<Prescriber Dr. {self.last_name}>"


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date)
    social_security = db.Column(db.String(15))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    establishment_id = db.Column(db.Integer, db.ForeignKey("establishments.id"))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    missions = db.relationship("Mission", backref="patient", lazy=True)

    def __repr__(self):
        return f"<Patient {self.last_name} {self.first_name}>"


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)  # ambulance, VSL, SMUR
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    capacity = db.Column(db.Integer, default=1)
    is_available = db.Column(db.Boolean, default=True)
    last_maintenance = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    missions = db.relationship("Mission", backref="vehicle", lazy=True)

    def __repr__(self):
        return f"<Vehicle {self.registration} ({self.vehicle_type})>"


class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    license_number = db.Column(db.String(20), unique=True, nullable=False)
    dea_certificate = db.Column(db.String(20))  # DEA/CCA certification
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_available = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    missions = db.relationship("Mission", backref="driver", lazy=True)
    incidents = db.relationship("Incident", backref="driver", lazy=True)
    messages_sent = db.relationship(
        "Message", foreign_keys="Message.sender_id", backref="sender", lazy=True
    )

    def __repr__(self):
        return f"<Driver {self.last_name} {self.first_name}>"


class Mission(db.Model):
    __tablename__ = "missions"

    STATUS_PENDING = "pending"
    STATUS_ASSIGNED = "assigned"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"))
    establishment_id = db.Column(db.Integer, db.ForeignKey("establishments.id"))
    prescriber_id = db.Column(db.Integer, db.ForeignKey("prescribers.id"))

    pickup_address = db.Column(db.String(255), nullable=False)
    dropoff_address = db.Column(db.String(255), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    # Configurable auto-dropoff delay (minutes)
    auto_dropoff_delay = db.Column(db.Integer, default=30)

    status = db.Column(db.String(20), default=STATUS_PENDING)
    mission_type = db.Column(db.String(50))  # aller, retour, aller-retour
    distance_km = db.Column(db.Float)
    notes = db.Column(db.Text)

    # GPS tracking
    last_latitude = db.Column(db.Float)
    last_longitude = db.Column(db.Float)
    last_gps_update = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoice = db.relationship("Invoice", backref="mission", uselist=False, lazy=True)
    incidents = db.relationship("Incident", backref="mission", lazy=True)
    documents = db.relationship("Document", backref="mission", lazy=True)

    def __repr__(self):
        return f"<Mission #{self.id} [{self.status}]>"


class Invoice(db.Model):
    __tablename__ = "invoices"

    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_PAID = "paid"
    STATUS_REJECTED = "rejected"

    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"), nullable=False)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    amount_base = db.Column(db.Float, default=0.0)
    amount_surcharges = db.Column(db.Float, default=0.0)
    amount_total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default=STATUS_DRAFT)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.amount_total}€>"


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"))
    doc_type = db.Column(db.String(50))  # prescription, feuille_de_soin, bon_transport
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Document {self.doc_type} - {self.filename}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    content = db.Column(db.Text, nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"))
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message from driver #{self.sender_id}>"


class Incident(db.Model):
    __tablename__ = "incidents"

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"

    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey("missions.id"))
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default=SEVERITY_LOW)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    resolution_notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Incident #{self.id} [{self.severity}]>"
