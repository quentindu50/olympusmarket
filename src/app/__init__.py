from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    from .config import Config
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    db.init_app(app)

    from .routes.dashboard import dashboard_bp
    from .routes.patients import patients_bp
    from .routes.drivers import drivers_bp
    from .routes.vehicles import vehicles_bp
    from .routes.transports import transports_bp
    from .routes.invoices import invoices_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(drivers_bp, url_prefix='/drivers')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(transports_bp, url_prefix='/transports')
    app.register_blueprint(invoices_bp, url_prefix='/invoices')

    with app.app_context():
        db.create_all()

    return app
