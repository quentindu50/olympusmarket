from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Transport, Patient, Driver, Vehicle
from datetime import datetime

transports_bp = Blueprint('transports', __name__, url_prefix='/transports')


def _parse_dt(val):
    if val:
        try:
            return datetime.fromisoformat(val)
        except ValueError:
            return None
    return None


@transports_bp.route('/')
def list():
    status_filter = request.args.get('status', '')
    type_filter = request.args.get('type', '')
    date_filter = request.args.get('date', '')

    query = Transport.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if type_filter:
        query = query.filter_by(transport_type=type_filter)
    if date_filter:
        try:
            from sqlalchemy import func
            d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(func.date(Transport.scheduled_at) == d)
        except ValueError:
            pass
    transports = query.order_by(Transport.scheduled_at.desc()).all()
    return render_template('transports/list.html', transports=transports,
                           status_filter=status_filter, type_filter=type_filter,
                           date_filter=date_filter)


@transports_bp.route('/new', methods=['GET', 'POST'])
def create():
    patients = Patient.query.order_by(Patient.last_name).all()
    drivers = Driver.query.order_by(Driver.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.registration).all()
    if request.method == 'POST':
        transport = Transport(
            patient_id=request.form['patient_id'],
            driver_id=request.form.get('driver_id') or None,
            vehicle_id=request.form.get('vehicle_id') or None,
            transport_type=request.form['transport_type'],
            pickup_address=request.form['pickup_address'],
            destination=request.form['destination'],
            scheduled_at=_parse_dt(request.form['scheduled_at']),
            return_scheduled_at=_parse_dt(request.form.get('return_scheduled_at')),
            reason=request.form.get('reason', ''),
            status=request.form.get('status', 'pending'),
            recurrent='recurrent' in request.form,
            recurrence_pattern=request.form.get('recurrence_pattern', ''),
            notes=request.form.get('notes', ''),
        )
        db.session.add(transport)
        db.session.commit()
        flash('Transport créé avec succès.', 'success')
        return redirect(url_for('transports.list'))
    return render_template('transports/form.html', transport=None,
                           patients=patients, drivers=drivers, vehicles=vehicles)


@transports_bp.route('/<int:transport_id>')
def detail(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    return redirect(url_for('transports.edit', transport_id=transport_id))


@transports_bp.route('/<int:transport_id>/edit', methods=['GET', 'POST'])
def edit(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    patients = Patient.query.order_by(Patient.last_name).all()
    drivers = Driver.query.order_by(Driver.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.registration).all()
    if request.method == 'POST':
        transport.patient_id = request.form['patient_id']
        transport.driver_id = request.form.get('driver_id') or None
        transport.vehicle_id = request.form.get('vehicle_id') or None
        transport.transport_type = request.form['transport_type']
        transport.pickup_address = request.form['pickup_address']
        transport.destination = request.form['destination']
        transport.scheduled_at = _parse_dt(request.form['scheduled_at'])
        transport.return_scheduled_at = _parse_dt(request.form.get('return_scheduled_at'))
        transport.reason = request.form.get('reason', '')
        transport.status = request.form.get('status', 'pending')
        transport.recurrent = 'recurrent' in request.form
        transport.recurrence_pattern = request.form.get('recurrence_pattern', '')
        transport.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Transport mis à jour.', 'success')
        return redirect(url_for('transports.list'))
    return render_template('transports/form.html', transport=transport,
                           patients=patients, drivers=drivers, vehicles=vehicles)


@transports_bp.route('/<int:transport_id>/status', methods=['POST'])
def update_status(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    transport.status = request.form['status']
    db.session.commit()
    flash('Statut mis à jour.', 'success')
    return redirect(url_for('transports.list'))


@transports_bp.route('/<int:transport_id>/delete', methods=['POST'])
def delete(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    db.session.delete(transport)
    db.session.commit()
    flash('Transport supprimé.', 'warning')
    return redirect(url_for('transports.list'))
