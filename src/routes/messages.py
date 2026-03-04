from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Message, Transport

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'POST':
        message = Message(
            sender_name=request.form['sender_name'],
            content=request.form['content'],
            urgent='urgent' in request.form,
            transport_id=request.form.get('transport_id') or None,
        )
        db.session.add(message)
        db.session.commit()
        flash('Message envoyé.', 'success')
        return redirect(url_for('messages.list'))
    messages = Message.query.order_by(Message.created_at.desc()).all()
    transports = Transport.query.order_by(Transport.scheduled_at.desc()).limit(50).all()
    return render_template('messages/list.html', messages=messages, transports=transports)
