from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisiere die Datenbank
    db.init_app(app)

    # Blueprints registrieren
    from app.routes.admin import bp as admin_bp
    from app.routes.api import bp as api_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app