"""
crm.py — Setter-only routes. Uses log_activity() from models.
"""
from datetime import date, datetime, timedelta

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models import db, Call, Lead, log_activity

crm_bp = Blueprint("crm", __name__, url_prefix="/crm")

STATUS_LABELS = {
    "new_lead":    "New Lead",
    "messaged":    "Messaged",
    "replied":     "Replied",
    "interested":  "Interested",
    "call_booked": "Call Booked",
    "deal_done":   "Deal Done",
}

# ── decorators ────────────────────────────────────────────────────────────────

def setter_required(fn):
    from functools import wraps
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return fn(*args, **kwargs)
    return wrapper


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def _guard(lead: Lead):
    if not current_user.is_admin and lead.assigned_to != current_user.id:
        abort(403)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@crm_bp.route("/dashboard")
@setter_required
def dashboard():
    today = date.today()
    now   = datetime.now()

    my_leads = (
        Lead.query
        .filter_by(assigned_to=current_user.id)
        .options(joinedload(Lead.call))
        .order_by(Lead.next_followup.asc().nullslast(), Lead.created_at.desc())
        .all()
    )

    call_booked = [l for l in my_leads if l.status == 'call_booked']
    active_leads = [l for l in my_leads if l.status != 'call_booked' and l.status != 'deal_done']

    overdue   = [l for l in active_leads if l.next_followup and l.next_followup < today]
    due_today = [l for l in active_leads if l.next_followup and l.next_followup == today]
    rest      = [l for l in active_leads if not l.next_followup or l.next_followup > today]

    return render_template(
        "crm/dashboard.html",
        call_booked_leads=call_booked,
        overdue_leads=overdue,
        today_leads=due_today,
        other_leads=rest,
        all_leads=my_leads,
        STATUS_LABELS=STATUS_LABELS,
        today=today,
        now=now,
    )


# ── Quick Add ─────────────────────────────────────────────────────────────────

@crm_bp.route("/quick-add", methods=["POST"])
@setter_required
def quick_add():
    handle = request.form.get("instagram_handle", "").strip().lstrip("@")
    notes  = request.form.get("notes", "").strip() or None

    if not handle:
        flash("Handle is required.", "error")
        return redirect(url_for("crm.dashboard"))

    if Lead.query.filter_by(instagram_handle=handle).first():
        flash(f"@{handle} already in the system.", "error")
        return redirect(url_for("crm.dashboard"))

    lead = Lead(instagram_handle=handle, status="new_lead",
                assigned_to=current_user.id, notes=notes)
    try:
        db.session.add(lead)
        db.session.flush()
        log_activity(current_user.id, f"Created lead @{handle}", lead.id)
        db.session.commit()
        flash(f"@{handle} added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Handle already exists (duplicate detected).", "warning")
    return redirect(url_for("crm.dashboard"))


# ── Add Lead ──────────────────────────────────────────────────────────────────

@crm_bp.route("/lead/add", methods=["GET", "POST"])
@setter_required
def add_lead():
    if request.method == "POST":
        handle = request.form.get("instagram_handle", "").strip().lstrip("@")

        if not handle:
            flash("Handle is required.", "error")
            return render_template("crm/add_lead.html", statuses=Lead.STATUSES)

        if Lead.query.filter_by(instagram_handle=handle).first():
            flash(f"@{handle} already in the system.", "error")
            return render_template("crm/add_lead.html", statuses=Lead.STATUSES)

        lead = Lead(
            instagram_handle=handle,
            status=request.form.get("status", "new_lead"),
            assigned_to=current_user.id,
            last_contacted=_parse_date(request.form.get("last_contacted")),
            next_followup=_parse_date(request.form.get("next_followup")),
            notes=request.form.get("notes", "").strip() or None,
        )
        try:
            db.session.add(lead)
            db.session.flush()
            log_activity(current_user.id, f"Created lead @{handle}", lead.id)
            db.session.commit()
            flash(f"@{handle} added.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Handle already exists (duplicate detected).", "warning")
        return redirect(url_for("crm.add_lead"))

    return render_template("crm/add_lead.html", statuses=Lead.STATUSES)


# ── Edit Lead ─────────────────────────────────────────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/edit", methods=["GET", "POST"])
@login_required
def edit_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)

    if request.method == "POST":
        handle = request.form.get("instagram_handle", "").strip().lstrip("@")
        if not handle:
            flash("Handle is required.", "error")
            return render_template("crm/edit_lead.html", lead=lead, statuses=Lead.STATUSES)

        clash = Lead.query.filter(Lead.instagram_handle == handle, Lead.id != lead_id).first()
        if clash:
            flash(f"@{handle} already belongs to another lead.", "error")
            return render_template("crm/edit_lead.html", lead=lead, statuses=Lead.STATUSES)

        lead.instagram_handle = handle
        lead.status           = request.form.get("status", lead.status)
        lead.last_contacted   = _parse_date(request.form.get("last_contacted"))
        lead.next_followup    = _parse_date(request.form.get("next_followup"))
        lead.notes            = request.form.get("notes", "").strip() or None
        log_activity(current_user.id, f"Edited lead @{handle}", lead.id)
        
        try:
            db.session.commit()
            flash(f"@{handle} updated.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Handle already exists (duplicate detected).", "warning")
        
        return redirect(url_for("admin.all_leads" if current_user.is_admin else "crm.dashboard"))

    return render_template("crm/edit_lead.html", lead=lead, statuses=Lead.STATUSES)


