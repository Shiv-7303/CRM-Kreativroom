# Instagram Outreach CRM - MVP Checklist (5-7 Days) 🚀
**Project Goal:** Build a WORKING Instagram Outreach CRM with Admin Panel

**Philosophy:** USAGE > PERFECTION | SPEED > FEATURES | If setters don't use it = it's useless

**Tech Stack:** Flask | HTML + TailwindCSS | SQLite | Simple Auth | Render (Free Tier)

**Timeline:** 5-7 days (DAY 1-5 build, DAY 6 user testing, DAY 7 iterate)

---

## 📋 ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────┐
│                  FLASK APP                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. LOGIN PAGE                                  │
│     ├─ Admin login → Admin Dashboard            │
│     └─ Setter login → CRM Dashboard             │
│                                                 │
│  2. ADMIN DASHBOARD (ONLY YOU)                  │
│     ├─ Create/Edit/Delete users                 │
│     ├─ Performance metrics (stats)              │
│     ├─ System health monitoring                 │
│     ├─ View all leads                           │
│     └─ Database management                      │
│                                                 │
│  3. CRM DASHBOARD (SETTERS)                     │
│     ├─ View assigned leads                      │
│     ├─ Add/Edit leads                           │
│     ├─ Status buttons                           │
│     ├─ Follow-up system                         │
│     └─ Book calls                               │
│                                                 │
└─────────────────────────────────────────────────┘

