from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Driver
from .. import db

drivers_bp = Blueprint('drivers', __name__)


@drivers_bp.route('/')
def list_drivers():
    drivers = Driver.query.order_by(Driver.last_name).all()
    return render_template('drivers/list.html', drivers=drivers)


@drivers_bp.route('/new', methods=['GET', 'POST'])
def new_driver():
    if request.method == 'POST':
        driver = Driver(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form['phone'],
            email=request.form.get('email'),
            license_number=request.form.get('license_number'),
            license_expiry=_parse_date(request.form.get('license_expiry')),
            vsl_card_number=request.form.get('vsl_card_number'),
            vsl_card_expiry=_parse_date(request.form.get('vsl_card_expiry')),
            ambulance_card_number=request.form.get('ambulance_card_number'),
            ambulance_card_expiry=_parse_date(request.form.get('ambulance_card_expiry')),
            contract_type=request.form.get('contract_type'),
            hire_date=_parse_date(request.form.get('hire_date')),
            status=request.form.get('status', 'active'),
            notes=request.form.get('notes'),
        )
        db.session.add(driver)
        db.session.commit()
        flash('Chauffeur créé avec succès.', 'success')
        return redirect(url_for('drivers.list_drivers'))
    return render_template('drivers/form.html', driver=None)


@drivers_bp.route('/<int:driver_id>/edit', methods=['GET', 'POST'])
def edit_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    if request.method == 'POST':
        driver.first_name = request.form['first_name']
        driver.last_name = request.form['last_name']
        driver.phone = request.form['phone']
        driver.email = request.form.get('email')
        driver.license_number = request.form.get('license_number')
        driver.license_expiry = _parse_date(request.form.get('license_expiry'))
        driver.vsl_card_number = request.form.get('vsl_card_number')
        driver.vsl_card_expiry = _parse_date(request.form.get('vsl_card_expiry'))
        driver.ambulance_card_number = request.form.get('ambulance_card_number')
        driver.ambulance_card_expiry = _parse_date(request.form.get('ambulance_card_expiry'))
        driver.contract_type = request.form.get('contract_type')
        driver.hire_date = _parse_date(request.form.get('hire_date'))
        driver.status = request.form.get('status', 'active')
        driver.notes = request.form.get('notes')
        db.session.commit()
        flash('Chauffeur mis à jour.', 'success')
        return redirect(url_for('drivers.list_drivers'))
    return render_template('drivers/form.html', driver=driver)


def _parse_date(value):
    if not value:
        return None
    from datetime import datetime
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None
