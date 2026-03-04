from datetime import datetime
from .. import db


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    social_security_number = db.Column(db.String(15), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    ald = db.Column(db.Boolean, default=False)
    mutual_insurance = db.Column(db.String(100), nullable=True)
    prescribing_doctor = db.Column(db.String(200), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transports = db.relationship('Transport', backref='patient', lazy=True)

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
