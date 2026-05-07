"""
admin.py — Admin-only routes. Uses log_activity() from models.
"""
import secrets
import string
from collections import defaultdict
from datetime import date, datetime, timedelta

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from sqlalchemy.orm import joinedload
from sqlalchemy import func

from instagram_crm.models import db, Activity, Call, Lead, User, log_activity

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper


STATUS_LABELS = {
    "new_lead":    "New Lead",
    "messaged":    "Messaged",
    "replied":     "Replied",
    "interested":  "Interested",
    "call_booked": "Call Booked",
    "deal_done":   "Deal Done",
}


def _user_stats():
    today = date.today()
    now = datetime.now()
    rows = []

    users = User.query.filter(User.role != 'admin').order_by(User.email).all()
    for user in users:
        total_leads = Lead.query.filter_by(assigned_to=user.id).count()
        active_leads = (
            Lead.query
            .filter(Lead.assigned_to == user.id, Lead.status != "deal_done")
            .count()
        )
        calls_booked = (
            Call.query
            .join(Lead)
            .filter(Lead.assigned_to == user.id)
            .count()
        )
        open_calls = Lead.query.filter_by(assigned_to=user.id, status="call_booked").count()
        deals_done = Lead.query.filter_by(assigned_to=user.id, status="deal_done").count()
        overdue = (
            Lead.query
            .filter(Lead.assigned_to == user.id,
                    Lead.next_followup != None,
                    Lead.next_followup < today,
                    Lead.status != "call_booked",
                    Lead.status != "deal_done")
            .count()
        )
        next_call = (
            Call.query
            .join(Lead)
            .filter(Lead.assigned_to == user.id, Call.call_datetime >= now)
            .order_by(Call.call_datetime.asc())
            .first()
        )
        rows.append({
            "user": user,
            "total_leads": total_leads,
            "active_leads": active_leads,
            "calls_booked": calls_booked,
            "open_calls": open_calls,
            "deals_done": deals_done,
            "overdue": overdue,
            "next_call": next_call,
        })

    rows.sort(key=lambda row: (row["calls_booked"], row["total_leads"]), reverse=True)
    return rows


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    today     = date.today()
    day_start = datetime.combine(today, datetime.min.time())
    week_ago  = datetime.utcnow() - timedelta(days=7)

    # ── User filter ───────────────────────────────────────────────────────
    filter_users = User.query.filter(User.role != 'admin').order_by(User.email).all()
    selected_user_id = request.args.get("user_id", type=int)
    selected_user = None
    if selected_user_id:
        selected_user = db.session.get(User, selected_user_id)
        if not selected_user:
            selected_user_id = None          # invalid id → show all

    # ── Metrics (optionally scoped to one user) ───────────────────────────
    total_users = User.query.filter(User.role != 'admin').count()

    if selected_user_id:
        total_leads     = Lead.query.filter_by(assigned_to=selected_user_id).count()
        total_calls     = Call.query.join(Lead).filter(Lead.assigned_to == selected_user_id).count()
        leads_today     = Lead.query.filter(Lead.assigned_to == selected_user_id, Lead.created_at >= day_start).count()
        calls_this_week = Call.query.join(Lead).filter(Lead.assigned_to == selected_user_id, Call.call_datetime >= week_ago).count()
        deals_done      = Lead.query.filter_by(assigned_to=selected_user_id, status="deal_done").count()
        overdue_count   = (
            Lead.query
            .filter(Lead.assigned_to == selected_user_id,
                    Lead.next_followup != None,
                    Lead.next_followup < today,
                    Lead.status != "call_booked",
                    Lead.status != "deal_done")
            .count()
        )
        followups_done  = (
            Activity.query
            .filter(Activity.user_id == selected_user_id,
                    Activity.action.like("Follow-up done%"))
            .count()
        )
    else:
        total_leads     = Lead.query.count()
        total_calls     = Call.query.count()
        leads_today     = Lead.query.filter(Lead.created_at >= day_start).count()
        calls_this_week = Call.query.filter(Call.call_datetime >= week_ago).count()
        deals_done      = Lead.query.filter_by(status="deal_done").count()
        overdue_count   = (
            Lead.query
            .filter(Lead.next_followup != None,
                    Lead.next_followup < today,
                    Lead.status != "call_booked",
                    Lead.status != "deal_done")
            .count()
        )
        followups_done  = (
            Activity.query
            .filter(Activity.action.like("Follow-up done%"))
            .count()
        )

    active_today = User.query.filter(User.role != 'admin', User.last_login >= day_start).count()

    # ── Leads added today (status changes logged as Activity) ───────────
    add_query = (
        Activity.query
        .filter(Activity.timestamp >= day_start, Activity.action.startswith("Created lead"))
    )
    if selected_user_id:
        add_query = add_query.filter(Activity.user_id == selected_user_id)
    leads_added_today = add_query.count()
    lead_additions = (
        add_query
        .order_by(Activity.timestamp.desc())
        .limit(15).all()
    )

    # ── Recent activity ───────────────────────────────────────────────────
    act_query = Activity.query
    if selected_user_id:
        act_query = act_query.filter(Activity.user_id == selected_user_id)
    recent_activities = act_query.order_by(Activity.timestamp.desc()).limit(10).all()

    users = User.query.order_by(User.last_login.desc().nullslast()).all()
    user_stats = _user_stats()

    # ── Upcoming calls ────────────────────────────────────────────────────
    calls_query = (
        Call.query
        .options(joinedload(Call.lead).joinedload(Lead.setter))
        .filter(Call.call_datetime >= datetime.now())
    )
    if selected_user_id:
        calls_query = calls_query.join(Call.lead).filter(Lead.assigned_to == selected_user_id)
    upcoming_calls = calls_query.order_by(Call.call_datetime.asc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_leads=total_leads,
        total_calls=total_calls,
        leads_today=leads_today,
        calls_this_week=calls_this_week,
        active_today=active_today,
        deals_done=deals_done,
        overdue_count=overdue_count,
        followups_done=followups_done,
        leads_added_today=leads_added_today,
        lead_additions=lead_additions,
        recent_activities=recent_activities,
        users=users,
        user_stats=user_stats,
        upcoming_calls=upcoming_calls,
        filter_users=filter_users,
        selected_user_id=selected_user_id,
        selected_user=selected_user,
    )


