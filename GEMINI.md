# KreativeRoom CRM (Instagram Outreach)

## Project Overview

KreativeRoom CRM is a Flask-based Instagram outreach management system. It is designed with a clear separation of concerns between two main user roles: **Admin** (management, system health, and reporting) and **Setter** (daily outreach operations, lead management). 

The system tracks "Leads" through a defined pipeline (New -> Messaged -> Replied -> Interested -> Call Booked -> Deal Done) and features a prominent follow-up system for setters to manage daily tasks efficiently.

### Technologies
*   **Backend:** Python, Flask (Application Factory pattern)
*   **Database:** SQLite (local) / PostgreSQL (production) with SQLAlchemy ORM
*   **Frontend:** HTML/Jinja2 templates styled with Tailwind CSS
*   **Dependencies:** Flask-Login, Werkzeug, python-dotenv, Gunicorn

## Directory Structure

The core application code is located in the `instagram_crm/` directory:
*   `app.py`: Main application factory and blueprint registration.
*   `models.py`: Database schema (User, Lead, Call, Activity) and logging utilities.
*   `admin.py`: Admin blueprint (reporting, user management, global lead overrides).
*   `crm.py`: Setter blueprint (operational dashboard, lead workflow).
*   `auth.py`: Authentication and role-based redirection.
*   `templates/`: Jinja2 HTML templates.
*   `static/`: Compiled Tailwind CSS and other static assets.

## Building and Running

### Prerequisites
*   Python 3.x
*   Node.js & npm (for Tailwind CSS)

### Setup & Run
1.  **Backend Setup:**
    Navigate to the project folder and install Python dependencies.
    ```bash
    cd instagram_crm
    pip install -r requirements.txt
    ```
2.  **Initialize Database:**
    ```bash
    python init_db.py
    ```
    *(You may also need to run `python create_admin.py` if an initial admin user is required).*

3.  **Frontend Setup (Tailwind CSS):**
    Install npm dependencies and build the CSS.
    ```bash
    npm install
    npm run build
    ```

4.  **Run the Development Server:**
    ```bash
    flask run
    # or
    python app.py
    ```

### Testing
Tests are written using `pytest`. The main test suite for the admin and CRM functionality is located in `t_admin.py`.
```bash
cd instagram_crm
pytest t_admin.py -v
```

## Development Conventions

*   **Modularity:** The application logic is strictly separated into Blueprints (`auth`, `admin`, `crm`). Keep role-specific logic within its respective blueprint.
*   **Role-Based Access Control (RBAC):** Use the custom decorators `@admin_required` and `@setter_required` to restrict route access.
*   **Auditability:** Use the `log_activity(user_id, action, lead_id)` function from `models.py` to meticulously log significant actions (status changes, booked calls, user creation) to provide a transparent audit trail.
*   **Styling:** Prefer vanilla HTML with Tailwind CSS utility classes. Avoid writing custom CSS unless absolutely necessary. Run `npm run build` when modifying Tailwind classes in templates.
*   **Validation:** All new features or bug fixes must be verified by running the `t_admin.py` test suite. Ensure any new setter or admin routes are covered by corresponding access control tests.
