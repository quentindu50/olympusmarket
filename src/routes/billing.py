from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Billing, Transport
from datetime import date

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')


def _parse_date(val):
    if val:
        try:
            return date.fromisoformat(val)
        except ValueError:
            return None
    return None


@billing_bp.route('/')
def list():
    records = Billing.query.order_by(Billing.created_at.desc()).all()
    total = sum(r.amount for r in records if r.amount)
    total_paid = sum(r.amount for r in records if r.paid and r.amount)
    total_unpaid = total - total_paid
    return render_template('billing/list.html', records=records,
                           total=total, total_paid=total_paid, total_unpaid=total_unpaid)


@billing_bp.route('/new', methods=['GET', 'POST'])
def create():
    transports = Transport.query.order_by(Transport.scheduled_at.desc()).all()
    if request.method == 'POST':
        record = Billing(
            transport_id=request.form['transport_id'],
            amount=float(request.form.get('amount') or 0),
            tiers_payant='tiers_payant' in request.form,
            cpam_transmitted='cpam_transmitted' in request.form,
            paid='paid' in request.form,
            payment_date=_parse_date(request.form.get('payment_date')),
            notes=request.form.get('notes', ''),
        )
        db.session.add(record)
        db.session.commit()
        flash('Facturation créée avec succès.', 'success')
        return redirect(url_for('billing.list'))
    return render_template('billing/form.html', record=None, transports=transports)


@billing_bp.route('/<int:billing_id>/edit', methods=['GET', 'POST'])
def edit(billing_id):
    record = Billing.query.get_or_404(billing_id)
    transports = Transport.query.order_by(Transport.scheduled_at.desc()).all()
    if request.method == 'POST':
        record.transport_id = request.form['transport_id']
        record.amount = float(request.form.get('amount') or 0)
        record.tiers_payant = 'tiers_payant' in request.form
        record.cpam_transmitted = 'cpam_transmitted' in request.form
        record.paid = 'paid' in request.form
        record.payment_date = _parse_date(request.form.get('payment_date'))
        record.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Facturation mise à jour.', 'success')
        return redirect(url_for('billing.list'))
    return render_template('billing/form.html', record=record, transports=transports)


@billing_bp.route('/<int:billing_id>/paid', methods=['POST'])
def mark_paid(billing_id):
    record = Billing.query.get_or_404(billing_id)
    record.paid = True
    record.payment_date = date.today()
    db.session.commit()
    flash('Paiement enregistré.', 'success')
    return redirect(url_for('billing.list'))