# ── Stats Page ────────────────────────────────────────────────────────────────

@admin_bp.route("/stats")
@admin_required
def stats():
    week_ago = datetime.utcnow() - timedelta(days=7)

    # ── User filter ───────────────────────────────────────────────────────
    filter_users = User.query.filter(User.role != 'admin').order_by(User.email).all()
    selected_user_id = request.args.get("user_id", type=int)
    selected_user = None
    if selected_user_id:
        selected_user = db.session.get(User, selected_user_id)
        if not selected_user:
            selected_user_id = None

    # ── All-time metrics (optionally scoped) ──────────────────────────────
    total_users = User.query.filter(User.role != 'admin').count()

    if selected_user_id:
        total_leads  = Lead.query.filter_by(assigned_to=selected_user_id).count()
        total_calls  = Call.query.join(Lead).filter(Lead.assigned_to == selected_user_id).count()
    else:
        total_leads  = Lead.query.count()
        total_calls  = Call.query.count()

    conversion = round((total_calls / total_leads) * 100, 1) if total_leads else 0

    # ── This-week metrics (optionally scoped) ─────────────────────────────
    if selected_user_id:
        leads_this_week = Lead.query.filter(Lead.assigned_to == selected_user_id, Lead.created_at >= week_ago).count()
        calls_this_week = Call.query.join(Lead).filter(Lead.assigned_to == selected_user_id, Call.call_datetime >= week_ago).count()
        followups_this_week = (
            Activity.query
            .filter(Activity.user_id == selected_user_id,
                    Activity.timestamp >= week_ago,
                    Activity.action.like("Follow-up done%"))
            .count()
        )
    else:
        leads_this_week = Lead.query.filter(Lead.created_at >= week_ago).count()
        calls_this_week = Call.query.filter(Call.call_datetime >= week_ago).count()
        followups_this_week = (
            Activity.query
            .filter(Activity.timestamp >= week_ago,
                    Activity.action.like("Follow-up done%"))
            .count()
        )

    # Per-setter stats — one DB query each, not a full scan
    user_stats = _user_stats()

    # ── Recent activity (optionally scoped) ───────────────────────────────
    act_query = Activity.query.filter(Activity.timestamp >= week_ago)
    if selected_user_id:
        act_query = act_query.filter(Activity.user_id == selected_user_id)
    recent_activities = act_query.order_by(Activity.timestamp.desc()).limit(20).all()

    return render_template(
        "admin/stats.html",
        total_users=total_users,
        total_leads=total_leads,
        total_calls=total_calls,
        conversion=conversion,
        leads_this_week=leads_this_week,
        calls_this_week=calls_this_week,
        followups_this_week=followups_this_week,
        user_stats=user_stats,
        recent_activities=recent_activities,
        now=datetime.utcnow(),
        filter_users=filter_users,
        selected_user_id=selected_user_id,
        selected_user=selected_user,
    )


