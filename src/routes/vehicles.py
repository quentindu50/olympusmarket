from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Vehicle

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")


@vehicles_bp.route("/")
def index():
    vehicles = Vehicle.query.order_by(Vehicle.registration).all()
    return render_template("vehicles/index.html", vehicles=vehicles)


@vehicles_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        vehicle = Vehicle(
            registration=request.form.get("registration", ""),
            vehicle_type=request.form.get("vehicle_type", "VSL"),
            brand=request.form.get("brand", ""),
            model=request.form.get("model", ""),
            year=request.form.get("year") or None,
            capacity=int(request.form.get("capacity", 1)),
        )
        db.session.add(vehicle)
        db.session.commit()
        flash("Véhicule ajouté avec succès.", "success")
        return redirect(url_for("vehicles.index"))
    return render_template("vehicles/form.html", vehicle=None)


@vehicles_bp.route("/<int:vehicle_id>")
def detail(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template("vehicles/detail.html", vehicle=vehicle)


@vehicles_bp.route("/<int:vehicle_id>/toggle_availability", methods=["POST"])
def toggle_availability(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    vehicle.is_available = not vehicle.is_available
    db.session.commit()
    flash("Disponibilité mise à jour.", "success")
    return redirect(url_for("vehicles.detail", vehicle_id=vehicle_id))
