from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Driver

drivers_bp = Blueprint("drivers", __name__, url_prefix="/drivers")


@drivers_bp.route("/")
def index():
    drivers = Driver.query.filter_by(is_active=True).order_by(Driver.last_name).all()
    return render_template("drivers/index.html", drivers=drivers)


@drivers_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        driver = Driver(
            first_name=request.form.get("first_name", ""),
            last_name=request.form.get("last_name", ""),
            license_number=request.form.get("license_number", ""),
            dea_certificate=request.form.get("dea_certificate", ""),
            phone=request.form.get("phone", ""),
            email=request.form.get("email", ""),
        )
        db.session.add(driver)
        db.session.commit()
        flash("Chauffeur ajouté avec succès.", "success")
        return redirect(url_for("drivers.index"))
    return render_template("drivers/form.html", driver=None)


@drivers_bp.route("/<int:driver_id>")
def detail(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return render_template("drivers/detail.html", driver=driver)


@drivers_bp.route("/<int:driver_id>/toggle_availability", methods=["POST"])
def toggle_availability(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    driver.is_available = not driver.is_available
    db.session.commit()
    flash("Disponibilité mise à jour.", "success")
    return redirect(url_for("drivers.detail", driver_id=driver_id))
