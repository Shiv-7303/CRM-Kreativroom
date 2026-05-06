"""50+ backend tests for Instagram CRM - covers all checklist.md phases"""
import pytest
from app import create_app, db
from models import User, Lead, Activity, Call
from datetime import datetime, date, timedelta

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", "WTF_CSRF_ENABLED": False, "SERVER_NAME": "localhost.localdomain"})
    with app.app_context():
        db.create_all()
        admin = User(email="admin@test.com", role="admin")
        admin.set_password("adminpass")
        s1 = User(email="setter1@test.com", role="setter")
        s1.set_password("setterpass")
        s2 = User(email="setter2@test.com", role="setter")
        s2.set_password("setterpass")
        db.session.add_all([admin, s1, s2])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(c, email, pw):
    return c.post('/login', data=dict(email=email, password=pw), follow_redirects=True)

def logout(c):
    return c.get('/logout', follow_redirects=True)

# ═══ PHASE 1: AUTH & ROLES (Tests 1-10) ═══
def test_01_login_page_loads(client):
    rv = client.get('/login')
    assert rv.status_code == 200
    assert b"Sign in" in rv.data or b"Sign In" in rv.data

def test_02_admin_login_success(client):
    rv = login(client, "admin@test.com", "adminpass")
    assert b"Admin Overview" in rv.data

def test_03_setter_login_success(client):
    rv = login(client, "setter1@test.com", "setterpass")
    assert b"Dashboard" in rv.data

def test_04_login_wrong_password(client):
    rv = login(client, "admin@test.com", "wrong")
    assert b"Invalid" in rv.data

def test_05_login_wrong_email(client):
    rv = login(client, "nobody@test.com", "x")
    assert b"Invalid" in rv.data

def test_06_logout_works(client):
    login(client, "setter1@test.com", "setterpass")
    rv = logout(client)
    assert b"Sign in" in rv.data or b"Sign In" in rv.data