# ── Delete Lead ───────────────────────────────────────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/delete", methods=["POST"])
@login_required
def delete_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)
    handle = lead.instagram_handle
    log_activity(current_user.id, f"Deleted lead @{handle}")
    db.session.delete(lead)
    db.session.commit()
    flash(f"@{handle} deleted.", "info")
    return redirect(url_for("admin.all_leads" if current_user.is_admin else "crm.dashboard"))


# ── Status Update ─────────────────────────────────────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/status/<new_status>", methods=["POST"])
@login_required
def update_status(lead_id, new_status):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)

    if new_status not in Lead.STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("crm.dashboard"))

    old = lead.status
    lead.status = new_status
    lead.last_contacted = datetime.utcnow()
    log_activity(current_user.id, f"Status: {old} → {new_status}", lead.id)
    db.session.commit()
    flash(f"@{lead.instagram_handle} → {STATUS_LABELS[new_status]}.", "success")
    return redirect(url_for("admin.all_leads" if current_user.is_admin else "crm.dashboard"))


# ── Follow-up Done (user picks next date) ─────────────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/followup-done", methods=["POST"])
@login_required
def followup_done(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)

    lead.last_contacted = datetime.utcnow()

    next_date = _parse_date(request.form.get("next_followup", ""))
    if next_date:
        lead.next_followup = next_date
        log_activity(current_user.id, f"Follow-up done → next {next_date.strftime('%d %b')}", lead.id)
        db.session.commit()
        flash(f"@{lead.instagram_handle} — next follow-up on {next_date.strftime('%d %b %Y')}.", "success")
    else:
        next_date = date.today() + timedelta(days=2)
        lead.next_followup = next_date
        log_activity(current_user.id, "Follow-up done → next in 2 days", lead.id)
        db.session.commit()
        flash(f"@{lead.instagram_handle} — next follow-up in 2 days.", "success")
    return redirect(url_for("crm.dashboard"))


# ── Book / Edit Call  (GET = form, POST = save) ───────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/book-call", methods=["GET", "POST"])
@login_required
def book_call(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)

    if request.method == "GET":
        return render_template("crm/book_call.html", lead=lead)

    # ── POST ──────────────────────────────────────────────────────────────────
    call_date = request.form.get("call_date", "").strip()
    call_time = request.form.get("call_time", "").strip()

    if not call_date or not call_time:
        flash("Date and time are required.", "error")
        return render_template("crm/book_call.html", lead=lead)

    try:
        call_dt = datetime.strptime(f"{call_date} {call_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        flash("Invalid date/time format.", "error")
        return render_template("crm/book_call.html", lead=lead)

    if call_dt < datetime.now():
        flash("Cannot book a call in the past. Pick a future time.", "error")
        return render_template("crm/book_call.html", lead=lead)

    is_update = lead.call is not None
    if is_update:
        lead.call.call_datetime = call_dt
        log_activity(current_user.id,
                     f"Call rescheduled → {call_dt.strftime('%d %b %Y %H:%M')}", lead.id)
    else:
        lead.prev_status = lead.status          # save so cancel can restore
        db.session.add(Call(lead_id=lead.id, call_datetime=call_dt))
        log_activity(current_user.id,
                     f"Call booked: {call_dt.strftime('%d %b %Y %H:%M')}", lead.id)

    lead.status        = "call_booked"
    lead.next_followup = None
    db.session.commit()

    verb = "rescheduled" if is_update else "booked"
    flash(f"Call {verb} for @{lead.instagram_handle} on "
          f"{call_dt.strftime('%d %b %Y at %H:%M')}.", "success")
    return redirect(url_for("admin.all_leads" if current_user.is_admin else "crm.dashboard"))


# ── Cancel Call ───────────────────────────────────────────────────────────────

@crm_bp.route("/lead/<int:lead_id>/cancel-call", methods=["POST"])
@login_required
def cancel_call(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("crm.dashboard"))
    _guard(lead)

    if lead.call:
        db.session.delete(lead.call)

    restored        = lead.prev_status or "interested"
    lead.status     = restored
    lead.prev_status = None
    log_activity(current_user.id,
                 f"Call cancelled → restored to {restored}", lead.id)
    db.session.commit()
    flash(f"@{lead.instagram_handle} call cancelled. "
          f"Status restored to '{STATUS_LABELS.get(restored, restored)}'.", "info")
    return redirect(url_for("admin.all_leads" if current_user.is_admin else "crm.dashboard"))
