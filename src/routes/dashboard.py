from flask import Blueprint, render_template
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    from extensions import db
    from models import Patient, Driver, Vehicle, Transport, Message
    from sqlalchemy import func

    patient_count = db.session.query(func.count(Patient.id)).scalar()
    driver_count = db.session.query(func.count(Driver.id)).scalar()
    vehicle_count = db.session.query(func.count(Vehicle.id)).scalar()

    today = date.today()
    today_transports = Transport.query.filter(
        func.date(Transport.scheduled_at) == today
    ).count()

    recent_transports = Transport.query.order_by(Transport.scheduled_at.desc()).limit(10).all()
    urgent_messages = Message.query.filter_by(urgent=True).order_by(Message.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        patient_count=patient_count,
        driver_count=driver_count,
        vehicle_count=vehicle_count,
        today_transports=today_transports,
        recent_transports=recent_transports,
        urgent_messages=urgent_messages,
    )
