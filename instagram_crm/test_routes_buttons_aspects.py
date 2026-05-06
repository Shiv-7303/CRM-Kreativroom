"""Broad route, button, and behavior coverage for the CRM."""
from datetime import date, datetime, timedelta

import pytest

from app import create_app
from crm import _parse_date
from models import Activity, Call, Lead, User, db, log_activity


USERS = {
    "admin": ("admin@test.com", "adminpass"),
    "setter1": ("setter1@test.com", "setterpass"),
    "setter2": ("setter2@test.com", "setterpass"),
}


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SERVER_NAME="localhost.localdomain",
        SECRET_KEY="test-secret",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(email=USERS["admin"][0], role="admin")
        admin.set_password(USERS["admin"][1])
        setter1 = User(email=USERS["setter1"][0], role="setter")
        setter1.set_password(USERS["setter1"][1])
        setter2 = User(email=USERS["setter2"][0], role="setter")
        setter2.set_password(USERS["setter2"][1])
        db.session.add_all([admin, setter1, setter2])
        db.session.commit()

        leads = []
        for idx, status in enumerate(Lead.STATUSES):
            lead = Lead(
                instagram_handle=f"seed_{status}",
                status=status,
                assigned_to=setter1.id,
                notes=f"seed notes {idx}",
                next_followup=date.today() + timedelta(days=idx - 2),
            )
            leads.append(lead)
            db.session.add(lead)
        db.session.flush()
        call_lead = next(l for l in leads if l.status == "call_booked")
        db.session.add(Call(lead_id=call_lead.id, call_datetime=datetime.now() + timedelta(days=3)))
        other = Lead(instagram_handle="setter2_private", status="new_lead", assigned_to=setter2.id)
        db.session.add(other)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, role):
    email, password = USERS[role]
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


def logout(client):
    return client.get("/logout", follow_redirects=True)


def lead_id(handle):
    return Lead.query.filter_by(instagram_handle=handle).first().id


def user_id(email):
    return User.query.filter_by(email=email).first().id


GET_ROUTE_CASES = [
    ("anon-root", None, "/", 302, None),
    ("anon-login", None, "/login", 200, b"Sign in"),
    ("anon-admin-dashboard", None, "/admin/dashboard", 302, None),
    ("anon-admin-users", None, "/admin/users", 302, None),
    ("anon-admin-stats", None, "/admin/stats", 302, None),
    ("anon-admin-leads", None, "/admin/leads", 302, None),
    ("anon-admin-calls", None, "/admin/calls", 302, None),
    ("anon-crm-dashboard", None, "/crm/dashboard", 302, None),
    ("anon-crm-add", None, "/crm/lead/add", 302, None),
    ("setter-dashboard", "setter1", "/crm/dashboard", 200, b"Dashboard"),
    ("setter-root", "setter1", "/", 302, None),
    ("setter-add-lead", "setter1", "/crm/lead/add", 200, b"Add New Lead"),
    ("setter-edit-own", "setter1", "/crm/lead/{new_lead}/edit", 200, b"Edit @seed_new_lead"),
    ("setter-book-own", "setter1", "/crm/lead/{interested}/book-call", 200, b"Book a Call"),
    ("setter-admin-dashboard", "setter1", "/admin/dashboard", 403, b"Access Denied"),
    ("setter-admin-users", "setter1", "/admin/users", 403, b"Access Denied"),
    ("setter-admin-stats", "setter1", "/admin/stats", 403, b"Access Denied"),
    ("setter-admin-leads", "setter1", "/admin/leads", 403, b"Access Denied"),
    ("setter-admin-calls", "setter1", "/admin/calls", 403, b"Access Denied"),
    ("setter-edit-other", "setter1", "/crm/lead/{setter2_private}/edit", 403, b"Access Denied"),
    ("setter-book-other", "setter1", "/crm/lead/{setter2_private}/book-call", 403, b"Access Denied"),
    ("admin-dashboard", "admin", "/admin/dashboard", 200, b"Admin Overview"),
    ("admin-root", "admin", "/", 302, None),
    ("admin-users", "admin", "/admin/users", 200, b"Manage Team"),
    ("admin-stats", "admin", "/admin/stats", 200, b"Performance Stats"),
    ("admin-leads", "admin", "/admin/leads", 200, b"All Leads"),
    ("admin-calls", "admin", "/admin/calls", 200, b"Call Details"),
    ("admin-edit-lead", "admin", "/crm/lead/{new_lead}/edit", 200, b"Edit @seed_new_lead"),
    ("admin-book-lead", "admin", "/crm/lead/{interested}/book-call", 200, b"Book a Call"),
    ("admin-crm-dashboard-redirect", "admin", "/crm/dashboard", 302, None),
    ("not-found", "admin", "/missing-page", 404, b"Page Not Found"),
]

