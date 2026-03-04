from datetime import datetime
from extensions import db


class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    social_security_number = db.Column(db.String(20))
    ald = db.Column(db.Boolean, default=False)
    mutual_insurance = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    doctor_name = db.Column(db.String(100))
    doctor_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transports = db.relationship('Transport', backref='patient', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    license_number = db.Column(db.String(50))
    vsl_card = db.Column(db.Boolean, default=False)
    ambulance_card = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='available')  # available/unavailable/on_mission
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transports = db.relationship('Transport', backref='driver', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(20), nullable=False, unique=True)
    vehicle_type = db.Column(db.String(20), nullable=False)  # vsl/ambulance/taxi
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    insurance_expiry = db.Column(db.Date)
    technical_control_expiry = db.Column(db.Date)
    mileage = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='available')  # available/unavailable/maintenance
    notes = db.Column(db.Text)
    transports = db.relationship('Transport', backref='vehicle', lazy=True)


class Transport(db.Model):
    __tablename__ = 'transports'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    transport_type = db.Column(db.String(20), nullable=False)  # vsl/ambulance/taxi
    pickup_address = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    return_scheduled_at = db.Column(db.DateTime, nullable=True)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending/assigned/in_progress/completed/cancelled
    prescription_photo = db.Column(db.String(255))
    recurrent = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    billing = db.relationship('Billing', backref='transport', lazy=True, uselist=False)
    messages = db.relationship('Message', backref='transport', lazy=True)


class Billing(db.Model):
    __tablename__ = 'billing'
    id = db.Column(db.Integer, primary_key=True)
    transport_id = db.Column(db.Integer, db.ForeignKey('transports.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    tiers_payant = db.Column(db.Boolean, default=False)
    cpam_transmitted = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    urgent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transport_id = db.Column(db.Integer, db.ForeignKey('transports.id'), nullable=True)
