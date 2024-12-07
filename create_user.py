from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists!")