def test_07_setter_blocked_from_admin(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.get('/admin/dashboard')
    assert rv.status_code == 403

def test_08_admin_redirected_from_crm(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/crm/dashboard', follow_redirects=True)
    assert b"Admin Overview" in rv.data

def test_09_unauthenticated_redirect(client):
    rv = client.get('/crm/dashboard', follow_redirects=True)
    assert b"Sign in" in rv.data or b"Sign In" in rv.data

def test_10_unauthenticated_admin_redirect(client):
    rv = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Sign in" in rv.data or b"Sign In" in rv.data

# ═══ PHASE 2: ADMIN USER MANAGEMENT (Tests 11-18) ═══
def test_11_admin_create_user(client, app):
    login(client, "admin@test.com", "adminpass")
    rv = client.post('/admin/users/create', data=dict(email="new@test.com", role="setter"), follow_redirects=True)
    assert b"new@test.com" in rv.data
    with app.app_context():
        assert User.query.filter_by(email="new@test.com").first() is not None

def test_12_admin_create_duplicate_user(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.post('/admin/users/create', data=dict(email="setter1@test.com", role="setter"), follow_redirects=True)
    assert b"already exists" in rv.data

def test_13_admin_delete_user(client, app):
    login(client, "admin@test.com", "adminpass")
    with app.app_context():
        uid = User.query.filter_by(email="setter2@test.com").first().id
    rv = client.post(f'/admin/users/{uid}/delete', follow_redirects=True)
    assert b"deleted" in rv.data
    with app.app_context():
        assert db.session.get(User, uid) is None

def test_14_admin_reset_password(client, app):
    login(client, "admin@test.com", "adminpass")
    with app.app_context():
        uid = User.query.filter_by(email="setter1@test.com").first().id
    rv = client.post(f'/admin/users/{uid}/reset-password', follow_redirects=True)
    assert b"TEMP PASSWORD" in rv.data or b"New password" in rv.data or b"Password reset" in rv.data

def test_15_admin_users_page_loads(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/users')
    assert rv.status_code == 200
    assert b"setter1@test.com" in rv.data

def test_16_admin_dashboard_loads(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/dashboard')
    assert rv.status_code == 200
    assert b"Admin Overview" in rv.data

def test_17_admin_stats_page_loads(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/stats')
    assert rv.status_code == 200

def test_18_admin_all_leads_page_loads(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/leads')
    assert rv.status_code == 200

def test_18b_admin_calls_page_loads(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/calls')
    assert rv.status_code == 200
    assert b"Calls Booked" in rv.data

# ═══ PHASE 2: CRM LEAD CRUD (Tests 19-28) ═══
def test_19_setter_dashboard_loads(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.get('/crm/dashboard')
    assert rv.status_code == 200
    assert b"Dashboard" in rv.data

def test_20_quick_add_lead(client, app):
    login(client, "setter1@test.com", "setterpass")
    rv = client.post('/crm/quick-add', data=dict(instagram_handle="lead1", notes="test"), follow_redirects=True)
    assert b"@lead1 added" in rv.data
    with app.app_context():
        lead = Lead.query.filter_by(instagram_handle="lead1").first()
        assert lead is not None
        assert lead.status == "new_lead"
        assert lead.setter.email == "setter1@test.com"

def test_21_quick_add_duplicate(client):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="dup1"))
    rv = client.post('/crm/quick-add', data=dict(instagram_handle="dup1"), follow_redirects=True)
    assert b"already" in rv.data

def test_22_quick_add_empty_handle(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.post('/crm/quick-add', data=dict(instagram_handle=""), follow_redirects=True)
    assert b"required" in rv.data

def test_23_add_lead_page_loads(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.get('/crm/lead/add')
    assert rv.status_code == 200

def test_24_add_lead_form(client, app):
    login(client, "setter1@test.com", "setterpass")
    rv = client.post('/crm/lead/add', data=dict(instagram_handle="form_lead", status="new_lead", notes="from form"), follow_redirects=True)
    assert b"@form_lead added" in rv.data

def test_25_edit_lead(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="edit_me"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="edit_me").first().id
    rv = client.post(f'/crm/lead/{lid}/edit', data=dict(instagram_handle="edit_me", status="messaged", notes="edited"), follow_redirects=True)
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.notes == "edited"

def test_26_delete_lead(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="delete_me"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="delete_me").first().id
    rv = client.post(f'/crm/lead/{lid}/delete', follow_redirects=True)
    assert b"deleted" in rv.data
    with app.app_context():
        assert db.session.get(Lead, lid) is None

def test_27_cannot_edit_other_setter_lead(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="s1_private"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="s1_private").first().id
    logout(client)
    login(client, "setter2@test.com", "setterpass")
    rv = client.post(f'/crm/lead/{lid}/edit', data=dict(instagram_handle="s1_private", status="replied", notes="hack"))
    assert rv.status_code == 403

def test_28_cannot_delete_other_setter_lead(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="s1_nodelete"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="s1_nodelete").first().id
    logout(client)
    login(client, "setter2@test.com", "setterpass")
    rv = client.post(f'/crm/lead/{lid}/delete')
    assert rv.status_code == 403

# ═══ PHASE 3: STATUS BUTTONS + FOLLOW-UPS (Tests 29-40) ═══
def test_29_status_new_to_messaged(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="status1"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="status1").first().id
    client.post(f'/crm/lead/{lid}/status/messaged', follow_redirects=True)
    with app.app_context():
        assert db.session.get(Lead, lid).status == "messaged"

def test_30_status_messaged_to_replied(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="status2"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="status2").first().id
    client.post(f'/crm/lead/{lid}/status/messaged')
    client.post(f'/crm/lead/{lid}/status/replied')
    with app.app_context():
        assert db.session.get(Lead, lid).status == "replied"

def test_31_status_replied_to_interested(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="status3"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="status3").first().id
    client.post(f'/crm/lead/{lid}/status/replied')
    client.post(f'/crm/lead/{lid}/status/interested')
    with app.app_context():
        assert db.session.get(Lead, lid).status == "interested"

def test_32_invalid_status_rejected(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="status_bad"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="status_bad").first().id
    rv = client.post(f'/crm/lead/{lid}/status/invalid_xyz', follow_redirects=True)
    assert b"Invalid status" in rv.data

def test_33_followup_done_sets_plus2(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="fup1"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="fup1").first().id
    rv = client.post(f'/crm/lead/{lid}/followup-done', follow_redirects=True)
    assert b"next follow-up in 2 days" in rv.data
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.next_followup == date.today() + timedelta(days=2)

def test_34_followup_done_updates_last_contacted(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="fup2"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="fup2").first().id
    client.post(f'/crm/lead/{lid}/followup-done')
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.last_contacted is not None

def test_35_overdue_leads_display(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="overdue1"))
    with app.app_context():
        lead = Lead.query.filter_by(instagram_handle="overdue1").first()
        lead.next_followup = date.today() - timedelta(days=3)
        db.session.commit()
    rv = client.get('/crm/dashboard')
    assert b"OVERDUE" in rv.data
    assert b"@overdue1" in rv.data

def test_36_today_leads_display(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="today1"))
    with app.app_context():
        lead = Lead.query.filter_by(instagram_handle="today1").first()
        lead.next_followup = date.today()
        db.session.commit()
    rv = client.get('/crm/dashboard')
    assert b"TODAY" in rv.data
    assert b"@today1" in rv.data

def test_37_setter_sees_only_own_leads(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="s1_only"))
    logout(client)
    login(client, "setter2@test.com", "setterpass")
    rv = client.get('/crm/dashboard')
    assert b"@s1_only" not in rv.data

def test_38_admin_sees_all_leads(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="vis1"))
    logout(client)
    login(client, "setter2@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="vis2"))
    logout(client)
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/leads')
    assert b"@vis1" in rv.data
    assert b"@vis2" in rv.data

def test_39_edit_lead_sets_followup(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="fup_edit"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="fup_edit").first().id
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/edit', data=dict(instagram_handle="fup_edit", status="new_lead", next_followup=future, notes=""))
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.next_followup == date.today() + timedelta(days=5)

def test_40_status_change_logs_activity(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="act_log"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="act_log").first().id
    client.post(f'/crm/lead/{lid}/status/messaged')
    with app.app_context():
        act = Activity.query.filter(Activity.action.like("%messaged%"), Activity.lead_id == lid).first()
        assert act is not None

# ═══ PHASE 4: CALL BOOKING + STATS (Tests 41-50) ═══
def test_41_book_call_page_loads(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_page"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_page").first().id
    rv = client.get(f'/crm/lead/{lid}/book-call')
    assert rv.status_code == 200

def test_42_book_call_success(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_ok"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_ok").first().id
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    rv = client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="14:00"), follow_redirects=True)
    assert b"booked" in rv.data
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.status == "call_booked"
        assert lead.call is not None

def test_43_book_call_missing_time(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_notime"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_notime").first().id
    rv = client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date="2030-01-01", call_time=""), follow_redirects=True)
    assert b"required" in rv.data

def test_44_book_call_logs_activity(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_act"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_act").first().id
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="10:00"))
    with app.app_context():
        act = Activity.query.filter(Activity.action.like("Call booked%"), Activity.lead_id == lid).first()
        assert act is not None