for status in Lead.STATUSES:
    GET_ROUTE_CASES.append((f"admin-filter-status-{status}", "admin", f"/admin/leads?status={status}", 200, b"All Leads"))

for setter in ("1", "2", "abc", ""):
    GET_ROUTE_CASES.append((f"admin-filter-setter-{setter or 'empty'}", "admin", f"/admin/leads?setter={setter}", 200, b"All Leads"))


@pytest.mark.parametrize("name,role,path,expected_status,expected_body", GET_ROUTE_CASES, ids=[c[0] for c in GET_ROUTE_CASES])
def test_route_access_matrix(client, app, name, role, path, expected_status, expected_body):
    with app.app_context():
        path = (
            path.replace("{new_lead}", str(lead_id("seed_new_lead")))
            .replace("{interested}", str(lead_id("seed_interested")))
            .replace("{setter2_private}", str(lead_id("setter2_private")))
        )
    if role:
        login(client, role)
    rv = client.get(path)
    assert rv.status_code == expected_status
    if expected_body:
        assert expected_body in rv.data


TEMPLATE_WIRING_CASES = [
    ("login-form", None, "/login", b'action="/login"', b"Sign In"),
    ("base-admin-dashboard-link", "admin", "/admin/dashboard", b'href="/admin/users"', b"Manage Team"),
    ("base-admin-leads-link", "admin", "/admin/dashboard", b'href="/admin/leads"', b"All Leads"),
    ("base-admin-calls-link", "admin", "/admin/dashboard", b'href="/admin/calls"', b"Calls Booked"),
    ("base-admin-stats-link", "admin", "/admin/dashboard", b'href="/admin/stats"', b"Stats"),
    ("users-create-button", "admin", "/admin/users", b'action="/admin/users/create"', b"Create User"),
    ("users-edit-save-button", "admin", "/admin/users", b'action="/admin/users/2/edit"', b"Save"),
    ("users-reset-button", "admin", "/admin/users", b"/reset-password", b"Reset PW"),
    ("users-delete-button", "admin", "/admin/users", b"/delete", b"Delete"),
    ("leads-override-button", "admin", "/admin/leads", b"/override", b"Save"),
    ("leads-edit-link", "admin", "/admin/leads", b"/edit", b"Edit"),
    ("leads-delete-button", "admin", "/admin/leads", b"/delete", b"Delete"),
    ("crm-add-link", "setter1", "/crm/dashboard", b'href="/crm/lead/add"', b"+ Add Lead"),
    ("crm-followup-form", "setter1", "/crm/dashboard", b"/followup-done", b"Done"),
    ("crm-delete-form", "setter1", "/crm/dashboard", b"/delete", b"Delete"),
    ("crm-edit-link", "setter1", "/crm/dashboard", b"/edit", b"Edit"),
    ("add-lead-save", "setter1", "/crm/lead/add", b'action="/crm/lead/add"', b"Save Lead"),
]


@pytest.mark.parametrize("name,role,path,needle,label", TEMPLATE_WIRING_CASES, ids=[c[0] for c in TEMPLATE_WIRING_CASES])
def test_visible_buttons_and_links_are_wired(client, name, role, path, needle, label):
    if role:
        login(client, role)
    rv = client.get(path)
    assert rv.status_code == 200
    assert needle in rv.data
    assert label in rv.data


STATUS_BUTTON_CASES = [(status, "setter1") for status in Lead.STATUSES] + [(status, "admin") for status in Lead.STATUSES]


@pytest.mark.parametrize("new_status,role", STATUS_BUTTON_CASES, ids=[f"{r}-{s}" for s, r in STATUS_BUTTON_CASES])
def test_status_buttons_update_valid_statuses(client, app, new_status, role):
    login(client, role)
    with app.app_context():
        lead = Lead(instagram_handle=f"{role}_{new_status}_target", status="new_lead", assigned_to=user_id(USERS["setter1"][0]))
        db.session.add(lead)
        db.session.commit()
        lid = lead.id
    rv = client.post(f"/crm/lead/{lid}/status/{new_status}", follow_redirects=True)
    assert rv.status_code == 200
    with app.app_context():
        assert db.session.get(Lead, lid).status == new_status


FOLLOWUP_CASES = list(range(0, 31))


@pytest.mark.parametrize("offset", FOLLOWUP_CASES, ids=[f"plus-{i}" for i in FOLLOWUP_CASES])
def test_followup_done_accepts_every_calendar_offset(client, app, offset):
    login(client, "setter1")
    target = date.today() + timedelta(days=offset)
    with app.app_context():
        lead = Lead(instagram_handle=f"followup_{offset}", assigned_to=user_id(USERS["setter1"][0]))
        db.session.add(lead)
        db.session.commit()
        lid = lead.id
    rv = client.post(
        f"/crm/lead/{lid}/followup-done",
        data={"next_followup": target.strftime("%Y-%m-%d")},
        follow_redirects=True,
    )
    assert rv.status_code == 200
    with app.app_context():
        assert db.session.get(Lead, lid).next_followup == target


