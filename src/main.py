# MediRoute — Système de Gestion du Transport Médical
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from src.database import init_db
from src.routes.auth import auth_bp
from src.routes.patients import patients_bp
from src.routes.drivers import drivers_bp
from src.routes.vehicles import vehicles_bp
from src.routes.missions import missions_bp
from src.routes.messages import messages_bp
from src.routes.invoices import invoices_bp
from src.routes.dashboard import dashboard_bp
from src.routes.establishments import establishments_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///mediroute.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "mediroute-dev-secret")

    if config:
        app.config.update(config)

    JWTManager(app)
    init_db(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(missions_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(establishments_bp)

    return app


def main():
    print("Welcome to MediRoute — Système de Gestion du Transport Médical")
    app = create_app()
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)


if __name__ == "__main__":
    main()