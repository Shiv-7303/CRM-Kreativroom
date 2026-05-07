"""
app.py — Flask application factory.
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from instagram_crm.models import db

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if not app.config["SECRET_KEY"] and app.config.get("ENV") == "production":
        raise ValueError("No SECRET_KEY set for production environment!")
    elif not app.config["SECRET_KEY"]:
        app.config["SECRET_KEY"] = "dev-secret-change-me"
    app.config["SQLALCHEMY_DATABASE_URI"]     = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    # Auto-create admin
    with app.app_context():
        db.create_all()
        from instagram_crm.models import User
        admin_email = "admin@kr.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(email=admin_email, role="admin")
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "admin@0411"))
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user {admin_email} created successfully!")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view         = "auth.login"
    login_manager.login_message      = "Please log in to continue."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        from instagram_crm.models import User
        db.session.expire_all()
        return db.session.get(User, int(user_id))

    @app.before_request
    def reject_stale_password_sessions():
        from flask import flash, redirect, session, url_for
        from flask_login import current_user, logout_user
        from sqlalchemy import select
        from instagram_crm.models import User

        if not current_user.is_authenticated:
            return None

        fresh_hash = db.session.execute(
            select(User.password_hash).where(User.id == current_user.id)
        ).scalar_one_or_none()
        if fresh_hash is None:
            logout_user()
            session.pop("password_hash_snapshot", None)
            flash("Your account is no longer available. Please contact an admin.", "warning")
            return redirect(url_for("auth.login"))

        snapshot = session.get("password_hash_snapshot")
        if snapshot is None:
            session["password_hash_snapshot"] = fresh_hash
            return None
        if snapshot == fresh_hash:
            return None

        logout_user()
        session.pop("password_hash_snapshot", None)
        flash("Your password was reset. Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    @app.context_processor
    def inject_overdue_count():
        from flask_login import current_user
        from datetime import date
        from instagram_crm.models import Lead
        count = 0
        if current_user.is_authenticated and current_user.role == "setter":
            today = date.today()
            count = (Lead.query
                     .filter(Lead.assigned_to == current_user.id,
                             Lead.next_followup != None,
                             Lead.next_followup < today)
                     .count())
        return {"overdue_count": count}

    @app.route("/")
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("crm.dashboard"))

    # ── Blueprints ────────────────────────────────────────────────────────────
    from instagram_crm.auth  import auth_bp
    from instagram_crm.admin import admin_bp
    from instagram_crm.crm   import crm_bp

    # ── Error handlers ─────────────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("errors/500.html"), 500

    return app

# Gunicorn wrapper
app = create_app()
