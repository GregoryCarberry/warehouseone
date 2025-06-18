from flask import Flask
from .db import db
from .auth_routes import auth_bp
from .permissions import register_permission_hooks
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/warehouse'
    app.config['SESSION_TYPE'] = 'filesystem'

    CORS(app, supports_credentials=True)

    db.init_app(app)
    app.register_blueprint(auth_bp)

    register_permission_hooks(app)

    return app
