from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Message, Driver, Mission

messaging_bp = Blueprint("messaging", __name__, url_prefix="/messaging")


@messaging_bp.route("/")
def index():
    messages = Message.query.order_by(Message.sent_at.desc()).all()
    unread_count = Message.query.filter_by(is_read=False).count()
    return render_template(
        "messaging/index.html", messages=messages, unread_count=unread_count
    )


@messaging_bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        message = Message(
            sender_id=request.form.get("sender_id") or None,
            content=request.form.get("content", ""),
            mission_id=request.form.get("mission_id") or None,
        )
        db.session.add(message)
        db.session.commit()
        flash("Message envoyé.", "success")
        return redirect(url_for("messaging.index"))
    drivers = Driver.query.filter_by(is_active=True).order_by(Driver.last_name).all()
    missions = Mission.query.order_by(Mission.scheduled_at.desc()).limit(50).all()
    return render_template("messaging/form.html", drivers=drivers, missions=missions)


@messaging_bp.route("/<int:message_id>/read", methods=["POST"])
def mark_read(message_id):
    message = Message.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return redirect(url_for("messaging.index"))
