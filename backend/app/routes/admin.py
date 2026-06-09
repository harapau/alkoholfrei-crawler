from flask import Blueprint

# Admin-Blueprint erstellen
bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin_dashboard():
    return "Admin Dashboard"