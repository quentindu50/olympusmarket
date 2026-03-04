from datetime import datetime
from .. import db


class Establishment(db.Model):
    __tablename__ = 'establishments'

    TYPES = [
        ('hospital', 'Hôpital'),
        ('clinic', 'Clinique'),
        ('dialysis', 'Centre de dialyse'),
        ('radiotherapy', 'Centre de radiothérapie'),
        ('ehpad', 'EHPAD'),
        ('doctor', 'Cabinet médical'),
        ('other', 'Autre'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    establishment_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    contact_name = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transports_destination = db.relationship(
        'Transport', foreign_keys='Transport.destination_establishment_id',
        backref='destination_establishment', lazy=True
    )

    def __repr__(self):
        return f'<Establishment {self.name}>'
