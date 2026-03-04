from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Driver

drivers_bp = Blueprint('drivers', __name__, url_prefix='/drivers')


@drivers_bp.route('/')
def list():
    drivers = Driver.query.order_by(Driver.last_name).all()
    return render_template('drivers/list.html', drivers=drivers)


@drivers_bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        driver = Driver(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            license_number=request.form.get('license_number', ''),
            vsl_card='vsl_card' in request.form,
            ambulance_card='ambulance_card' in request.form,
            status=request.form.get('status', 'available'),
            notes=request.form.get('notes', ''),
        )
        db.session.add(driver)
        db.session.commit()
        flash('Chauffeur créé avec succès.', 'success')
        return redirect(url_for('drivers.list'))
    return render_template('drivers/form.html', driver=None)


@drivers_bp.route('/<int:driver_id>')
def detail(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return render_template('drivers/form.html', driver=driver, readonly=True)


@drivers_bp.route('/<int:driver_id>/edit', methods=['GET', 'POST'])
def edit(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    if request.method == 'POST':
        driver.first_name = request.form['first_name']
        driver.last_name = request.form['last_name']
        driver.phone = request.form.get('phone', '')
        driver.email = request.form.get('email', '')
        driver.license_number = request.form.get('license_number', '')
        driver.vsl_card = 'vsl_card' in request.form
        driver.ambulance_card = 'ambulance_card' in request.form
        driver.status = request.form.get('status', 'available')
        driver.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Chauffeur mis à jour avec succès.', 'success')
        return redirect(url_for('drivers.list'))
    return render_template('drivers/form.html', driver=driver)


@drivers_bp.route('/<int:driver_id>/delete', methods=['POST'])
def delete(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    db.session.delete(driver)
    db.session.commit()
    flash('Chauffeur supprimé.', 'warning')
    return redirect(url_for('drivers.list'))
