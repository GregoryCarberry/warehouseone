from warehouse.models import db, User, Permission
from werkzeug.security import generate_password_hash
from warehouse import create_app

app = create_app()

def seed():
    with app.app_context():
        if not Permission.query.first():
            permissions = [
                Permission(name='view_products', description='Can view products'),
                Permission(name='make_orders', description='Can make orders'),
                Permission(name='edit_stock', description='Can edit stock'),
                Permission(name='manage_users', description='Can manage user accounts')
            ]
            db.session.add_all(permissions)
            db.session.commit()
        else:
            permissions = Permission.query.all()

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('adminpass'))
            db.session.add(admin)
            admin.permissions.extend(permissions)

        if not User.query.filter_by(username='staff').first():
            staff = User(username='staff', password_hash=generate_password_hash('staffpass'))
            db.session.add(staff)
            staff.permissions.append(next(p for p in permissions if p.name == 'view_products'))

        db.session.commit()
        print("Seeded users and permissions.")

if __name__ == '__main__':
    seed()
