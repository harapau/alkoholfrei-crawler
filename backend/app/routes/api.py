from flask import Blueprint

# API-Blueprint erstellen
bp = Blueprint('api', __name__)

@bp.route('/api/wines')
def get_wines():
    return "API: Liste der Weine"