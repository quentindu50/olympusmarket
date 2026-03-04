from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Vehicle
from datetime import date, timedelta

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


def _parse_date(val):
    if val:
        try:
            return date.fromisoformat(val)
        except ValueError:
            return None
    return None


@vehicles_bp.route('/')
def list():
    vehicles = Vehicle.query.order_by(Vehicle.registration).all()
    today = date.today()
    soon = today + timedelta(days=30)
    warnings = {}
    for v in vehicles:
        w = []
        if v.insurance_expiry:
            if v.insurance_expiry < today:
                w.append('Assurance expirée')
            elif v.insurance_expiry <= soon:
                w.append('Assurance expire bientôt')
        if v.technical_control_expiry:
            if v.technical_control_expiry < today:
                w.append('Contrôle technique expiré')
            elif v.technical_control_expiry <= soon:
                w.append('Contrôle technique expire bientôt')
        if w:
            warnings[v.id] = w
    return render_template('vehicles/list.html', vehicles=vehicles, warnings=warnings)


@vehicles_bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        vehicle = Vehicle(
            registration=request.form['registration'],
            vehicle_type=request.form['vehicle_type'],
            brand=request.form.get('brand', ''),
            model=request.form.get('model', ''),
            year=request.form.get('year') or None,
            insurance_expiry=_parse_date(request.form.get('insurance_expiry')),
            technical_control_expiry=_parse_date(request.form.get('technical_control_expiry')),
            mileage=request.form.get('mileage') or 0,
            status=request.form.get('status', 'available'),
            notes=request.form.get('notes', ''),
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Véhicule créé avec succès.', 'success')
        return redirect(url_for('vehicles.list'))
    return render_template('vehicles/form.html', vehicle=None)


@vehicles_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
def edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if request.method == 'POST':
        vehicle.registration = request.form['registration']
        vehicle.vehicle_type = request.form['vehicle_type']
        vehicle.brand = request.form.get('brand', '')
        vehicle.model = request.form.get('model', '')
        vehicle.year = request.form.get('year') or None
        vehicle.insurance_expiry = _parse_date(request.form.get('insurance_expiry'))
        vehicle.technical_control_expiry = _parse_date(request.form.get('technical_control_expiry'))
        vehicle.mileage = request.form.get('mileage') or 0
        vehicle.status = request.form.get('status', 'available')
        vehicle.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Véhicule mis à jour avec succès.', 'success')
        return redirect(url_for('vehicles.list'))
    return render_template('vehicles/form.html', vehicle=vehicle)


@vehicles_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
def delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    flash('Véhicule supprimé.', 'warning')
    return redirect(url_for('vehicles.list'))
