from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Invoice, Mission

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def _generate_invoice_number():
    last = Invoice.query.order_by(Invoice.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"FAC-{next_id:05d}"


@billing_bp.route("/")
def index():
    status_filter = request.args.get("status", "")
    query = Invoice.query.order_by(Invoice.issued_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    invoices = query.all()
    return render_template(
        "billing/index.html", invoices=invoices, status_filter=status_filter
    )


@billing_bp.route("/new/<int:mission_id>", methods=["GET", "POST"])
def new(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    if request.method == "POST":
        amount_base = float(request.form.get("amount_base", 0))
        amount_surcharges = float(request.form.get("amount_surcharges", 0))
        invoice = Invoice(
            mission_id=mission_id,
            invoice_number=_generate_invoice_number(),
            amount_base=amount_base,
            amount_surcharges=amount_surcharges,
            amount_total=amount_base + amount_surcharges,
            notes=request.form.get("notes", ""),
        )
        db.session.add(invoice)
        db.session.commit()
        flash("Facture créée avec succès.", "success")
        return redirect(url_for("billing.index"))
    return render_template("billing/form.html", mission=mission)


@billing_bp.route("/<int:invoice_id>")
def detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template("billing/detail.html", invoice=invoice)


@billing_bp.route("/<int:invoice_id>/status", methods=["POST"])
def update_status(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    new_status = request.form.get("status")
    if new_status in [
        Invoice.STATUS_DRAFT,
        Invoice.STATUS_SENT,
        Invoice.STATUS_PAID,
        Invoice.STATUS_REJECTED,
    ]:
        invoice.status = new_status
        if new_status == Invoice.STATUS_PAID:
            from datetime import datetime
            invoice.paid_at = datetime.utcnow()
        db.session.commit()
        flash("Statut de la facture mis à jour.", "success")
    return redirect(url_for("billing.detail", invoice_id=invoice_id))
