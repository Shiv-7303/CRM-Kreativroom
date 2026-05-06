"""
models.py — User, Lead, Call, Activity + log_activity() helper
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(50), default="setter")
    last_login    = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    leads      = db.relationship("Lead", backref="setter", lazy="dynamic")
    activities = db.relationship("Activity", backref="user", lazy="dynamic")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


class Lead(db.Model):
    __tablename__ = "leads"

    STATUSES = ["new_lead", "messaged", "replied", "interested", "call_booked", "deal_done"]

    id               = db.Column(db.Integer, primary_key=True)
    instagram_handle = db.Column(db.String(255), unique=True, nullable=False)
    status           = db.Column(db.String(50), default="new_lead", nullable=False, index=True)
    prev_status      = db.Column(db.String(50), nullable=True)   # ← restored on cancel-call
    assigned_to      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    last_contacted   = db.Column(db.DateTime, nullable=True)
    next_followup    = db.Column(db.Date, nullable=True, index=True)
    notes            = db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    call       = db.relationship("Call", backref="lead", uselist=False,
                                 cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="lead", lazy="dynamic")

    def __repr__(self):
        return f"<Lead @{self.instagram_handle} [{self.status}]>"


class Call(db.Model):
    __tablename__ = "calls"

    id            = db.Column(db.Integer, primary_key=True)
    lead_id       = db.Column(db.Integer, db.ForeignKey("leads.id"), unique=True, nullable=False)
    call_datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Call lead={self.lead_id} at={self.call_datetime}>"


class Activity(db.Model):
    __tablename__ = "activities"

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    action    = db.Column(db.String(255), nullable=False)
    lead_id   = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Activity user={self.user_id} '{self.action}'>"


# ── Shared logging utility ─────────────────────────────────────────────────────

def log_activity(user_id, action: str, lead_id=None) -> None:
    """
    Append an Activity row.  Caller is responsible for db.session.commit().
    """
    db.session.add(Activity(user_id=user_id, action=action, lead_id=lead_id))
