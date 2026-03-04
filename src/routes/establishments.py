from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models import Establishment
from src.database import db

establishments_bp = Blueprint("establishments", __name__, url_prefix="/api/establishments")


@establishments_bp.route("", methods=["GET"])
@jwt_required()
def list_establishments():
    q = request.args.get("q", "")
    query = Establishment.query
    if q:
        query = query.filter(Establishment.name.ilike(f"%{q}%"))
    establishments = query.order_by(Establishment.name).all()
    return jsonify([e.to_dict() for e in establishments]), 200


@establishments_bp.route("/<int:establishment_id>", methods=["GET"])
@jwt_required()
def get_establishment(establishment_id):
    establishment = Establishment.query.get_or_404(establishment_id)
    return jsonify(establishment.to_dict()), 200


@establishments_bp.route("", methods=["POST"])
@jwt_required()
def create_establishment():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    establishment = Establishment(
        name=data["name"],
        establishment_type=data.get("establishment_type"),
        address=data.get("address"),
        postal_code=data.get("postal_code"),
        city=data.get("city"),
        phone=data.get("phone"),
        email=data.get("email"),
    )
    db.session.add(establishment)
    db.session.commit()
    return jsonify(establishment.to_dict()), 201