DATABASE: SQLite (app.db file)
DEPLOYMENT: Render (FREE TIER)
```

---

## 🚀 BUILD ORDER (FOLLOW EXACTLY)

### **DAY 1:** Flask + SQLite + Login + Admin Setup (5-6 hours)
- [ ] Flask app setup with blueprints
- [ ] SQLite models (User, Lead, Call only)
- [ ] Login/logout system (with role checking)
- [ ] Basic Admin Dashboard (stub)
- [ ] Basic CRM Dashboard (stub)

### **DAY 2:** Admin User Management + CRM Basic Dashboard (5-6 hours)
- [ ] Admin: Create user form (email, password, role)
- [ ] Admin: List all users with edit/delete
- [ ] Admin: Reset user password
- [ ] CRM: Show assigned leads in table
- [ ] CRM: Lead CRUD (create, edit, delete)

### **DAY 3:** Status Buttons + Follow-up System (4-6 hours)
- [ ] CRM: Status buttons (Messaged, Replied, Interested, Book Call)
- [ ] CRM: Show overdue follow-ups (red, prominent)
- [ ] CRM: Show today's follow-ups
- [ ] CRM: "Follow-up Done" button (+2 days logic)
- [ ] Admin: View all leads (not just assigned)

### **DAY 4:** Call Booking + Admin Stats (4-5 hours)
- [ ] CRM: Book call form (date + time)
- [ ] CRM: Display booked calls
- [ ] Admin: Performance stats (total leads, calls booked, users, etc.)
- [ ] Admin: Activity tracking (simple - last user login, last action, etc.)

### **DAY 5:** UI Polish + Testing + Deploy (5-6 hours)
- [ ] CRM Dashboard: readable table with colors
- [ ] Admin Dashboard: clean stats display
- [ ] Mobile responsive (both admin and CRM)
- [ ] Manual testing all flows
- [ ] Deploy to Render with SQLite

### **DAY 6:** Real User Testing (2-3 hours)
- [ ] Give setter their login credentials
- [ ] Watch them use CRM
- [ ] Note what's confusing

### **DAY 7:** Bug Fixes + Optimization (3-4 hours)
- [ ] Fix issues found
- [ ] Speed optimizations
- [ ] Ready for team

---

## 🎯 WHAT TO BUILD

### ✅ USER ROLES & ACCESS

**ADMIN (You):**
- [ ] Login with email/password
- [ ] Access `/admin` dashboard
- [ ] Create/edit/delete users
- [ ] View performance stats
- [ ] View all leads (search/filter)
- [ ] Monitor system health
- [ ] Change any lead status (override)
- [ ] See activity log

**SETTER (Team Members):**
- [ ] Login with email/password
- [ ] Access `/dashboard` (CRM)
- [ ] See only assigned leads
- [ ] Add new leads
- [ ] Edit own leads
- [ ] Change status (buttons)
- [ ] Book calls
- [ ] Set follow-ups
- [ ] Cannot access admin panel
- [ ] Cannot see other setter's leads

---

### ✅ ADMIN DASHBOARD (Personal, Only You)

**Top Menu:**
- [ ] Logo/App name
- [ ] "Users" link
- [ ] "Stats" link
- [ ] "All Leads" link
- [ ] User email (top right)
- [ ] Logout button

**Users Management Page:**
- [ ] Table: Email | Role | Created | Actions
- [ ] "Add New User" button
- [ ] Edit user (change role, email)
- [ ] Delete user (with confirmation)
- [ ] Reset password button (generate temp password, show in modal)
- [ ] Search users by email

**Stats Page:**
- [ ] Total users: X
- [ ] Total leads: Y
- [ ] Total calls booked: Z
- [ ] Leads created today: N
- [ ] Calls booked this week: M
- [ ] Active users today: K
- [ ] Last 5 activities (user email, action, lead, timestamp)
- [ ] Users table with last login

**All Leads Page:**
- [ ] View ALL leads (not just assigned)
- [ ] Filter by status, setter
- [ ] Search by handle
- [ ] Change status from admin (override)
- [ ] See who it's assigned to
- [ ] Quick stats per setter

---

### ✅ CRM DASHBOARD (For Setters)

**Navigation Bar:**
- [ ] App logo
- [ ] "My Leads" (shows assigned count)
- [ ] "Follow-ups" (shows overdue count in red)
- [ ] User email (top right)
- [ ] Logout button

**Main Dashboard:**
- [ ] **OVERDUE FOLLOW-UPS Section** (red background)
  - [ ] Table of leads with next_followup < today
  - [ ] Sorted by oldest first
  - [ ] Status, handle, follow-up date
  - [ ] "Follow-up Done" button on each
  
- [ ] **TODAY'S FOLLOW-UPS Section** (yellow background)
  - [ ] Leads with next_followup == today
  
- [ ] **ALL MY LEADS** (table)
  - [ ] Columns: Handle | Status | Next Follow-up | Notes | Actions
  - [ ] Status badges (colored)
  - [ ] Status buttons per row (Mark Messaged, Replied, Interested, Book Call)
  - [ ] Edit/Delete buttons
  
- [ ] **Add Lead Button**
  - [ ] Opens form or modal
  - [ ] Fields: handle, assigned_to (auto-fill self), status, notes
  - [ ] Simple + fast

---

## ❌ WHAT TO REMOVE

❌ Followers count, niche, source
❌ Activity tracking (detailed)
❌ CSV import/export
❌ Advanced filters
❌ Pagination (small SQLite DB)
❌ Drag-and-drop
❌ Animations
❌ Dark mode
❌ Rate limiting
❌ Extensive testing

---

## 📊 DATABASE SCHEMA (SQLite)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'setter',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leads table
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instagram_handle VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'new_lead',
    assigned_to INTEGER REFERENCES users(id),
    last_contacted TIMESTAMP,
    next_followup TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calls table
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER UNIQUE REFERENCES leads(id),
    call_datetime TIMESTAMP NOT NULL
);

-- Activity log (simple)
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255),
    lead_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 PHASE 1: FLASK + SQLite + LOGIN + ADMIN SETUP (DAY 1)

### 1.1 Project Setup
- [ ] Create folder: `instagram_crm/`
- [ ] Create `.env`:
  ```
  SECRET_KEY=your_random_secret_key_here
  FLASK_ENV=development
  DATABASE_URL=sqlite:///app.db
  ```
- [ ] Create `requirements.txt`:
  ```
  Flask
  Flask-Login
  Flask-SQLAlchemy
  python-dotenv
  Werkzeug
  ```
- [ ] `pip install -r requirements.txt`

### 1.2 Folder Structure
```
instagram_crm/
├── app.py                 # Main app
├── models.py             # User, Lead, Call, Activity
├── auth.py               # Login/logout routes
├── admin.py              # Admin routes (users, stats, all leads)
├── crm.py                # CRM routes (setter dashboard)
├── templates/
│   ├── base.html         # Master template
│   ├── login.html        # Login form
│   ├── admin/
│   │   ├── dashboard.html    # Stats
│   │   ├── users.html        # User management
│   │   └── all_leads.html    # All leads view
│   └── crm/
│       ├── dashboard.html    # Setter dashboard
│       ├── add_lead.html     # Add lead form
│       └── edit_lead.html    # Edit lead form
├── static/
│   └── style.css         # Tailwind CSS (optional)
├── instance/
│   └── app.db            # SQLite database (auto-created)
├── .env                  # Config (git ignore)
└── .gitignore
```

### 1.3 Flask App (`app.py`)
- [ ] Initialize Flask app
- [ ] Configure SQLAlchemy with SQLite
- [ ] Initialize Flask-Login
- [ ] Create blueprints: auth, admin, crm
- [ ] Register all blueprints
- [ ] Create db tables on startup (if not exist)

### 1.4 Models (`models.py`)
- [ ] **User Model:**
  - [ ] id, email (unique), password_hash, role, last_login, created_at
  - [ ] Methods: set_password(pw), check_password(pw)
  
- [ ] **Lead Model:**
  - [ ] id, instagram_handle (unique), status, assigned_to (FK), last_contacted, next_followup, notes, created_at
  - [ ] Relationship to User (assigned_to)
  - [ ] Relationship to Call
  
- [ ] **Call Model:**
  - [ ] id, lead_id (FK, unique), call_datetime
  
- [ ] **Activity Model:**
  - [ ] id, user_id (FK), action, lead_id, timestamp

### 1.5 Auth Routes (`auth.py`)
- [ ] GET `/login` → show login form
- [ ] POST `/login` → verify email/password
  - [ ] If admin role → redirect to `/admin/dashboard`
  - [ ] If setter role → redirect to `/crm/dashboard`
- [ ] GET `/logout` → clear session, redirect to login
- [ ] Login required decorator for all protected routes

### 1.6 Admin Blueprint Setup (`admin.py`)
- [ ] GET `/admin/dashboard` → admin stats page (stub for now)
- [ ] GET `/admin/users` → user management page (stub for now)
- [ ] GET `/admin/leads` → all leads page (stub for now)
- [ ] Add admin_required decorator (check role == 'admin')

### 1.7 CRM Blueprint Setup (`crm.py`)
- [ ] GET `/crm/dashboard` → setter dashboard (stub for now)
- [ ] Add setter_required decorator (check logged in)

### 1.8 Templates
- [ ] **base.html:** Basic HTML, TailwindCSS, navigation (stub)
- [ ] **login.html:** Email/password form, centered
- [ ] **admin/dashboard.html:** Stub (will fill Day 4)
- [ ] **crm/dashboard.html:** Stub (will fill Day 2-3)

### 1.9 Test Day 1
- [ ] Run `flask run` → works
- [ ] Visit `/login` → form shows
- [ ] Create admin user manually in SQLite:
  ```sql
  INSERT INTO users (email, password_hash, role) 
  VALUES ('admin@example.com', 'hashed_password', 'admin');
  ```
- [ ] Login with admin → redirects to `/admin/dashboard`
- [ ] Logout → back to login
- [ ] Test role-based redirect (admin vs setter)

---

## 👥 PHASE 2: ADMIN USER MANAGEMENT + CRM BASIC DASHBOARD (DAY 2)

### 2.1 Admin - User Management Page

#### Routes (`admin.py`):
- [ ] GET `/admin/users` → show list of all users
- [ ] GET `/admin/users/create` → show create user form
- [ ] POST `/admin/users/create` → create new user
  - [ ] Generate random password, show in modal
  - [ ] Send to user (or show once)
  - [ ] Store hashed password in DB
- [ ] GET `/admin/users/<id>/edit` → show edit form
- [ ] POST `/admin/users/<id>/edit` → update user (email, role)
- [ ] POST `/admin/users/<id>/delete` → delete user (with confirmation)
- [ ] POST `/admin/users/<id>/reset-password` → generate temp password, show in modal

#### Template (`admin/users.html`):
- [ ] Table: Email | Role | Last Login | Created | Actions
- [ ] "Create New User" button at top
- [ ] Edit icon per row → opens edit modal
- [ ] Delete icon per row → confirmation dialog
- [ ] Reset password link per row → shows temp password
- [ ] Search by email (simple JS filter or server-side)

### 2.2 Admin - Dashboard Stub
- [ ] `admin/dashboard.html` → show:
  - [ ] Total users
  - [ ] Total leads
  - [ ] Links to Users, All Leads, Stats
  - [ ] Will add real stats on Day 4

### 2.3 CRM - Basic Dashboard for Setters

#### Routes (`crm.py`):
- [ ] GET `/crm/dashboard` → fetch leads assigned to current user
  - [ ] Show overdue follow-ups (next_followup < today)
  - [ ] Show today's follow-ups (next_followup == today)
  - [ ] Show all other leads
  - [ ] Render dashboard.html

#### Template (`crm/dashboard.html`):
- [ ] OVERDUE section (red background)
  - [ ] Table of overdue leads
  - [ ] Buttons: Follow-up Done, Edit, Delete
  
- [ ] TODAY section (yellow background)
  - [ ] Table of today's follow-ups
  
- [ ] ALL LEADS section
  - [ ] Table: Handle | Status | Next Follow-up | Notes | Actions
  - [ ] Status badges (different colors)
  - [ ] Edit/Delete buttons
  
- [ ] "Add Lead" button

### 2.4 CRM - Lead CRUD

#### Routes (`crm.py`):
- [ ] GET `/crm/lead/add` → show add lead form
- [ ] POST `/crm/lead/add` → create lead
  - [ ] auto-assign to current user
  - [ ] auto-set status to 'new_lead'
  - [ ] Redirect to dashboard
  
- [ ] GET `/crm/lead/<id>/edit` → show edit form (only if assigned to user)
- [ ] POST `/crm/lead/<id>/edit` → update lead
  - [ ] Can edit: status, next_followup, notes
  - [ ] Redirect to dashboard
  
- [ ] POST `/crm/lead/<id>/delete` → delete lead (only if assigned to user)
  - [ ] Confirmation
  - [ ] Redirect to dashboard

#### Templates:
- [ ] `crm/add_lead.html`:
  - [ ] Handle input (required)
  - [ ] Status dropdown (default new_lead)
  - [ ] Notes textarea
  - [ ] Submit + Cancel buttons
  
- [ ] `crm/edit_lead.html`:
  - [ ] Same as add_lead
  - [ ] Pre-filled with current values
  - [ ] Delete button at bottom

### 2.5 Test Day 2
- [ ] Admin: Create user → works
- [ ] Admin: Edit user → works
- [ ] Admin: Delete user → works
- [ ] Admin: Reset password → shows temp password
- [ ] Setter: Add lead → creates, assigned to self
- [ ] Setter: Edit lead → updates
- [ ] Setter: Delete lead → deletes with confirmation
- [ ] Dashboard shows leads correctly

---

## ⚡ PHASE 3: STATUS BUTTONS + FOLLOW-UP SYSTEM (DAY 3)

### 3.1 Status Change Buttons

#### Routes (`crm.py`):
- [ ] POST `/crm/lead/<id>/status/messaged` → update status, update last_contacted
- [ ] POST `/crm/lead/<id>/status/replied` → update status
- [ ] POST `/crm/lead/<id>/status/interested` → update status
- [ ] POST `/crm/lead/<id>/status/call_booked` → update status
- [ ] All routes: redirect to dashboard or AJAX update

#### In Dashboard:
- [ ] Each lead row has buttons:
  - [ ] "Mark Messaged"
  - [ ] "Mark Replied"
  - [ ] "Mark Interested"
  - [ ] "Book Call" (link to call form)
- [ ] Buttons are colored (green for status change)
- [ ] Quick + obvious (1-click actions)

### 3.2 Follow-up System (CRITICAL)

#### Display Logic:
- [ ] Query 1: `leads where next_followup <= today` (OVERDUE)
  - [ ] Display at top in RED section
  - [ ] Sort by oldest first
  - [ ] Show: Handle, Status, Days Overdue, "Follow-up Done" button
  
- [ ] Query 2: `leads where next_followup == today` (TODAY)
  - [ ] Display in YELLOW section
  - [ ] Show: Handle, Status, "Follow-up Done" button
  
- [ ] Query 3: All other leads (next_followup > today or NULL)
  - [ ] Display in normal table

#### Routes (`crm.py`):
- [ ] POST `/crm/lead/<id>/followup-done`
  - [ ] Sets next_followup = today + 2 days
  - [ ] Updates last_contacted = now
  - [ ] Keeps current status (or set to 'follow_up' if you prefer)
  - [ ] Log activity
  - [ ] Redirect to dashboard
  
- [ ] GET/POST `/crm/lead/<id>/set-followup`
  - [ ] Show date picker
  - [ ] Submit → set next_followup date
  - [ ] Update DB

#### In Edit Form:
- [ ] "Next Follow-up Date" input (date picker)
- [ ] Default: empty (can set manually)
- [ ] Helpful: When mark as 'replied', suggest +3 days

### 3.3 Admin - View All Leads

#### Routes (`admin.py`):
- [ ] GET `/admin/leads` → show all leads (any status, any setter)
  - [ ] Filter by status (dropdown)
  - [ ] Filter by setter (dropdown)
  - [ ] Search by handle
  - [ ] Can change status from admin (override)
  - [ ] Can assign to different setter

#### Template (`admin/all_leads.html`):
- [ ] Table: Handle | Status | Assigned To | Next Follow-up | Actions
- [ ] Status badges
- [ ] Edit link per row
- [ ] Filter dropdowns at top

### 3.4 Test Day 3
- [ ] Setter: Add lead → mark as messaged → status changes
- [ ] Setter: Mark as replied → status changes
- [ ] Setter: Set next_followup to yesterday → appears in OVERDUE section (red)
- [ ] Settler: Set next_followup to today → appears in TODAY section (yellow)
- [ ] Setter: Click "Follow-up Done" → next_followup = today + 2 days
- [ ] Admin: View all leads → see all (any setter)
- [ ] Admin: Change lead status → works
- [ ] Overdue leads are prominent, can't miss

---

## 📞 PHASE 4: CALL BOOKING + ADMIN STATS (DAY 4)

### 4.1 Call Booking

#### Routes (`crm.py`):
- [ ] GET `/crm/lead/<id>/book-call` → show call booking form
- [ ] POST `/crm/lead/<id>/book-call` → create call
  - [ ] Store call_datetime
  - [ ] Auto-move lead to 'call_booked' status
  - [ ] Log activity
  - [ ] Redirect to dashboard
  
- [ ] POST `/crm/lead/<id>/edit-call` → update call
- [ ] POST `/crm/lead/<id>/cancel-call` → delete call

#### Template (`crm/book_call.html`):
- [ ] Lead name (read-only)
- [ ] Date input (date picker)
- [ ] Time input (time picker or "HH:MM" text)
- [ ] Submit + Cancel buttons
- [ ] Simple, 30 seconds to fill

#### In Dashboard:
- [ ] If status = 'call_booked', show call date/time in table
- [ ] Link to edit/cancel call

### 4.2 Admin - Performance Stats

#### Routes (`admin.py`):
- [ ] GET `/admin/stats` → show performance metrics

#### Metrics to Display:
- [ ] **Overview:**
  - [ ] Total users: X
  - [ ] Total leads: Y
  - [ ] Total calls booked: Z
  - [ ] Conversion rate: (calls booked / total leads) %
  
- [ ] **This Week:**
  - [ ] New leads created: N
  - [ ] Calls booked: M
  - [ ] Follow-ups completed: K
  
- [ ] **Users Activity:**
  - [ ] Table: Email | Leads Assigned | Calls Booked | Last Login
  - [ ] Sort by most active
  
- [ ] **Recent Activity Log:**
  - [ ] Last 10 actions
  - [ ] Format: [Time] [User] [Action] [Lead]
  - [ ] Example: "2 mins ago - Sarah - Mark Replied - @insta_handle"

#### Template (`admin/stats.html`):
- [ ] Simple cards showing metrics
- [ ] No fancy charts (simple numbers OK)
- [ ] Readable layout
- [ ] Last activity table

### 4.3 Activity Logging

#### In models.py:
- [ ] Every action logs to activities table:
  - [ ] User adds lead
  - [ ] User changes status
  - [ ] User books call
  - [ ] User follows up
  - [ ] Admin creates user
  - [ ] Admin resets password
  
#### Logging Function:
```python
def log_activity(user_id, action, lead_id=None):
    activity = Activity(
        user_id=user_id,
        action=action,
        lead_id=lead_id,
        timestamp=datetime.now()
    )
    db.session.add(activity)
    db.session.commit()
