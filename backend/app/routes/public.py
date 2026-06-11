from flask import Blueprint, render_template
from app.models.wine import Wine

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    return render_template('public/index.html')