# ── Team Overview ─────────────────────────────────────────────────────────────

@admin_bp.route("/team")
@admin_required
def team():
    today = date.today()
    now   = datetime.now()
    day_start = datetime.combine(today, datetime.min.time())
    week_ago  = datetime.utcnow() - timedelta(days=7)

    users = User.query.filter(User.role != 'admin').order_by(User.email).all()
    team_rows = []

    for user in users:
        total_leads  = Lead.query.filter_by(assigned_to=user.id).count()
        active_leads = Lead.query.filter(Lead.assigned_to == user.id, Lead.status != "deal_done").count()
        calls_booked = Call.query.join(Lead).filter(Lead.assigned_to == user.id).count()
        deals_done   = Lead.query.filter_by(assigned_to=user.id, status="deal_done").count()
        overdue = (
            Lead.query
            .filter(Lead.assigned_to == user.id,
                    Lead.next_followup != None,
                    Lead.next_followup < today,
                    Lead.status != "call_booked",
                    Lead.status != "deal_done")
            .count()
        )
        followups_done = (
            Activity.query
            .filter(Activity.user_id == user.id,
                    Activity.action.like("Follow-up done%"))
            .count()
        )
        leads_added_today = (
            Lead.query
            .filter(Lead.assigned_to == user.id,
                    Lead.created_at >= day_start)
            .count()
        )
        leads_added_week = (
            Lead.query
            .filter(Lead.assigned_to == user.id,
                    Lead.created_at >= week_ago)
            .count()
        )
        pending_followup = (
            Lead.query
            .filter(Lead.assigned_to == user.id,
                    Lead.next_followup != None,
                    Lead.next_followup >= today,
                    Lead.status != "call_booked",
                    Lead.status != "deal_done")
            .count()
        )
        last_activity = (
            Activity.query
            .filter(Activity.user_id == user.id)
            .order_by(Activity.timestamp.desc())
            .first()
        )
        conv = round((calls_booked / total_leads) * 100, 1) if total_leads else 0

        team_rows.append({
            "user": user,
            "total_leads": total_leads,
            "active_leads": active_leads,
            "calls_booked": calls_booked,
            "deals_done": deals_done,
            "overdue": overdue,
            "followups_done": followups_done,
            "leads_added_today": leads_added_today,
            "leads_added_week": leads_added_week,
            "pending_followup": pending_followup,
            "last_activity": last_activity,
            "conversion": conv,
        })

    team_rows.sort(key=lambda r: (r["calls_booked"], r["total_leads"]), reverse=True)

    return render_template(
        "admin/team.html",
        team_rows=team_rows,
        today=today,
    )


# ── Users ─────────────────────────────────────────────────────────────────────

@admin_bp.route("/calls")
@admin_required
def calls():
    setter_filter = request.args.get("setter", "").strip()
    query = (
        Call.query
        .join(Lead)
        .options(joinedload(Call.lead).joinedload(Lead.setter))
    )

    selected_setter = None
    if setter_filter:
        try:
            selected_setter = int(setter_filter)
            query = query.filter(Lead.assigned_to == selected_setter)
        except ValueError:
            selected_setter = None

    calls = query.order_by(Call.call_datetime.asc()).all()
    setters = User.query.filter_by(role="setter").order_by(User.email).all()

    call_stats = []
    for setter in setters:
        total = Call.query.join(Lead).filter(Lead.assigned_to == setter.id).count()
        upcoming = (
            Call.query
            .join(Lead)
            .filter(Lead.assigned_to == setter.id, Call.call_datetime >= datetime.now())
            .count()
        )
        call_stats.append({"user": setter, "total": total, "upcoming": upcoming})
    call_stats.sort(key=lambda row: row["total"], reverse=True)

    return render_template(
        "admin/calls.html",
        calls=calls,
        setters=setters,
        setter_filter=setter_filter,
        selected_setter=selected_setter,
        call_stats=call_stats,
        upcoming_count=sum(1 for call in calls if call.call_datetime >= datetime.now()),
        now=datetime.now(),
    )