```

### 4.4 Test Day 4
- [ ] Setter: Mark lead as interested → button works
- [ ] Settler: Click "Book Call" → form shows
- [ ] Settler: Fill date/time → lead moves to "Call Booked"
- [ ] Admin: View stats → shows correct numbers
- [ ] Admin: Check activity log → shows recent actions
- [ ] Admin: See which user is most active

---

## 🎨 PHASE 5: UI POLISH + TESTING + DEPLOY (DAY 5)

### 5.1 CRM Dashboard UI

#### Templates Update:
- [ ] **Navigation bar:**
  - [ ] Logo/app name (left)
  - [ ] "My Leads (X)" link (center)
  - [ ] "Follow-ups (Y)" link with badge showing overdue count in red
  - [ ] User email (right)
  - [ ] Logout button
  
- [ ] **OVERDUE section:**
  - [ ] Red background (bg-red-100)
  - [ ] Bold heading: "⚠️ OVERDUE FOLLOW-UPS (3)"
  - [ ] Table with columns: Handle | Days Overdue | Status | "Follow-up Done" button
  - [ ] Sort by oldest first
  
- [ ] **TODAY section:**
  - [ ] Yellow background (bg-yellow-100)
  - [ ] Heading: "📅 FOLLOW-UPS TODAY (2)"
  - [ ] Same table format
  
- [ ] **ALL LEADS section:**
  - [ ] Table: Handle | Status | Next Follow-up | Notes | Actions
  - [ ] Status badges with colors:
    - new_lead = blue
    - messaged = purple
    - replied = orange
    - interested = green
    - call_booked = gold
  - [ ] Action buttons per row:
    - Status change buttons (Mark Messaged, Replied, Interested)
    - Edit link
    - Delete link
  - [ ] "Add Lead" button at top
  
- [ ] **Add Lead Form:**
  - [ ] Modal or simple page
  - [ ] Fields: Handle, Status, Notes
  - [ ] Submit + Cancel buttons
  - [ ] Clear after submit (stay on form for quick entry)

### 5.2 Admin Dashboard UI

#### Templates Update:
- [ ] **Navigation bar:**
  - [ ] Logo (left)
  - [ ] "Users" link
  - [ ] "All Leads" link
  - [ ] "Stats" link
  - [ ] User email + Logout (right)
  
- [ ] **Users page:**
  - [ ] Table: Email | Role | Last Login | Created | Actions
  - [ ] Edit icon per row
  - [ ] Delete icon per row
  - [ ] Reset password link
  - [ ] "Create New User" button at top
  
- [ ] **All Leads page:**
  - [ ] Filter by status (dropdown)
  - [ ] Filter by setter (dropdown)
  - [ ] Search by handle
  - [ ] Table: Handle | Setter | Status | Next Follow-up | Actions
  - [ ] Can change status from admin
  
- [ ] **Stats page:**
  - [ ] Cards showing: Total Users, Total Leads, Total Calls, Conversion Rate
  - [ ] Activity log (last 10 actions)
  - [ ] Users table with activity
  
- [ ] **Dashboard (home):**
  - [ ] Quick overview (3 big cards)
  - [ ] Links to Users, Leads, Stats

### 5.3 Colors & Styling
- [ ] Use Tailwind defaults (no custom colors needed)
- [ ] Status badges: 5 different colors (blue, purple, orange, green, gold)
- [ ] Buttons: Green for positive, Red for delete, Blue for primary
- [ ] Overdue: Red background
- [ ] Today: Yellow background
- [ ] Tables: Clean, good spacing, readable fonts

### 5.4 Forms
- [ ] All inputs have labels
- [ ] Placeholders are helpful
- [ ] Submit buttons are clear
- [ ] Cancel buttons are obvious
- [ ] Error messages show below fields
- [ ] Date pickers work (use HTML date input)
- [ ] Time pickers work (use HTML time input or text)

### 5.5 Mobile Optimization
- [ ] Test on iPhone (375px)
- [ ] Test on Android (375px)
- [ ] Navigation bar responsive (hamburger menu if needed)
- [ ] Table columns hide on mobile (important ones visible)
- [ ] Buttons are clickable (44px minimum)
- [ ] Forms are usable (labels above inputs)
- [ ] Modals are full-screen on mobile (if used)

### 5.6 Manual Testing

**Test Flows:**
- [ ] Admin flow:
  - [ ] Login as admin
  - [ ] Create user (email, password auto-generated)
  - [ ] View users list
  - [ ] Edit user (change role)
  - [ ] Delete user
  - [ ] Reset password
  - [ ] View all leads
  - [ ] Change lead status (override)
  - [ ] View stats
  - [ ] Check activity log
  - [ ] Logout

- [ ] Setter flow:
  - [ ] Login as setter
  - [ ] See assigned leads
  - [ ] Add new lead
  - [ ] Mark as messaged (status change)
  - [ ] Mark as replied
  - [ ] Mark as interested
  - [ ] Set next follow-up date
  - [ ] Check overdue section (if any)
  - [ ] Check today section (if any)
  - [ ] Book call
  - [ ] Edit call date
  - [ ] Follow-up done (next_followup +2 days)
  - [ ] Logout

- [ ] Edge cases:
  - [ ] Try login with wrong password → error shown
  - [ ] Try access admin as setter → redirect to CRM
  - [ ] Try access CRM as admin → should work
  - [ ] Try delete own lead → works
  - [ ] Try edit other setter's lead → can't (permission check)
  - [ ] Try delete non-existent lead → error or 404

### 5.7 SQLite Database Notes
- [ ] Database file: `instance/app.db` (don't commit to git)
- [ ] All queries are fast (SQLite is fine for <10K leads)
- [ ] Backup: Download app.db file periodically
- [ ] No migrations needed (simple Flask-SQLAlchemy)

### 5.8 Deploy to Render (Free Tier)

#### Preparation:
- [ ] Create GitHub repo
- [ ] Push code (except .env, instance/ folder)
- [ ] Create `.gitignore`:
  ```
  .env
  instance/
  __pycache__
  *.pyc
  .DS_Store
  venv/
  ```

#### Render Setup:
- [ ] Create Render account (free)
- [ ] New → Web Service
- [ ] Connect GitHub repo
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `gunicorn app:app`
- [ ] Set environment variables:
  - [ ] SECRET_KEY (generate random string)
  - [ ] FLASK_ENV=production
- [ ] Add Procfile (if needed):
  ```
  web: gunicorn app:app
  ```
- [ ] Deploy
- [ ] Test on production URL

#### First-time Production Setup:
- [ ] Manually create admin user in production database
- [ ] Or add initialization script to auto-create admin on first run
- [ ] Create 2-3 test setter users
- [ ] Test login on production

### 5.9 Test Day 5
- [ ] All flows work on production
- [ ] No console errors
- [ ] Mobile view works
- [ ] Dashboard loads fast
- [ ] Forms submit without errors
- [ ] Login/logout works
- [ ] Admin can manage users
- [ ] Setters can use CRM
- [ ] Ready to share with real user

---

## 👥 PHASE 6: REAL USER TESTING (DAY 6)

### 6.1 Prepare for Testing (30 mins)
- [ ] Create setter user account (give email + password)
- [ ] Send production URL
- [ ] Send quick guide:
  ```
  1. Login with your email
  2. Add a lead
  3. Mark it as messaged
  4. Set a follow-up date
  5. Come back tomorrow
  6. Mark as followed up
  7. Try booking a call
  ```

### 6.2 Watch Real User (90 mins)
- [ ] Have them share screen (or watch over shoulder)
- [ ] Ask them to complete above steps
- [ ] Don't help unless they ask
- [ ] Note:
  - [ ] Where did they get stuck?
  - [ ] What confused them?
  - [ ] What did they ignore?
  - [ ] What did they like?
  - [ ] What was slow?
  - [ ] What's missing?

### 6.3 Interview (30 mins)
- [ ] "What was easy?"
- [ ] "What was confusing?"
- [ ] "What's missing?"
- [ ] "Would you use this every day?"
- [ ] "What would make it 10x better?"
- [ ] "Any bugs you found?"

### 6.4 Document Findings
- [ ] List bugs (crashes, errors, wrong data)
- [ ] List confusing UX (unclear buttons, unclear flow)
- [ ] List missing features (but don't promise)
- [ ] List ideas they mentioned

---

## 🔧 PHASE 7: BUG FIXES + OPTIMIZATION (DAY 7)

### 7.1 Priority Bugs
- [ ] Fix crashes
- [ ] Fix data loss/corruption
- [ ] Fix broken flows
- [ ] Fix wrong calculations (follow-up date, status, etc.)

### 7.2 Confusing UX
- [ ] Simplify unclear labels
- [ ] Reorder buttons (most used = most prominent)
- [ ] Make "Overdue" section more obvious
- [ ] Clarify "Follow-up Done" button
- [ ] Better error messages

### 7.3 Performance
- [ ] If dashboard slow → check database queries (use .explain())
- [ ] If forms slow → check validation or file uploads
- [ ] If search slow → add indexing
- [ ] Check Render logs for errors

### 7.4 Final Testing
- [ ] Test all flows again
- [ ] Mobile test
- [ ] Browser test (Chrome, Firefox, Safari)
- [ ] Backup database
- [ ] Document any known issues

### 7.5 Ready for Team
- [ ] Write simple documentation:
  ```
  # How to Use Instagram Outreach CRM
  
  ## For Setters:
  1. Login with your email
  2. "Add Lead" to add new Instagram handle
  3. Use status buttons to update progress
  4. Set follow-up dates to never miss follow-ups
  5. Book calls when ready
  
  ## Admin Features (You):
  - Manage users (create, edit, delete)
  - View all leads
  - Monitor stats and performance
  - Reset user passwords
  ```
- [ ] Share login credentials with team
- [ ] Give production URL
- [ ] Offer support for first week

---

## 📋 RENDER DEPLOYMENT CHECKLIST

### Before Deploying:
- [ ] All code committed to GitHub
- [ ] No secrets in code (use .env)
- [ ] `.gitignore` includes .env, instance/, __pycache__
- [ ] `requirements.txt` up to date
- [ ] `Procfile` created (if Render asks for it)
- [ ] LOCAL testing done (flask run works perfectly)

### On Render:
- [ ] Web Service connected to GitHub
- [ ] Environment variables set (SECRET_KEY, FLASK_ENV)
- [ ] Build logs show no errors
- [ ] App running (check in Render dashboard)
- [ ] Can access production URL

### First-time Setup:
- [ ] Database auto-created (Flask-SQLAlchemy)
- [ ] Create admin user manually (SQL or script)
- [ ] Test login works
- [ ] Test CRM works
- [ ] Test admin panel works

### Monitoring:
- [ ] Check Render logs regularly (Logs tab)
- [ ] Monitor app uptime (should be 100%)
- [ ] Backup database weekly (download app.db)

---

## ✅ FINAL SUCCESS CRITERIA

**The CRM is ready when:**

✅ **Setter can:**
- [ ] Add lead in < 30 seconds
- [ ] Mark status in 1 click
- [ ] Set follow-up in < 1 minute
- [ ] Book call in 2 minutes
- [ ] See overdue follow-ups (red, can't miss)

✅ **Admin (You) can:**
- [ ] Create users + send credentials
- [ ] View all leads
- [ ] Monitor performance (stats)
- [ ] See activity log
- [ ] Override/manage any lead

✅ **System:**
- [ ] Fast (all pages < 2 seconds)
- [ ] Simple (no confusing buttons)
- [ ] Reliable (no crashes, no data loss)
- [ ] Mobile-friendly (works on phone)
- [ ] Deployed on Render (public URL)

✅ **Team:**
- [ ] Setter logs in successfully
- [ ] Setter uses CRM every day
- [ ] You can manage backend easily
- [ ] No support questions (it's obvious)

---

## 💡 POST-LAUNCH (AFTER REAL USAGE)

**ONLY add features if setters ask for them:**

Possible Phase 2:
- [ ] CSV import (bulk add leads)
- [ ] Better filtering/search
- [ ] Bulk status change
- [ ] Activity reports
- [ ] User performance leaderboard
- [ ] Slack notifications
- [ ] Google Calendar integration

---

## 📌 REMEMBER

**This is an MVP. The goal is:**
1. ✅ It works
2. ✅ You can manage users
3. ✅ Setters actually use it
4. ✅ No follow-ups are missed

**NOT:**
- ❌ Perfect code
- ❌ Beautiful design
- ❌ Complex features
- ❌ Scalability (yet)

---

**🚀 Ready to build? Start TODAY with PHASE 0-1. Follow the order. Deploy by Day 5. Launch by Day 7.**











