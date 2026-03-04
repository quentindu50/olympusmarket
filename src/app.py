import os
from flask import Flask
from extensions import db, csrf


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vitaltransport-secret-key-2024')
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vitaltransport.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    csrf.init_app(app)

    from routes.dashboard import dashboard_bp
    from routes.patients import patients_bp
    from routes.drivers import drivers_bp
    from routes.vehicles import vehicles_bp
    from routes.transports import transports_bp
    from routes.billing import billing_bp
    from routes.messages import messages_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(transports_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(messages_bp)

    with app.app_context():
        from models import Patient, Driver, Vehicle, Transport, Billing, Message  # noqa: F401
        db.create_all()

    return app