def test_45_cancel_call(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_cancel"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_cancel").first().id
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="10:00"))
    rv = client.post(f'/crm/lead/{lid}/cancel-call', follow_redirects=True)
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.status != "call_booked"
        assert lead.call is None

def test_46_admin_stats_numbers(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="stat1"))
    client.post('/crm/quick-add', data=dict(instagram_handle="stat2"))
    logout(client)
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/stats')
    assert rv.status_code == 200

def test_46b_admin_call_details_show_setter_and_time(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="call_detail"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="call_detail").first().id
    future = (date.today() + timedelta(days=4)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="16:30"))
    logout(client)
    login(client, "admin@test.com", "adminpass")
    rv = client.get('/admin/calls')
    assert b"@call_detail" in rv.data
    assert b"setter1@test.com" in rv.data
    assert b"16:30" in rv.data

def test_47_activity_log_on_lead_create(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="actlog1"))
    with app.app_context():
        act = Activity.query.filter(Activity.action.like("%Created lead%actlog1%")).first()
        assert act is not None

def test_48_activity_log_on_followup(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="actfup"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="actfup").first().id
    client.post(f'/crm/lead/{lid}/followup-done')
    with app.app_context():
        act = Activity.query.filter(Activity.action.like("Follow-up done%"), Activity.lead_id == lid).first()
        assert act is not None

def test_49_lead_not_found_edit(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.post('/crm/lead/99999/edit', data=dict(instagram_handle="x", status="new_lead", notes=""), follow_redirects=True)
    assert b"not found" in rv.data

def test_50_lead_not_found_delete(client):
    login(client, "setter1@test.com", "setterpass")
    rv = client.post('/crm/lead/99999/delete', follow_redirects=True)
    assert b"not found" in rv.data

# ═══ BONUS EDGE CASES (Tests 51-55) ═══
def test_51_handle_strips_at_symbol(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="@with_at"))
    with app.app_context():
        lead = Lead.query.filter_by(instagram_handle="with_at").first()
        assert lead is not None

def test_52_admin_create_user_empty_email(client):
    login(client, "admin@test.com", "adminpass")
    rv = client.post('/admin/users/create', data=dict(email="", role="setter"), follow_redirects=True)
    assert b"required" in rv.data

def test_53_full_workflow(client, app):
    """Complete setter workflow: add -> message -> reply -> interested -> book call"""
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="full_flow"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="full_flow").first().id
    client.post(f'/crm/lead/{lid}/status/messaged')
    client.post(f'/crm/lead/{lid}/status/replied')
    client.post(f'/crm/lead/{lid}/status/interested')
    future = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="15:00"))
    with app.app_context():
        lead = db.session.get(Lead, lid)
        assert lead.status == "call_booked"
        assert lead.call is not None
        acts = Activity.query.filter_by(lead_id=lid).count()
        assert acts >= 4

def test_54_setter_cannot_change_other_lead_status(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="guard_test"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="guard_test").first().id
    logout(client)
    login(client, "setter2@test.com", "setterpass")
    rv = client.post(f'/crm/lead/{lid}/status/messaged')
    assert rv.status_code == 403

def test_55_delete_lead_cascades_call(client, app):
    login(client, "setter1@test.com", "setterpass")
    client.post('/crm/quick-add', data=dict(instagram_handle="cascade_del"))
    with app.app_context():
        lid = Lead.query.filter_by(instagram_handle="cascade_del").first().id
    future = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    client.post(f'/crm/lead/{lid}/book-call', data=dict(call_date=future, call_time="10:00"))
    with app.app_context():
        assert Call.query.filter_by(lead_id=lid).first() is not None
    client.post(f'/crm/lead/{lid}/delete')
    with app.app_context():
        assert Call.query.filter_by(lead_id=lid).first() is None
