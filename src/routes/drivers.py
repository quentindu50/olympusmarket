from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models import Driver, User, UserRole
from src.database import db

drivers_bp = Blueprint("drivers", __name__, url_prefix="/api/drivers")


@drivers_bp.route("", methods=["GET"])
@jwt_required()
def list_drivers():
    available_only = request.args.get("available") == "true"
    query = Driver.query
    if available_only:
        query = query.filter_by(is_available=True)
    drivers = query.all()
    return jsonify([d.to_dict() for d in drivers]), 200


@drivers_bp.route("/<int:driver_id>", methods=["GET"])
@jwt_required()
def get_driver(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    return jsonify(driver.to_dict()), 200


@drivers_bp.route("/<int:driver_id>/availability", methods=["PUT"])
@jwt_required()
def set_availability(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    data = request.get_json() or {}
    if "is_available" not in data:
        return jsonify({"error": "is_available required"}), 400
    driver.is_available = bool(data["is_available"])
    db.session.commit()
    return jsonify(driver.to_dict()), 200
