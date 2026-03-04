from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from ..models import Transport, Patient, Driver, Vehicle, Establishment, Invoice
from .. import db

transports_bp = Blueprint('transports', __name__)


@transports_bp.route('/')
def list_transports():
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    query = Transport.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if date_filter:
        try:
            d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            day_start = datetime.combine(d, datetime.min.time())
            day_end = datetime.combine(d, datetime.max.time())
            query = query.filter(
                Transport.scheduled_datetime >= day_start,
                Transport.scheduled_datetime <= day_end,
            )
        except ValueError:
            pass
    transports = query.order_by(Transport.scheduled_datetime.desc()).all()
    return render_template(
        'transports/list.html',
        transports=transports,
        status_filter=status_filter,
        date_filter=date_filter,
        statuses=Transport.STATUSES,
    )


@transports_bp.route('/new', methods=['GET', 'POST'])
def new_transport():
    if request.method == 'POST':
        transport = Transport(
            patient_id=int(request.form['patient_id']),
            driver_id=_parse_int(request.form.get('driver_id')),
            vehicle_id=_parse_int(request.form.get('vehicle_id')),
            destination_establishment_id=_parse_int(request.form.get('destination_establishment_id')),
            transport_type=request.form['transport_type'],
            pickup_address=request.form['pickup_address'],
            pickup_city=request.form.get('pickup_city'),
            destination_address=request.form['destination_address'],
            destination_city=request.form.get('destination_city'),
            scheduled_datetime=datetime.strptime(request.form['scheduled_datetime'], '%Y-%m-%dT%H:%M'),
            return_datetime=_parse_datetime(request.form.get('return_datetime')),
            reason=request.form.get('reason'),
            priority=request.form.get('priority', 'normal'),
            status=request.form.get('status', 'scheduled'),
            distance_km=_parse_float(request.form.get('distance_km')),
            recurrence=request.form.get('recurrence'),
            notes=request.form.get('notes'),
        )
        db.session.add(transport)
        db.session.commit()
        flash('Transport créé avec succès.', 'success')
        return redirect(url_for('transports.list_transports'))
    patients = Patient.query.order_by(Patient.last_name).all()
    drivers = Driver.query.filter_by(status='active').order_by(Driver.last_name).all()
    vehicles = Vehicle.query.filter_by(status='available').order_by(Vehicle.registration_plate).all()
    establishments = Establishment.query.order_by(Establishment.name).all()
    return render_template(
        'transports/form.html',
        transport=None,
        patients=patients,
        drivers=drivers,
        vehicles=vehicles,
        establishments=establishments,
    )


@transports_bp.route('/<int:transport_id>/edit', methods=['GET', 'POST'])
def edit_transport(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    if request.method == 'POST':
        transport.patient_id = int(request.form['patient_id'])
        transport.driver_id = _parse_int(request.form.get('driver_id'))
        transport.vehicle_id = _parse_int(request.form.get('vehicle_id'))
        transport.destination_establishment_id = _parse_int(request.form.get('destination_establishment_id'))
        transport.transport_type = request.form['transport_type']
        transport.pickup_address = request.form['pickup_address']
        transport.pickup_city = request.form.get('pickup_city')
        transport.destination_address = request.form['destination_address']
        transport.destination_city = request.form.get('destination_city')
        transport.scheduled_datetime = datetime.strptime(request.form['scheduled_datetime'], '%Y-%m-%dT%H:%M')
        transport.return_datetime = _parse_datetime(request.form.get('return_datetime'))
        transport.reason = request.form.get('reason')
        transport.priority = request.form.get('priority', 'normal')
        transport.status = request.form.get('status', 'scheduled')
        transport.distance_km = _parse_float(request.form.get('distance_km'))
        transport.recurrence = request.form.get('recurrence')
        transport.notes = request.form.get('notes')
        db.session.commit()
        flash('Transport mis à jour.', 'success')
        return redirect(url_for('transports.list_transports'))
    patients = Patient.query.order_by(Patient.last_name).all()
    drivers = Driver.query.filter_by(status='active').order_by(Driver.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.registration_plate).all()
    establishments = Establishment.query.order_by(Establishment.name).all()
    return render_template(
        'transports/form.html',
        transport=transport,
        patients=patients,
        drivers=drivers,
        vehicles=vehicles,
        establishments=establishments,
    )


@transports_bp.route('/<int:transport_id>/status', methods=['POST'])
def update_status(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    new_status = request.form.get('status')
    if new_status in [s[0] for s in Transport.STATUSES]:
        transport.status = new_status
        db.session.commit()
        flash('Statut mis à jour.', 'success')
    return redirect(url_for('transports.list_transports'))


def _parse_int(value):
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None


def _parse_float(value):
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M')
    except ValueError:
        return None
