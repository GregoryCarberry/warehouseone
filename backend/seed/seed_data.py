import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add /app to path

import random
from decimal import Decimal
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Permission, UserPermission, Store, Product

def ean13_like(n: int) -> str:
    """Return a 13‑digit zero‑padded string for barcode-like values."""
    return str(n).zfill(13)


def ean8_like(n: int) -> str:
    """Return an 8‑digit zero‑padded string for SKU values.

    EAN‑8 codes consist of eight numeric digits.  We generate simple
    sequential values by zero‑padding the provided integer up to eight
    digits.  When seeding, we start from a large base number to avoid
    leading zeros (e.g. 10000000 + i).
    """
    return str(n).zfill(8)

def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        perm_names = [
            '*',
            'view_users', 'view_permissions', 'grant_permissions',
            'view_stock', 'edit_stock', 'approve_orders',
            'view_products', 'make_orders',
            'view_reports'
        ]
        for name in perm_names:
            if not Permission.query.filter_by(name=name).first():
                db.session.add(Permission(name=name, description=f'Permission: {name}'))
        db.session.commit()

        if not User.query.filter_by(username='root').first():
            root = User(username='root', password_hash=generate_password_hash('rootpass'))
            db.session.add(root)
            db.session.commit()
            star = Permission.query.filter_by(name='*').first()
            db.session.add(UserPermission(user_id=root.user_id, permission_id=star.permission_id))
            db.session.commit()

        store = Store.query.filter_by(name='Main Store').first()
        if not store:
            store = Store(name='Main Store', address='123 Example St', contact='01234 567890')
            db.session.add(store)
            db.session.commit()

        base_price = Decimal('9.99')
        # Seed 100 products.  SKUs use an 8‑digit numeric string (EAN‑8 like).
        # We start from 10000000 + i to avoid leading zeros and ensure fixed length.
        for i in range(1, 101):
            sku = ean8_like(10000000 + i)
            name = f"Shampoo {i}"
            brand = f"Brand {((i - 1) % 10) + 1}"
            # Only create the product if it does not already exist with this SKU
            if not Product.query.filter_by(sku=sku).first():
                p = Product(
                    name=name,
                    sku=sku,
                    # The primary barcode remains EAN‑13 like for product labels.
                    barcode=ean13_like(200000000000 + i),
                    # Outer barcodes are optional and remain 13 digits.  Only every
                    # third product receives an outer barcode to demonstrate nulls.
                    outer_barcode=ean13_like(300000000000 + i) if i % 3 == 0 else None,
                    brand=brand,
                    description="Test product for seeding",
                    price=base_price,
                    stock=100,
                    low_stock_threshold=10,
                    store_id=None
                )
                db.session.add(p)
        db.session.commit()

        print("Seeding complete. Created root user (root/rootpass) and 100 products.")

if __name__ == '__main__':
    seed()