@admin_bp.route("/users")
@admin_required
def users():
    search    = request.args.get("q", "").strip().lower()
    query     = User.query
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users, search=search)


@admin_bp.route("/users/create", methods=["POST"])
@admin_required
def add_user():
    email = request.form.get("email", "").strip().lower()
    role  = request.form.get("role", "setter")

    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("admin.users"))

    if User.query.filter_by(email=email).first():
        flash(f"{email} already exists.", "error")
        return redirect(url_for("admin.users"))

    if role not in ("admin", "setter"):
        role = "setter"

    alphabet     = string.ascii_letters + string.digits
    generated_pw = "".join(secrets.choice(alphabet) for _ in range(12))

    user = User(email=email, role=role)
    user.set_password(generated_pw)
    db.session.add(user)
    db.session.flush()
    log_activity(current_user.id, f"Created user {email} ({role})")
    db.session.commit()

    flash(f"User {email} created as {role}.", "success")
    flash(f"TEMP PASSWORD for {email}: {generated_pw}", "temp_password")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.users"))

    new_email = request.form.get("email", "").strip().lower()
    new_role  = request.form.get("role", user.role)

    if new_email and new_email != user.email:
        if User.query.filter_by(email=new_email).first():
            flash(f"{new_email} is already taken.", "error")
            return redirect(url_for("admin.users"))
        user.email = new_email

    if new_role in ("admin", "setter"):
        user.role = new_role

    log_activity(current_user.id, f"Edited user {user.email}")
    db.session.commit()
    flash("User updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin.users"))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.users"))

    email = user.email
    log_activity(current_user.id, f"Deleted user {email}")
    db.session.delete(user)
    db.session.commit()
    flash(f"{email} deleted.", "info")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_password(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.users"))

    alphabet = string.ascii_letters + string.digits
    temp_pw  = "".join(secrets.choice(alphabet) for _ in range(12))
    user.set_password(temp_pw)
    log_activity(current_user.id, f"Reset password for {user.email}")
    db.session.commit()

    flash(f"TEMP PASSWORD for {user.email}: {temp_pw}", "temp_password")
    return redirect(url_for("admin.users"))


# ── All Leads ─────────────────────────────────────────────────────────────────

@admin_bp.route("/leads")
@admin_required
def all_leads():
    today = date.today()
    status_filter = request.args.get("status", "").strip()
    setter_filter = request.args.get("setter", "").strip()
    search_query  = request.args.get("q", "").strip()
    date_from     = request.args.get("date_from", "").strip()
    date_to       = request.args.get("date_to", "").strip()
    fup_from      = request.args.get("fup_from", "").strip()
    fup_to        = request.args.get("fup_to", "").strip()
    quick         = request.args.get("quick", "").strip()

    query = Lead.query

    # Quick filters
    if quick == "overdue":
        query = query.filter(
            Lead.next_followup != None,
            Lead.next_followup < today,
            Lead.status != "call_booked",
            Lead.status != "deal_done"
        )
    elif quick == "today":
        query = query.filter(Lead.next_followup == today)
    elif quick == "this_week":
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        query = query.filter(
            Lead.next_followup != None,
            Lead.next_followup >= week_start,
            Lead.next_followup <= week_end
        )

    # Search by Instagram handle
    if search_query:
        query = query.filter(Lead.instagram_handle.ilike(f"%{search_query}%"))

    # Status filter
    if status_filter and status_filter in Lead.STATUSES:
        query = query.filter_by(status=status_filter)

    # Setter filter
    if setter_filter:
        try:
            query = query.filter_by(assigned_to=int(setter_filter))
        except ValueError:
            pass

    # Date range filter (created_at)
    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Lead.created_at >= df)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Lead.created_at < dt)
        except ValueError:
            pass

    # Follow-up date range filter
    if fup_from:
        try:
            ff = datetime.strptime(fup_from, "%Y-%m-%d").date()
            query = query.filter(Lead.next_followup >= ff)
        except ValueError:
            pass
    if fup_to:
        try:
            ft = datetime.strptime(fup_to, "%Y-%m-%d").date()
            query = query.filter(Lead.next_followup <= ft)
        except ValueError:
            pass

    leads   = query.options(joinedload(Lead.setter), joinedload(Lead.call)).order_by(Lead.created_at.desc()).all()
    setters = User.query.order_by(User.email).all()

    setter_stats = defaultdict(lambda: {"total": 0, "calls": 0})
    for lead in Lead.query.all():
        if lead.assigned_to:
            setter_stats[lead.assigned_to]["total"] += 1
            if lead.status == "call_booked":
                setter_stats[lead.assigned_to]["calls"] += 1

    return render_template(
        "admin/all_leads.html",
        leads=leads,
        setters=setters,
        status_filter=status_filter,
        setter_filter=setter_filter,
        search_query=search_query,
        date_from=date_from,
        date_to=date_to,
        fup_from=fup_from,
        fup_to=fup_to,
        quick=quick,
        STATUS_LABELS=STATUS_LABELS,
        setter_stats=setter_stats,
        today=today,
    )


