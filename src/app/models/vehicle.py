from datetime import datetime
from .. import db


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    TYPES = [('taxi', 'Taxi'), ('vsl', 'VSL'), ('ambulance', 'Ambulance')]

    id = db.Column(db.Integer, primary_key=True)
    registration_plate = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    mileage = db.Column(db.Integer, default=0)
    insurance_number = db.Column(db.String(100), nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    technical_control_date = db.Column(db.Date, nullable=True)
    technical_control_expiry = db.Column(db.Date, nullable=True)
    last_maintenance_date = db.Column(db.Date, nullable=True)
    next_maintenance_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='available')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transports = db.relationship('Transport', backref='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.registration_plate} ({self.vehicle_type})>'
