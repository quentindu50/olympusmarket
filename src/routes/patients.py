from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models import Patient
from src.database import db

patients_bp = Blueprint("patients", __name__, url_prefix="/api/patients")


@patients_bp.route("", methods=["GET"])
@jwt_required()
def list_patients():
    q = request.args.get("q", "")
    query = Patient.query
    if q:
        query = query.filter(
            (Patient.last_name.ilike(f"%{q}%")) | (Patient.first_name.ilike(f"%{q}%"))
        )
    patients = query.order_by(Patient.last_name).all()
    return jsonify([p.to_dict() for p in patients]), 200


@patients_bp.route("/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify(patient.to_dict()), 200


@patients_bp.route("", methods=["POST"])
@jwt_required()
def create_patient():
    data = request.get_json()
    if not data or not data.get("first_name") or not data.get("last_name"):
        return jsonify({"error": "first_name and last_name are required"}), 400

    patient = Patient(
        first_name=data["first_name"],
        last_name=data["last_name"],
        social_security_number=data.get("social_security_number"),
        phone=data.get("phone"),
        address=data.get("address"),
        postal_code=data.get("postal_code"),
        city=data.get("city"),
        amo=data.get("amo"),
        amc=data.get("amc"),
        has_ald=data.get("has_ald", False),
        allergies=data.get("allergies"),
        notes=data.get("notes"),
        prescriber_name=data.get("prescriber_name"),
        prescriber_phone=data.get("prescriber_phone"),
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


@patients_bp.route("/<int:patient_id>", methods=["PUT"])
@jwt_required()
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json() or {}
    for field in [
        "first_name", "last_name", "social_security_number", "phone",
        "address", "postal_code", "city", "amo", "amc", "has_ald",
        "allergies", "notes", "prescriber_name", "prescriber_phone",
    ]:
        if field in data:
            setattr(patient, field, data[field])
    db.session.commit()
    return jsonify(patient.to_dict()), 200
