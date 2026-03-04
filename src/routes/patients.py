from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Patient, Transport

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')


@patients_bp.route('/')
def list():
    search = request.args.get('q', '')
    query = Patient.query
    if search:
        query = query.filter(
            (Patient.first_name.ilike(f'%{search}%')) |
            (Patient.last_name.ilike(f'%{search}%')) |
            (Patient.phone.ilike(f'%{search}%'))
        )
    patients = query.order_by(Patient.last_name).all()
    return render_template('patients/list.html', patients=patients, search=search)


@patients_bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        patient = Patient(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            social_security_number=request.form.get('social_security_number', ''),
            ald='ald' in request.form,
            mutual_insurance=request.form.get('mutual_insurance', ''),
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            doctor_name=request.form.get('doctor_name', ''),
            doctor_phone=request.form.get('doctor_phone', ''),
            notes=request.form.get('notes', ''),
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient créé avec succès.', 'success')
        return redirect(url_for('patients.list'))
    return render_template('patients/form.html', patient=None)


@patients_bp.route('/<int:patient_id>')
def detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    transports = Transport.query.filter_by(patient_id=patient_id).order_by(Transport.scheduled_at.desc()).all()
    return render_template('patients/detail.html', patient=patient, transports=transports)


@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.social_security_number = request.form.get('social_security_number', '')
        patient.ald = 'ald' in request.form
        patient.mutual_insurance = request.form.get('mutual_insurance', '')
        patient.phone = request.form.get('phone', '')
        patient.address = request.form.get('address', '')
        patient.doctor_name = request.form.get('doctor_name', '')
        patient.doctor_phone = request.form.get('doctor_phone', '')
        patient.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Patient mis à jour avec succès.', 'success')
        return redirect(url_for('patients.detail', patient_id=patient.id))
    return render_template('patients/form.html', patient=patient)


@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
def delete(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient supprimé.', 'warning')
    return redirect(url_for('patients.list'))
