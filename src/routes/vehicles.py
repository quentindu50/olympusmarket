from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models import Vehicle, TransportType
from src.database import db

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/api/vehicles")


@vehicles_bp.route("", methods=["GET"])
@jwt_required()
def list_vehicles():
    available_only = request.args.get("available") == "true"
    transport_type = request.args.get("type")
    query = Vehicle.query
    if available_only:
        query = query.filter_by(is_available=True)
    if transport_type:
        try:
            tt = TransportType(transport_type)
            query = query.filter_by(transport_type=tt)
        except ValueError:
            return jsonify({"error": "Invalid transport type"}), 400
    vehicles = query.all()
    return jsonify([v.to_dict() for v in vehicles]), 200


@vehicles_bp.route("/<int:vehicle_id>", methods=["GET"])
@jwt_required()
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(vehicle.to_dict()), 200


@vehicles_bp.route("", methods=["POST"])
@jwt_required()
def create_vehicle():
    data = request.get_json()
    if not data or not data.get("license_plate") or not data.get("transport_type"):
        return jsonify({"error": "license_plate and transport_type are required"}), 400
    try:
        tt = TransportType(data["transport_type"])
    except ValueError:
        return jsonify({"error": "Invalid transport_type"}), 400
    vehicle = Vehicle(
        license_plate=data["license_plate"],
        transport_type=tt,
        brand=data.get("brand"),
        model=data.get("model"),
        year=data.get("year"),
        mileage=data.get("mileage", 0),
    )
    db.session.add(vehicle)
    db.session.commit()
    return jsonify(vehicle.to_dict()), 201


@vehicles_bp.route("/<int:vehicle_id>/mileage", methods=["PUT"])
@jwt_required()
def update_mileage(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json() or {}
    if "mileage" not in data:
        return jsonify({"error": "mileage required"}), 400
    vehicle.mileage = float(data["mileage"])
    db.session.commit()
    return jsonify(vehicle.to_dict()), 200
