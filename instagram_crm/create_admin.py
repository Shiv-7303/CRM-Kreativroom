from app import create_app
from models import db, User

app = create_app()
with app.app_context():
    # Check if user already exists
    email = "admin@kr.com"
    user = User.query.filter_by(email=email).first()
    
    if not user:
        admin_user = User(
            email=email,
            role="admin"
        )
        admin_user.set_password("admin@0411")
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user {email} created successfully!")
    else:
        # Update existing user to admin and reset password just in case
        user.role = "admin"
        user.set_password("admin@0411")
        db.session.commit()
        print(f"User {email} already exists. Updated to admin and reset password.")
