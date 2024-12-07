from app import create_app, db
from app.models.user import User
from app.models.settings import Settings

def setup_database():
    app = create_app()
    with app.app_context():
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create default settings if not exists
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
        
        db.session.commit()
        print('Admin user and default settings created.')

if __name__ == '__main__':
    setup_database()
