from datetime import datetime
from .. import db


class Transport(db.Model):
    __tablename__ = 'transports'

    TYPES = [('taxi', 'Taxi'), ('vsl', 'VSL'), ('ambulance', 'Ambulance')]
    STATUSES = [
        ('scheduled', 'Planifié'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    PRIORITIES = [('normal', 'Normal'), ('urgent', 'Urgent')]

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    destination_establishment_id = db.Column(
        db.Integer, db.ForeignKey('establishments.id'), nullable=True
    )
    transport_type = db.Column(db.String(20), nullable=False, default='vsl')
    pickup_address = db.Column(db.String(255), nullable=False)
    pickup_city = db.Column(db.String(100), nullable=True)
    destination_address = db.Column(db.String(255), nullable=False)
    destination_city = db.Column(db.String(100), nullable=True)
    scheduled_datetime = db.Column(db.DateTime, nullable=False)
    return_datetime = db.Column(db.DateTime, nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='scheduled')
    distance_km = db.Column(db.Float, nullable=True)
    recurrence = db.Column(db.String(20), nullable=True)
    recurrence_end_date = db.Column(db.Date, nullable=True)
    prescription_scan = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoice = db.relationship('Invoice', backref='transport', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Transport #{self.id} {self.scheduled_datetime}>'
