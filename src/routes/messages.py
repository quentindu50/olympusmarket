from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import Message
from src.database import db

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@messages_bp.route("", methods=["GET"])
@jwt_required()
def list_messages():
    user_id = int(get_jwt_identity())
    mission_id = request.args.get("mission_id")
    query = Message.query.filter(
        (Message.sender_id == user_id) | (Message.recipient_id == user_id)
    )
    if mission_id:
        query = query.filter_by(mission_id=int(mission_id))
    messages = query.order_by(Message.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages]), 200


@messages_bp.route("", methods=["POST"])
@jwt_required()
def send_message():
    sender_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"error": "content is required"}), 400
    message = Message(
        sender_id=sender_id,
        recipient_id=data.get("recipient_id"),
        mission_id=data.get("mission_id"),
        content=data["content"],
        is_urgent=data.get("is_urgent", False),
    )
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict()), 201


@messages_bp.route("/<int:message_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(message_id):
    message = Message.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return jsonify(message.to_dict()), 200
