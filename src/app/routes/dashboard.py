from flask import Blueprint, render_template
from datetime import datetime, date
from ..models import Transport, Patient, Driver, Vehicle, Invoice

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    today_transports = Transport.query.filter(
        Transport.scheduled_datetime >= today_start,
        Transport.scheduled_datetime <= today_end,
    ).order_by(Transport.scheduled_datetime).all()

    stats = {
        'total_patients': Patient.query.count(),
        'total_drivers': Driver.query.filter_by(status='active').count(),
        'total_vehicles': Vehicle.query.filter_by(status='available').count(),
        'today_transports': len(today_transports),
        'pending_invoices': Invoice.query.filter_by(status='pending').count(),
        'urgent_transports': Transport.query.filter(
            Transport.scheduled_datetime >= today_start,
            Transport.scheduled_datetime <= today_end,
            Transport.priority == 'urgent',
        ).count(),
    }

    return render_template(
        'dashboard.html',
        today_transports=today_transports,
        stats=stats,
        today=today,
    )
