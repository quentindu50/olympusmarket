from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
import uuid
from src.models import Invoice, Mission, MissionStatus
from src.database import db

invoices_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


def _generate_invoice_number():
    """Generate a unique invoice number using timestamp + UUID to avoid race conditions."""
    now = datetime.utcnow()
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"INV-{now.year}{now.month:02d}-{unique_suffix}"


@invoices_bp.route("", methods=["GET"])
@jwt_required()
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invoices]), 200


@invoices_bp.route("/<int:invoice_id>", methods=["GET"])
@jwt_required()
def get_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return jsonify(invoice.to_dict()), 200


@invoices_bp.route("", methods=["POST"])
@jwt_required()
def create_invoice():
    data = request.get_json()
    if not data or not data.get("mission_id"):
        return jsonify({"error": "mission_id is required"}), 400
    mission = Mission.query.get_or_404(data["mission_id"])
    if mission.status != MissionStatus.FINISHED:
        return jsonify({"error": "Mission must be finished before invoicing"}), 422
    invoice = Invoice(
        mission_id=mission.id,
        invoice_number=_generate_invoice_number(),
        amount_total=data.get("amount_total", 0),
        amount_amo=data.get("amount_amo", 0),
        amount_amc=data.get("amount_amc", 0),
        amount_patient=data.get("amount_patient", 0),
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify(invoice.to_dict()), 201


@invoices_bp.route("/<int:invoice_id>/transmit", methods=["PUT"])
@jwt_required()
def transmit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.is_transmitted = True
    db.session.commit()
    return jsonify(invoice.to_dict()), 200


@invoices_bp.route("/<int:invoice_id>/paid", methods=["PUT"])
@jwt_required()
def mark_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.is_paid = True
    db.session.commit()
    return jsonify(invoice.to_dict()), 200
