from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Establishment, Prescriber, Incident, Driver, Mission

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index():
    establishments = Establishment.query.order_by(Establishment.name).all()
    prescribers = Prescriber.query.order_by(Prescriber.last_name).all()
    incidents = Incident.query.order_by(Incident.reported_at.desc()).all()
    return render_template(
        "admin/index.html",
        establishments=establishments,
        prescribers=prescribers,
        incidents=incidents,
    )


# --- Establishments ---

@admin_bp.route("/establishments/new", methods=["GET", "POST"])
def new_establishment():
    if request.method == "POST":
        establishment = Establishment(
            name=request.form.get("name", ""),
            address=request.form.get("address", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", ""),
        )
        db.session.add(establishment)
        db.session.commit()
        flash("Établissement ajouté.", "success")
        return redirect(url_for("admin.index"))
    return render_template("admin/establishment_form.html")


# --- Prescribers ---

@admin_bp.route("/prescribers/new", methods=["GET", "POST"])
def new_prescriber():
    if request.method == "POST":
        prescriber = Prescriber(
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            rpps=request.form.get("rpps", "") or None,
            specialty=request.form.get("specialty", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", ""),
            establishment_id=request.form.get("establishment_id") or None,
        )
        db.session.add(prescriber)
        db.session.commit()
        flash("Prescripteur ajouté.", "success")
        return redirect(url_for("admin.index"))
    establishments = Establishment.query.order_by(Establishment.name).all()
    return render_template("admin/prescriber_form.html", establishments=establishments)


# --- Incidents ---

@admin_bp.route("/incidents/new", methods=["GET", "POST"])
def new_incident():
    if request.method == "POST":
        incident = Incident(
            mission_id=request.form.get("mission_id") or None,
            driver_id=request.form.get("driver_id") or None,
            description=request.form.get("description", ""),
            severity=request.form.get("severity", Incident.SEVERITY_LOW),
        )
        db.session.add(incident)
        db.session.commit()
        flash("Incident signalé.", "success")
        return redirect(url_for("admin.index"))
    drivers = Driver.query.filter_by(is_active=True).order_by(Driver.last_name).all()
    missions = Mission.query.order_by(Mission.scheduled_at.desc()).limit(50).all()
    return render_template(
        "admin/incident_form.html", drivers=drivers, missions=missions
    )


@admin_bp.route("/incidents/<int:incident_id>/resolve", methods=["POST"])
def resolve_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    incident.resolved = True
    incident.resolution_notes = request.form.get("resolution_notes", "")
    db.session.commit()
    flash("Incident résolu.", "success")
    return redirect(url_for("admin.index"))