BOOK_CALL_CASES = [(days, hour) for days in range(1, 16) for hour in ("09:00", "14:30")]


@pytest.mark.parametrize("days,hour", BOOK_CALL_CASES, ids=[f"day-{d}-{h}" for d, h in BOOK_CALL_CASES])
def test_book_call_button_creates_or_updates_calls(client, app, days, hour):
    login(client, "setter1")
    with app.app_context():
        lead = Lead(instagram_handle=f"call_{days}_{hour.replace(':', '')}", status="interested", assigned_to=user_id(USERS["setter1"][0]))
        db.session.add(lead)
        db.session.commit()
        lid = lead.id
    call_date = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
    rv = client.post(f"/crm/lead/{lid}/book-call", data={"call_date": call_date, "call_time": hour}, follow_redirects=True)
    assert rv.status_code == 200
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.status == "call_booked"
        assert lead.call is not None


ADMIN_BUTTON_CASES = []
for role in ("setter", "admin"):
    ADMIN_BUTTON_CASES.append(("create-user", {"email": f"new_{role}@test.com", "role": role}))
for role in ("setter", "admin", "invalid"):
    ADMIN_BUTTON_CASES.append(("edit-user", {"email": f"edited_{role}@test.com", "role": role}))
for status in Lead.STATUSES:
    ADMIN_BUTTON_CASES.append(("override-status", {"status": status, "assigned_to": ""}))
for assignment in ("none", "setter1", "setter2"):
    ADMIN_BUTTON_CASES.append(("override-assignment", {"status": "", "assigned_to": assignment}))
ADMIN_BUTTON_CASES.extend([
    ("reset-password", {}),
    ("delete-user", {}),
    ("deal-done", {}),
])


@pytest.mark.parametrize("kind,payload", ADMIN_BUTTON_CASES, ids=[f"{i}-{c[0]}" for i, c in enumerate(ADMIN_BUTTON_CASES)])
def test_admin_buttons_post_successfully(client, app, kind, payload):
    login(client, "admin")
    with app.app_context():
        admin_id = user_id(USERS["admin"][0])
        setter1_id = user_id(USERS["setter1"][0])
        setter2_id = user_id(USERS["setter2"][0])

    if kind == "create-user":
        rv = client.post("/admin/users/create", data=payload, follow_redirects=True)
        assert rv.status_code == 200
        assert payload["email"].encode() in rv.data
    elif kind == "edit-user":
        with app.app_context():
            target_id = setter2_id
        rv = client.post(f"/admin/users/{target_id}/edit", data=payload, follow_redirects=True)
        assert rv.status_code == 200
    elif kind == "reset-password":
        rv = client.post(f"/admin/users/{setter1_id}/reset-password", follow_redirects=True)
        assert rv.status_code == 200
        assert b"TEMP PASSWORD" in rv.data
    elif kind == "delete-user":
        with app.app_context():
            user = User(email="delete_target@test.com", role="setter")
            user.set_password("pass")
            db.session.add(user)
            db.session.commit()
            target_id = user.id
        rv = client.post(f"/admin/users/{target_id}/delete", follow_redirects=True)
        assert rv.status_code == 200
    elif kind == "deal-done":
        with app.app_context():
            lid = lead_id("seed_call_booked")
        rv = client.post(f"/admin/leads/{lid}/deal-done", follow_redirects=True)
        assert rv.status_code == 200
        with app.app_context():
            assert db.session.get(Lead, lid).status == "deal_done"
    else:
        with app.app_context():
            lid = lead_id("seed_new_lead")
            data = dict(payload)
            if data.get("assigned_to") == "setter1":
                data["assigned_to"] = str(setter1_id)
            elif data.get("assigned_to") == "setter2":
                data["assigned_to"] = str(setter2_id)
        rv = client.post(f"/admin/leads/{lid}/override", data=data, follow_redirects=True)
        assert rv.status_code == 200
        with app.app_context():
            lead = db.session.get(Lead, lid)
            if payload.get("status"):
                assert lead.status == payload["status"]


HANDLE_CASES = [
    ("plain", "plain"),
    ("@prefixed", "prefixed"),
    ("  spaced  ", "spaced"),
    ("@@double", "double"),
    ("Name_123", "Name_123"),
    ("lead.one", "lead.one"),
    ("lead-two", "lead-two"),
    (" lead_three ", "lead_three"),
    ("@LeadFour", "LeadFour"),
    ("12345", "12345"),
] + [(f"@bulk_handle_{i}", f"bulk_handle_{i}") for i in range(40)]


