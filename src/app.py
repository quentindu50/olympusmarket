"""
Flask application factory for the ambulance/transport management application.
"""

import os
from flask import Flask
from models import db


def create_app(config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///transport.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.missions import missions_bp
    from routes.patients import patients_bp
    from routes.drivers import drivers_bp
    from routes.vehicles import vehicles_bp
    from routes.billing import billing_bp
    from routes.messaging import messaging_bp
    from routes.admin import admin_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(missions_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(admin_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
