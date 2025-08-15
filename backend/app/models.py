from datetime import datetime
from . import db

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), nullable=False)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    valid_to = db.Column(db.DateTime, nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    permissions = db.relationship('Permission', secondary='user_permissions', backref='users')

class Permission(db.Model):
    __tablename__ = 'permissions'
    permission_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Store(db.Model):
    __tablename__ = 'stores'
    store_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255))
    contact = db.Column(db.String(120))

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    # Use 8-character numeric strings for SKUs (EAN‑8 like).  This field was
    # previously 13 characters wide but has been reduced to 8 to reflect the
    # intended EAN‑8 format.  Changing the length here will generate a new
    # Alembic migration the next time the container starts.
    sku = db.Column(db.String(8), unique=True, nullable=False)
    barcode = db.Column(db.String(13), unique=True, nullable=True)
    outer_barcode = db.Column(db.String(13), unique=True, nullable=True)
    brand = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=True)

class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.store_id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(40), nullable=False, default='PENDING')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_order = db.Column(db.Numeric(10, 2), nullable=False)
