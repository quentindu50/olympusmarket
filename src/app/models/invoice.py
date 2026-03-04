from datetime import datetime
from .. import db


class Invoice(db.Model):
    __tablename__ = 'invoices'

    STATUSES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    transport_id = db.Column(db.Integer, db.ForeignKey('transports.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    due_date = db.Column(db.Date, nullable=True)
    base_amount = db.Column(db.Float, nullable=False, default=0.0)
    km_amount = db.Column(db.Float, default=0.0)
    supplement_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    cpam_amount = db.Column(db.Float, default=0.0)
    mutual_amount = db.Column(db.Float, default=0.0)
    patient_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

    @classmethod
    def generate_invoice_number(cls):
        last = cls.query.order_by(cls.id.desc()).first()
        num = (last.id + 1) if last else 1
        return f'AT-{datetime.utcnow().year}-{num:05d}'
