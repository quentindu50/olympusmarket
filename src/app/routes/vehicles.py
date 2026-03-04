from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Vehicle
from .. import db

vehicles_bp = Blueprint('vehicles', __name__)


@vehicles_bp.route('/')
def list_vehicles():
    vehicles = Vehicle.query.order_by(Vehicle.registration_plate).all()
    return render_template('vehicles/list.html', vehicles=vehicles)


@vehicles_bp.route('/new', methods=['GET', 'POST'])
def new_vehicle():
    if request.method == 'POST':
        vehicle = Vehicle(
            registration_plate=request.form['registration_plate'],
            vehicle_type=request.form['vehicle_type'],
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            year=_parse_int(request.form.get('year')),
            mileage=_parse_int(request.form.get('mileage')) or 0,
            insurance_number=request.form.get('insurance_number'),
            insurance_expiry=_parse_date(request.form.get('insurance_expiry')),
            technical_control_date=_parse_date(request.form.get('technical_control_date')),
            technical_control_expiry=_parse_date(request.form.get('technical_control_expiry')),
            last_maintenance_date=_parse_date(request.form.get('last_maintenance_date')),
            next_maintenance_date=_parse_date(request.form.get('next_maintenance_date')),
            status=request.form.get('status', 'available'),
            notes=request.form.get('notes'),
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Véhicule créé avec succès.', 'success')
        return redirect(url_for('vehicles.list_vehicles'))
    return render_template('vehicles/form.html', vehicle=None)


@vehicles_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if request.method == 'POST':
        vehicle.registration_plate = request.form['registration_plate']
        vehicle.vehicle_type = request.form['vehicle_type']
        vehicle.brand = request.form.get('brand')
        vehicle.model = request.form.get('model')
        vehicle.year = _parse_int(request.form.get('year'))
        vehicle.mileage = _parse_int(request.form.get('mileage')) or 0
        vehicle.insurance_number = request.form.get('insurance_number')
        vehicle.insurance_expiry = _parse_date(request.form.get('insurance_expiry'))
        vehicle.technical_control_date = _parse_date(request.form.get('technical_control_date'))
        vehicle.technical_control_expiry = _parse_date(request.form.get('technical_control_expiry'))
        vehicle.last_maintenance_date = _parse_date(request.form.get('last_maintenance_date'))
        vehicle.next_maintenance_date = _parse_date(request.form.get('next_maintenance_date'))
        vehicle.status = request.form.get('status', 'available')
        vehicle.notes = request.form.get('notes')
        db.session.commit()
        flash('Véhicule mis à jour.', 'success')
        return redirect(url_for('vehicles.list_vehicles'))
    return render_template('vehicles/form.html', vehicle=vehicle)


def _parse_date(value):
    if not value:
        return None
    from datetime import datetime
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_int(value):
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None
