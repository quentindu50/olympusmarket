from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Patient
from .. import db

patients_bp = Blueprint('patients', __name__)


@patients_bp.route('/')
def list_patients():
    search = request.args.get('search', '')
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (Patient.social_security_number.ilike(f'%{search}%'))
        )
    patients = query.order_by(Patient.last_name).all()
    return render_template('patients/list.html', patients=patients, search=search)


@patients_bp.route('/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        patient = Patient(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            date_of_birth=_parse_date(request.form.get('date_of_birth')),
            social_security_number=request.form.get('social_security_number'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            postal_code=request.form.get('postal_code'),
            ald=bool(request.form.get('ald')),
            mutual_insurance=request.form.get('mutual_insurance'),
            prescribing_doctor=request.form.get('prescribing_doctor'),
            allergies=request.form.get('allergies'),
            notes=request.form.get('notes'),
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient créé avec succès.', 'success')
        return redirect(url_for('patients.list_patients'))
    return render_template('patients/form.html', patient=None)


@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.date_of_birth = _parse_date(request.form.get('date_of_birth'))
        patient.social_security_number = request.form.get('social_security_number')
        patient.phone = request.form.get('phone')
        patient.email = request.form.get('email')
        patient.address = request.form.get('address')
        patient.city = request.form.get('city')
        patient.postal_code = request.form.get('postal_code')
        patient.ald = bool(request.form.get('ald'))
        patient.mutual_insurance = request.form.get('mutual_insurance')
        patient.prescribing_doctor = request.form.get('prescribing_doctor')
        patient.allergies = request.form.get('allergies')
        patient.notes = request.form.get('notes')
        db.session.commit()
        flash('Patient mis à jour avec succès.', 'success')
        return redirect(url_for('patients.list_patients'))
    return render_template('patients/form.html', patient=patient)


@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if patient.transports:
        flash('Impossible de supprimer ce patient : il a des transports associés.', 'danger')
        return redirect(url_for('patients.list_patients'))
    db.session.delete(patient)
    db.session.commit()
    flash('Patient supprimé.', 'warning')
    return redirect(url_for('patients.list_patients'))


def _parse_date(value):
    if not value:
        return None
    from datetime import datetime
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None
