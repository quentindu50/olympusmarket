from datetime import datetime
from .. import db


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    license_number = db.Column(db.String(50), nullable=True)
    license_expiry = db.Column(db.Date, nullable=True)
    vsl_card_number = db.Column(db.String(50), nullable=True)
    vsl_card_expiry = db.Column(db.Date, nullable=True)
    ambulance_card_number = db.Column(db.String(50), nullable=True)
    ambulance_card_expiry = db.Column(db.Date, nullable=True)
    contract_type = db.Column(db.String(50), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transports = db.relationship('Transport', backref='driver', lazy=True)

    def __repr__(self):
        return f'<Driver {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
