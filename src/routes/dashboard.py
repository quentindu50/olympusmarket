from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from src.services.mission_service import get_dashboard_stats
from src.models import Driver, Vehicle

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("", methods=["GET"])
@jwt_required()
def dashboard():
    stats = get_dashboard_stats()
    stats["available_drivers"] = Driver.query.filter_by(is_available=True).count()
    stats["available_vehicles"] = Vehicle.query.filter_by(is_available=True).count()
    return jsonify(stats), 200