@admin_bp.route("/leads/<int:lead_id>/deal-done", methods=["POST"])
@admin_required
def mark_deal_done(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("admin.all_leads"))

    if lead.status != "call_booked":
        flash("Can only mark Deal Done from Call Booked state.", "error")
        return redirect(url_for("admin.all_leads"))

    lead.status = "deal_done"
    log_activity(current_user.id, "Deal Closed", lead.id)
    db.session.commit()
    flash(f"@{lead.instagram_handle} marked as Deal Done!", "success")
    return redirect(url_for("admin.all_leads"))


@admin_bp.route("/leads/<int:lead_id>/override", methods=["POST"])
@admin_required
def override_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead not found.", "error")
        return redirect(url_for("admin.all_leads"))

    new_status = request.form.get("status", "").strip()
    new_setter = request.form.get("assigned_to", "").strip()
    changes    = []

    if new_status and new_status != lead.status:
        if new_status not in Lead.STATUSES:
            flash("Invalid status.", "error")
            return redirect(url_for("admin.all_leads"))
        changes.append(f"{lead.status} → {new_status}")
        lead.status = new_status

    if new_setter:
        if new_setter == "none":
            if lead.assigned_to is not None:
                old = lead.setter.email.split("@")[0] if lead.setter else "None"
                changes.append(f"unassigned (was {old})")
                lead.assigned_to = None
        else:
            try:
                sid = int(new_setter)
                if sid != lead.assigned_to:
                    su = db.session.get(User, sid)
                    if su:
                        changes.append(f"assigned to {su.email.split('@')[0]}")
                        lead.assigned_to = sid
            except ValueError:
                pass

    if changes:
        log_activity(current_user.id,
                     f"Admin override: {', '.join(changes)}", lead.id)
        db.session.commit()
        flash(f"@{lead.instagram_handle} updated.", "success")
    else:
        flash("No changes made.", "info")

    return redirect(url_for("admin.all_leads"))


# ── Conversion Funnel ─────────────────────────────────────────────────────────

@admin_bp.route("/funnel")
@admin_required
def funnel():
    setter_filter = request.args.get("setter", "").strip()
    base = Lead.query
    selected_setter = None

    if setter_filter:
        try:
            sid = int(setter_filter)
            base = base.filter_by(assigned_to=sid)
            selected_setter = db.session.get(User, sid)
        except ValueError:
            pass

    stages = ["new_lead", "messaged", "replied", "interested", "call_booked", "deal_done"]
    funnel_data = []
    total_first = base.count() or 1

    for i, stage in enumerate(stages):
        count = base.filter_by(status=stage).count()
        pct = round((count / total_first) * 100, 1)
        prev = funnel_data[-1]["count"] if funnel_data else count
        drop = round((1 - count / prev) * 100, 1) if prev and funnel_data else 0
        funnel_data.append({
            "stage": stage,
            "label": stage.replace("_", " ").title(),
            "count": count,
            "pct": pct,
            "drop": drop,
        })

    setters = User.query.order_by(User.email).all()
    return render_template("admin/funnel.html",
        funnel_data=funnel_data, setters=setters,
        setter_filter=setter_filter, selected_setter=selected_setter)


# ── Overdue Pipeline ──────────────────────────────────────────────────────────

