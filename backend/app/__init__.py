import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    templates_path = os.path.join(base_dir, 'frontend', 'templates')
    static_path = os.path.join(base_dir, 'frontend', 'static')
    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)
    app.config.from_object(config_class)

    # Initialisiere die Datenbank
    db.init_app(app)
    migrate.init_app(app, db)

    # Celery initialisieren
    from app.tasks import celery, init_celery
    init_celery(app)

    # Blueprints registrieren
    from app.routes.admin import bp as admin_bp
    from app.routes.api import bp as api_bp
    from app.routes.public import bp as public_bp

    app.register_blueprint(public_bp, url_prefix=None)  # Öffentliche Routen ohne Präfix
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app