@pytest.mark.parametrize("raw,expected", HANDLE_CASES, ids=[f"handle-{i}" for i, _ in enumerate(HANDLE_CASES)])
def test_handle_inputs_are_normalized_by_add_buttons(client, app, raw, expected):
    login(client, "setter1")
    rv = client.post("/crm/quick-add", data={"instagram_handle": raw}, follow_redirects=True)
    assert rv.status_code == 200
    with app.app_context():
        assert Lead.query.filter_by(instagram_handle=expected).first() is not None


DATE_CASES = [(date.today() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(-20, 31)]
DATE_CASES += ["", "not-a-date", "2026-99-99", "05/05/2026", "2026-02-30"]


@pytest.mark.parametrize("raw", DATE_CASES, ids=[f"date-{i}" for i, _ in enumerate(DATE_CASES)])
def test_date_parser_never_crashes(raw):
    parsed = _parse_date(raw)
    assert parsed is None or isinstance(parsed, date)


PASSWORD_CASES = [f"pass-{i}-Value" for i in range(30)]


@pytest.mark.parametrize("password", PASSWORD_CASES, ids=[f"password-{i}" for i, _ in enumerate(PASSWORD_CASES)])
def test_password_hash_round_trips(app, password):
    with app.app_context():
        user = User(email=f"{password}@example.com", role="setter")
        user.set_password(password)
        assert user.check_password(password)
        assert not user.check_password(password + "-wrong")


ACTIVITY_CASES = [f"Activity case {i}" for i in range(25)]


@pytest.mark.parametrize("action", ACTIVITY_CASES, ids=[f"activity-{i}" for i, _ in enumerate(ACTIVITY_CASES)])
def test_activity_logger_records_actions(app, action):
    with app.app_context():
        uid = user_id(USERS["setter1"][0])
        lid = lead_id("seed_new_lead")
        log_activity(uid, action, lid)
        db.session.commit()
        assert Activity.query.filter_by(action=action, lead_id=lid, user_id=uid).first() is not None


OTHER_SETTER_POST_CASES = [
    ("status", "/crm/lead/{id}/status/messaged", {}),
    ("followup", "/crm/lead/{id}/followup-done", {"next_followup": date.today().strftime("%Y-%m-%d")}),
    ("book", "/crm/lead/{id}/book-call", {"call_date": (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"), "call_time": "10:00"}),
    ("cancel", "/crm/lead/{id}/cancel-call", {}),
    ("edit", "/crm/lead/{id}/edit", {"instagram_handle": "setter2_private", "status": "new_lead"}),
    ("delete", "/crm/lead/{id}/delete", {}),
]


@pytest.mark.parametrize("name,path,data", OTHER_SETTER_POST_CASES, ids=[c[0] for c in OTHER_SETTER_POST_CASES])
def test_setter_buttons_cannot_mutate_other_setters_leads(client, app, name, path, data):
    login(client, "setter1")
    with app.app_context():
        lid = lead_id("setter2_private")
    rv = client.post(path.replace("{id}", str(lid)), data=data)
    assert rv.status_code == 403


LOGIN_REDIRECT_CASES = [
    ("/crm/dashboard", "/crm/dashboard"),
    ("/admin/dashboard", "/admin/dashboard"),
    ("https://evil.example/steal", "/crm/dashboard"),
    ("//evil.example/steal", "/crm/dashboard"),
    ("dashboard", "/crm/dashboard"),
]


@pytest.mark.parametrize("next_url,expected_location", LOGIN_REDIRECT_CASES, ids=[f"next-{i}" for i, _ in enumerate(LOGIN_REDIRECT_CASES)])
def test_login_next_redirects_are_local_only(client, next_url, expected_location):
    rv = client.post(
        f"/login?next={next_url}",
        data={"email": USERS["setter1"][0], "password": USERS["setter1"][1]},
        follow_redirects=False,
    )
    assert rv.status_code == 302
    assert rv.headers["Location"].endswith(expected_location)


def test_password_reset_invalidates_active_user_session(app):
    setter_client = app.test_client()

    login(setter_client, "setter1")
    assert setter_client.get("/crm/dashboard").status_code == 200
    with setter_client.session_transaction() as sess:
        assert sess.get("password_hash_snapshot")

    with app.app_context():
        setter = User.query.filter_by(email=USERS["setter1"][0]).first()
        setter.set_password("new-temp-password")
        db.session.commit()

    rv = setter_client.get("/crm/dashboard", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Your password was reset" in rv.data
    assert b"Sign in" in rv.data or b"Sign In" in rv.data