@admin_bp.route("/overdue")
@admin_required
def overdue():
    today = date.today()
    setter_filter = request.args.get("setter", "").strip()
    sort_by = request.args.get("sort", "followup")

    query = Lead.query.options(joinedload(Lead.setter)).filter(
        Lead.next_followup != None,
        Lead.next_followup < today,
        Lead.status != "call_booked",
        Lead.status != "deal_done"
    )

    selected_setter = None
    if setter_filter:
        try:
            sid = int(setter_filter)
            query = query.filter_by(assigned_to=sid)
            selected_setter = db.session.get(User, sid)
        except ValueError:
            pass

    if sort_by == "followup":
        query = query.order_by(Lead.next_followup.asc())
    elif sort_by == "created":
        query = query.order_by(Lead.created_at.desc())
    elif sort_by == "setter":
        query = query.order_by(Lead.assigned_to.asc())

    overdue_leads = query.all()
    setters = User.query.order_by(User.email).all()

    overdue_by_setter = defaultdict(list)
    for lead in overdue_leads:
        overdue_by_setter[lead.setter.email if lead.setter else "Unassigned"].append(lead)

    return render_template("admin/overdue.html",
        overdue_leads=overdue_leads, setters=setters,
        setter_filter=setter_filter, selected_setter=selected_setter,
        sort_by=sort_by, today=today, overdue_by_setter=overdue_by_setter)


# ── Reports ───────────────────────────────────────────────────────────────────

@admin_bp.route("/reports")
@admin_required
def reports():
    today = date.today()
    day_start = datetime.combine(today, datetime.min.time())
    week_ago = datetime.utcnow() - timedelta(days=7)

    period = request.args.get("period", "daily")

    # Daily stats
    daily = {
        "leads_added": Lead.query.filter(Lead.created_at >= day_start).count(),
        "calls_booked": Call.query.filter(Call.call_datetime >= day_start).count(),
        "deals_done": Lead.query.filter_by(status="deal_done").filter(Lead.last_contacted >= day_start).count(),
        "followups": Activity.query.filter(Activity.timestamp >= day_start, Activity.action.like("Follow-up done%")).count(),
    }

    # Weekly stats
    weekly = {
        "leads_added": Lead.query.filter(Lead.created_at >= week_ago).count(),
        "calls_booked": Call.query.filter(Call.call_datetime >= week_ago).count(),
        "deals_done": Lead.query.filter_by(status="deal_done").filter(Lead.created_at >= week_ago).count(),
        "followups": Activity.query.filter(Activity.timestamp >= week_ago, Activity.action.like("Follow-up done%")).count(),
    }

    # Per-setter daily breakdown
    setters = User.query.filter_by(role="setter").all()
    setter_daily = []
    for s in setters:
        setter_daily.append({
            "user": s,
            "leads_added": Lead.query.filter(Lead.assigned_to == s.id, Lead.created_at >= day_start).count(),
            "calls_booked": Call.query.join(Lead).filter(Lead.assigned_to == s.id, Call.call_datetime >= day_start).count(),
            "followups": Activity.query.filter(Activity.user_id == s.id, Activity.timestamp >= day_start, Activity.action.like("Follow-up done%")).count(),
        })

    setter_daily.sort(key=lambda r: r["calls_booked"], reverse=True)

    return render_template("admin/reports.html",
        daily=daily, weekly=weekly, setter_daily=setter_daily,
        period=period, today=today)


# ── Setter Leaderboard ────────────────────────────────────────────────────────

@admin_bp.route("/leaderboard")
@admin_required
def leaderboard():
    setters = User.query.filter_by(role="setter").all()
    leaderboard_data = []

    for s in setters:
        total = Lead.query.filter_by(assigned_to=s.id).count()
        calls = Call.query.join(Lead).filter(Lead.assigned_to == s.id).count()
        deals = Lead.query.filter_by(assigned_to=s.id, status="deal_done").count()
        overdue_count = (
            Lead.query.filter(
                Lead.assigned_to == s.id,
                Lead.next_followup != None,
                Lead.next_followup < date.today(),
                Lead.status != "call_booked",
                Lead.status != "deal_done"
            ).count()
        )
        followups = Activity.query.filter(
            Activity.user_id == s.id,
            Activity.action.like("Follow-up done%")
        ).count()

        conv = round((calls / total) * 100, 1) if total else 0
        deal_rate = round((deals / total) * 100, 1) if total else 0

        leaderboard_data.append({
            "user": s,
            "total": total,
            "calls": calls,
            "deals": deals,
            "overdue": overdue_count,
            "followups": followups,
            "conversion": conv,
            "deal_rate": deal_rate,
        })

    sort = request.args.get("sort", "deals")
    if sort in ("deals", "conversion", "calls", "followups", "overdue"):
        reverse = sort != "overdue"
        leaderboard_data.sort(key=lambda r: r.get(sort, 0), reverse=reverse)

    return render_template("admin/leaderboard.html",
        leaderboard_data=leaderboard_data, sort=sort)


