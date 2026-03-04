from datetime import datetime, timedelta
from src.models import Mission, MissionStatus, TransportType
from src.database import db

# Default delay (minutes) before automatic drop for ambulances
AMBULANCE_AUTO_DROP_MINUTES = 20


def update_mission_status(mission_id, new_status, lat=None, lon=None):
    """Advance a mission through its status lifecycle and apply business rules."""
    mission = Mission.query.get(mission_id)
    if mission is None:
        return None, "Mission not found"

    now = datetime.utcnow()

    if new_status == MissionStatus.STARTED:
        mission.started_at = now
        mission.started_lat = lat
        mission.started_lon = lon
    elif new_status == MissionStatus.ON_SITE:
        mission.on_site_at = now
        mission.on_site_lat = lat
        mission.on_site_lon = lon
    elif new_status == MissionStatus.PATIENT_ONBOARD:
        mission.patient_onboard_at = now
    elif new_status == MissionStatus.DROPPED:
        mission.dropped_at = now
        mission.dropped_lat = lat
        mission.dropped_lon = lon
    elif new_status == MissionStatus.FINISHED:
        mission.finished_at = now
        _check_billing_readiness(mission)

    mission.status = new_status
    mission.updated_at = now
    db.session.commit()
    return mission, None


def check_ambulance_auto_drop(mission_id, delay_minutes=AMBULANCE_AUTO_DROP_MINUTES):
    """
    For ambulance missions that are ON_SITE and the delay has elapsed without
    reaching DROPPED status, automatically advance to DROPPED.
    Returns (mission, auto_dropped) tuple.
    """
    mission = Mission.query.get(mission_id)
    if mission is None:
        return None, False

    if (
        mission.transport_type == TransportType.AMBULANCE
        and mission.status == MissionStatus.ON_SITE
        and mission.on_site_at is not None
    ):
        elapsed = datetime.utcnow() - mission.on_site_at
        if elapsed >= timedelta(minutes=delay_minutes):
            mission.dropped_at = datetime.utcnow()
            mission.status = MissionStatus.DROPPED
            mission.updated_at = datetime.utcnow()
            db.session.commit()
            return mission, True

    return mission, False


def _check_billing_readiness(mission):
    """Mark mission as billing-ready when all required documents are present."""
    if (
        mission.has_transport_slip
        and mission.has_prescription
        and mission.distance_km is not None
    ):
        mission.is_billing_ready = True


def get_daily_missions(date=None):
    """Return all missions scheduled for a given date (defaults to today)."""
    if date is None:
        date = datetime.utcnow().date()
    start = datetime.combine(date, datetime.min.time())
    end = start + timedelta(days=1)
    return Mission.query.filter(
        Mission.scheduled_pickup_time >= start,
        Mission.scheduled_pickup_time < end,
    ).all()


def get_dashboard_stats():
    """Return key metrics for the regulation dashboard."""
    today = datetime.utcnow().date()
    daily = get_daily_missions(today)

    stats = {
        "missions_today": len(daily),
        "pending": sum(1 for m in daily if m.status == MissionStatus.PENDING),
        "in_progress": sum(
            1 for m in daily if m.status in (
                MissionStatus.STARTED,
                MissionStatus.ON_SITE,
                MissionStatus.PATIENT_ONBOARD,
                MissionStatus.DROPPED,
            )
        ),
        "finished": sum(1 for m in daily if m.status == MissionStatus.FINISHED),
        "cancelled": sum(1 for m in daily if m.status == MissionStatus.CANCELLED),
        "billing_ready": sum(1 for m in daily if m.is_billing_ready),
    }
    return stats
