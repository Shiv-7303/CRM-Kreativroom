"""
auth.py — Login / Logout routes. No public signup.
"""
from datetime import datetime

from flask import (Blueprint, flash, redirect, render_template, session,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from urllib.parse import urlsplit

from models import db, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Show login page (GET) or validate credentials (POST)."""
    # Already logged in → send to the right dashboard
    if current_user.is_authenticated:
        return _role_redirect(current_user)

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            session["password_hash_snapshot"] = user.password_hash
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Honour ?next= param, otherwise role-based redirect
            next_page = request.args.get("next")
            return redirect(next_page) if _is_safe_next(next_page) else _role_redirect(user)

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Clear session, back to login."""
    logout_user()
    session.pop("password_hash_snapshot", None)
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── helpers ───────────────────────────────────────────────────────────────────

def _role_redirect(user):
    """Redirect to the correct dashboard based on role."""
    if user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("crm.dashboard"))


def _is_safe_next(target: str | None) -> bool:
    """Allow only local relative redirects after login."""
    if not target:
        return False
    parsed = urlsplit(target)
    return not parsed.scheme and not parsed.netloc and target.startswith("/")
