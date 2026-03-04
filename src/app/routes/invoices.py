from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from ..models import Invoice, Transport
from .. import db

invoices_bp = Blueprint('invoices', __name__)


@invoices_bp.route('/')
def list_invoices():
    status_filter = request.args.get('status', '')
    query = Invoice.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    invoices = query.order_by(Invoice.issue_date.desc()).all()
    return render_template(
        'invoices/list.html',
        invoices=invoices,
        status_filter=status_filter,
        statuses=Invoice.STATUSES,
    )


@invoices_bp.route('/generate/<int:transport_id>', methods=['POST'])
def generate_invoice(transport_id):
    transport = Transport.query.get_or_404(transport_id)
    if transport.invoice:
        flash('Une facture existe déjà pour ce transport.', 'warning')
        return redirect(url_for('invoices.list_invoices'))
    invoice = Invoice(
        transport_id=transport_id,
        invoice_number=Invoice.generate_invoice_number(),
        issue_date=datetime.utcnow().date(),
        base_amount=float(request.form.get('base_amount', 0)),
        km_amount=float(request.form.get('km_amount', 0)),
        supplement_amount=float(request.form.get('supplement_amount', 0)),
        total_amount=float(request.form.get('total_amount', 0)),
        cpam_amount=float(request.form.get('cpam_amount', 0)),
        mutual_amount=float(request.form.get('mutual_amount', 0)),
        patient_amount=float(request.form.get('patient_amount', 0)),
        status='pending',
    )
    db.session.add(invoice)
    db.session.commit()
    flash(f'Facture {invoice.invoice_number} créée.', 'success')
    return redirect(url_for('invoices.list_invoices'))


@invoices_bp.route('/<int:invoice_id>/pay', methods=['POST'])
def mark_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.status = 'paid'
    invoice.payment_date = datetime.utcnow().date()
    invoice.payment_method = request.form.get('payment_method', 'virement')
    db.session.commit()
    flash('Facture marquée comme payée.', 'success')
    return redirect(url_for('invoices.list_invoices'))
