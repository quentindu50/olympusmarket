from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from src.models import Mission, MissionStatus, TransportType
from src.database import db
from src.services.mission_service import update_mission_status, get_daily_missions

missions_bp = Blueprint("missions", __name__, url_prefix="/api/missions")

VALID_STATUS_TRANSITIONS = {
    MissionStatus.PENDING: [MissionStatus.ASSIGNED, MissionStatus.CANCELLED],
    MissionStatus.ASSIGNED: [MissionStatus.STARTED, MissionStatus.CANCELLED],
    MissionStatus.STARTED: [MissionStatus.ON_SITE, MissionStatus.CANCELLED],
    MissionStatus.ON_SITE: [MissionStatus.PATIENT_ONBOARD, MissionStatus.DROPPED, MissionStatus.CANCELLED],
    MissionStatus.PATIENT_ONBOARD: [MissionStatus.DROPPED, MissionStatus.CANCELLED],
    MissionStatus.DROPPED: [MissionStatus.FINISHED],
    MissionStatus.FINISHED: [],
    MissionStatus.CANCELLED: [],
}


@missions_bp.route("", methods=["GET"])
@jwt_required()
def list_missions():
    date_str = request.args.get("date")
    status = request.args.get("status")
    driver_id = request.args.get("driver_id")
    query = Mission.query
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            missions = get_daily_missions(date)
            return jsonify([m.to_dict() for m in missions]), 200
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if status:
        try:
            query = query.filter_by(status=MissionStatus(status))
        except ValueError:
            return jsonify({"error": "Invalid status"}), 400
    if driver_id:
        query = query.filter_by(driver_id=int(driver_id))
    missions = query.order_by(Mission.scheduled_pickup_time).all()
    return jsonify([m.to_dict() for m in missions]), 200


@missions_bp.route("/<int:mission_id>", methods=["GET"])
@jwt_required()
def get_mission(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    return jsonify(mission.to_dict()), 200


@missions_bp.route("", methods=["POST"])
@jwt_required()
def create_mission():
    data = request.get_json()
    required = ["patient_id", "transport_type", "pickup_address", "destination_address", "scheduled_pickup_time"]
    for field in required:
        if not data or field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    try:
        tt = TransportType(data["transport_type"])
    except ValueError:
        return jsonify({"error": "Invalid transport_type"}), 400
    try:
        pickup_time = datetime.fromisoformat(data["scheduled_pickup_time"])
    except ValueError:
        return jsonify({"error": "Invalid scheduled_pickup_time format"}), 400
    mission = Mission(
        patient_id=data["patient_id"],
        driver_id=data.get("driver_id"),
        vehicle_id=data.get("vehicle_id"),
        transport_type=tt,
        pickup_address=data["pickup_address"],
        pickup_city=data.get("pickup_city"),
        destination_address=data["destination_address"],
        destination_city=data.get("destination_city"),
        scheduled_pickup_time=pickup_time,
        reason=data.get("reason"),
        is_recurring=data.get("is_recurring", False),
        recurrence_pattern=data.get("recurrence_pattern"),
        distance_km=data.get("distance_km"),
        notes=data.get("notes"),
    )
    db.session.add(mission)
    db.session.commit()
    return jsonify(mission.to_dict()), 201


@missions_bp.route("/<int:mission_id>/status", methods=["PUT"])
@jwt_required()
def update_status(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    data = request.get_json() or {}
    if "status" not in data:
        return jsonify({"error": "status is required"}), 400
    try:
        new_status = MissionStatus(data["status"])
    except ValueError:
        return jsonify({"error": "Invalid status"}), 400
    allowed = VALID_STATUS_TRANSITIONS.get(mission.status, [])
    if new_status not in allowed:
        return jsonify({
            "error": f"Cannot transition from {mission.status.value} to {new_status.value}"
        }), 422
    lat = data.get("lat")
    lon = data.get("lon")
    updated, error = update_mission_status(mission_id, new_status, lat=lat, lon=lon)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(updated.to_dict()), 200


@missions_bp.route("/<int:mission_id>", methods=["PUT"])
@jwt_required()
def update_mission(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    data = request.get_json() or {}
    for field in ["driver_id", "vehicle_id", "reason", "notes", "distance_km",
                  "has_transport_slip", "has_prescription"]:
        if field in data:
            setattr(mission, field, data[field])
    db.session.commit()
    return jsonify(mission.to_dict()), 200
