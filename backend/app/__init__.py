import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173"]}})

    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)

    from app.routes.health import bp as health_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.products import bp as products_bp

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(products_bp, url_prefix="/products")

    from app import models  # noqa: F401

    return app
