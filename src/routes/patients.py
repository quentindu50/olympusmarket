from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Patient, Establishment

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.route("/")
def index():
    search = request.args.get("q", "")
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.last_name.ilike(f"%{search}%"))
            | (Patient.first_name.ilike(f"%{search}%"))
        )
    patients = query.order_by(Patient.last_name).all()
    return render_template("patients/index.html", patients=patients, search=search)


@patients_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        from datetime import datetime
        birth_str = request.form.get("birth_date")
        birth_date = None
        if birth_str:
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        patient = Patient(
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            birth_date=birth_date,
            social_security=request.form.get("social_security", ""),
            address=request.form.get("address", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", ""),
            establishment_id=request.form.get("establishment_id") or None,
            notes=request.form.get("notes", ""),
        )
        db.session.add(patient)
        db.session.commit()
        flash("Patient ajouté avec succès.", "success")
        return redirect(url_for("patients.index"))
    establishments = Establishment.query.order_by(Establishment.name).all()
    return render_template("patients/form.html", patient=None, establishments=establishments)


@patients_bp.route("/<int:patient_id>")
def detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patients/detail.html", patient=patient)
