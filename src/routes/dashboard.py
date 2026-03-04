from flask import Blueprint, render_template
from models import db, Mission, Driver, Vehicle, Patient, Incident, Message

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    stats = {
        "missions_today": Mission.query.filter(
            Mission.status != Mission.STATUS_CANCELLED
        ).count(),
        "missions_pending": Mission.query.filter_by(
            status=Mission.STATUS_PENDING
        ).count(),
        "missions_in_progress": Mission.query.filter_by(
            status=Mission.STATUS_IN_PROGRESS
        ).count(),
        "drivers_available": Driver.query.filter_by(
            is_available=True, is_active=True
        ).count(),
        "vehicles_available": Vehicle.query.filter_by(is_available=True).count(),
        "patients_total": Patient.query.count(),
        "incidents_open": Incident.query.filter_by(resolved=False).count(),
        "messages_unread": Message.query.filter_by(is_read=False).count(),
    }
    recent_missions = (
        Mission.query.order_by(Mission.created_at.desc()).limit(5).all()
    )
    return render_template(
        "dashboard/index.html", stats=stats, recent_missions=recent_missions
    )
