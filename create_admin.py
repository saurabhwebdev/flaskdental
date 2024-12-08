from app import db, create_app
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin_account():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        if not User.query.filter_by(email='admin@dentflow.com').first():
            admin = User(
                first_name='Admin',
                last_name='User',
                email='admin@dentflow.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin account created successfully!")
            print("Email: admin@dentflow.com")
            print("Password: admin123")
        else:
            print("Admin account already exists!")

if __name__ == '__main__':
    create_admin_account()
