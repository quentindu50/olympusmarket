from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Mission, Patient, Driver, Vehicle, Prescriber, Establishment

missions_bp = Blueprint("missions", __name__, url_prefix="/missions")


@missions_bp.route("/")
def index():
    status_filter = request.args.get("status", "")
    query = Mission.query.order_by(Mission.scheduled_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    missions = query.all()
    return render_template("missions/index.html", missions=missions, status_filter=status_filter)


@missions_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        driver_id = request.form.get("driver_id") or None
        vehicle_id = request.form.get("vehicle_id") or None
        establishment_id = request.form.get("establishment_id") or None
        prescriber_id = request.form.get("prescriber_id") or None
        scheduled_str = request.form.get("scheduled_at")
        try:
            scheduled_at = datetime.strptime(scheduled_str, "%Y-%m-%dT%H:%M")
        except (ValueError, TypeError):
            flash("Date/heure invalide.", "danger")
            return redirect(url_for("missions.new"))

        mission = Mission(
            patient_id=patient_id,
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            establishment_id=establishment_id,
            prescriber_id=prescriber_id,
            pickup_address=request.form.get("pickup_address", ""),
            dropoff_address=request.form.get("dropoff_address", ""),
            scheduled_at=scheduled_at,
            mission_type=request.form.get("mission_type", "aller"),
            distance_km=request.form.get("distance_km") or None,
            auto_dropoff_delay=int(request.form.get("auto_dropoff_delay", 30)),
            notes=request.form.get("notes", ""),
        )
        db.session.add(mission)
        db.session.commit()
        flash("Mission créée avec succès.", "success")
        return redirect(url_for("missions.index"))

    patients = Patient.query.order_by(Patient.last_name).all()
    drivers = Driver.query.filter_by(is_active=True).order_by(Driver.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.registration).all()
    establishments = Establishment.query.order_by(Establishment.name).all()
    prescribers = Prescriber.query.order_by(Prescriber.last_name).all()
    return render_template(
        "missions/form.html",
        mission=None,
        patients=patients,
        drivers=drivers,
        vehicles=vehicles,
        establishments=establishments,
        prescribers=prescribers,
    )


@missions_bp.route("/<int:mission_id>")
def detail(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    return render_template("missions/detail.html", mission=mission)


@missions_bp.route("/<int:mission_id>/status", methods=["POST"])
def update_status(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    new_status = request.form.get("status")
    if new_status in [
        Mission.STATUS_PENDING,
        Mission.STATUS_ASSIGNED,
        Mission.STATUS_IN_PROGRESS,
        Mission.STATUS_COMPLETED,
        Mission.STATUS_CANCELLED,
    ]:
        mission.status = new_status
        if new_status == Mission.STATUS_IN_PROGRESS and not mission.started_at:
            mission.started_at = datetime.utcnow()
        if new_status == Mission.STATUS_COMPLETED and not mission.completed_at:
            mission.completed_at = datetime.utcnow()
        db.session.commit()
        flash("Statut mis à jour.", "success")
    return redirect(url_for("missions.detail", mission_id=mission_id))