# ── Individual User Report ────────────────────────────────────────────────────

@admin_bp.route("/user_report/<int:user_id>")
@admin_required
def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin.reports"))

    today = date.today()
    day_start = datetime.combine(today, datetime.min.time())
    week_ago = datetime.utcnow() - timedelta(days=7)

    period = request.args.get("period", "daily")

    if period == "daily":
        start_dt = day_start
        label = "Today"
    else:
        start_dt = week_ago
        label = "This Week"

    # Leads added
    leads_added = Lead.query.filter(Lead.assigned_to == user.id, Lead.created_at >= start_dt).count()
    # Calls booked
    calls_booked = Call.query.join(Lead).filter(Lead.assigned_to == user.id, Call.call_datetime >= start_dt).count()
    # Deals done (deal done and last_contacted in period)
    deals_done = Lead.query.filter(
        Lead.assigned_to == user.id,
        Lead.status == "deal_done",
        Lead.last_contacted >= start_dt
    ).count()
    # Follow-ups done
    followups = Activity.query.filter(
        Activity.user_id == user.id,
        Activity.timestamp >= start_dt,
        Activity.action.like("Follow-up done%")
    ).count()
    # Overdue count (as of today)
    overdue = Lead.query.filter(
        Lead.assigned_to == user.id,
        Lead.next_followup != None,
        Lead.next_followup < today,
        Lead.status != "call_booked",
        Lead.status != "deal_done"
    ).count()
    # Conversion rate (calls / leads)
    conversion = round((calls_booked / leads_added) * 100, 1) if leads_added else 0
    # Deal rate (deals / leads)
    deal_rate = round((deals_done / leads_added) * 100, 1) if leads_added else 0

    # Recent activity (last 10)
    recent_activities = Activity.query.filter(
        Activity.user_id == user.id
    ).order_by(Activity.timestamp.desc()).limit(10).all()

    # Leads by status breakdown
    status_breakdown = db.session.query(
        Lead.status, func.count(Lead.id)
    ).filter(
        Lead.assigned_to == user.id
    ).group_by(
        Lead.status
    ).all()
    status_breakdown = {status: count for status, count in status_breakdown}

    # Setter stats for comparison (all setters)
    all_setters = User.query.filter_by(role="setter").all()
    setter_comparison = []
    for s in all_setters:
        s_leads = Lead.query.filter(Lead.assigned_to == s.id, Lead.created_at >= start_dt).count()
        s_calls = Call.query.join(Lead).filter(Lead.assigned_to == s.id, Call.call_datetime >= start_dt).count()
        s_deals = Lead.query.filter(
            Lead.assigned_to == s.id,
            Lead.status == "deal_done",
            Lead.last_contacted >= start_dt
        ).count()
        s_follows = Activity.query.filter(
            Activity.user_id == s.id,
            Activity.timestamp >= start_dt,
            Activity.action.like("Follow-up done%")
        ).count()
        setter_comparison.append({
            "user": s,
            "leads": s_leads,
            "calls": s_calls,
            "deals": s_deals,
            "follows": s_follows,
            "conv": round((s_calls / s_leads) * 100, 1) if s_leads else 0,
            "deal_rate": round((s_deals / s_leads) * 100, 1) if s_leads else 0
        })
    setter_comparison.sort(key=lambda x: x["leads"], reverse=True)

    return render_template("admin/user_report.html",
        user=user,
        period=period,
        label=label,
        leads_added=leads_added,
        calls_booked=calls_booked,
        deals_done=deals_done,
        followups=followups,
        overdue=overdue,
        conversion=conversion,
        deal_rate=deal_rate,
        recent_activities=recent_activities,
        status_breakdown=status_breakdown,
        setter_comparison=setter_comparison,
        today=today)
