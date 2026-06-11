from flask import Blueprint, jsonify, request
from app import create_app

bp = Blueprint('admin', __name__)

@bp.route('/crawl/start', methods=['POST'])
def start_crawl():
    """Starte einen neuen Crawl-Vorgang für eine Winzer-URL."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL ist erforderlich"}), 400

    url = data['url']

    # Celery-Task asynchron aufrufen
    from app.tasks import celery
    task = celery.send_task('crawl_winery', args=[url])
    return jsonify({"message": f"Crawl für {url} gestartet!", "task_id": task.id})

@bp.route('/wines', methods=['GET'])
def list_wines():
    """Liste alle Weine in der Admin-Oberfläche auf."""
    from app.models.wine import Wine
    wines = Wine.query.all()
    return jsonify([{
        "id": wine.id,
        "name": wine.name,
        "winery": wine.winery,
        "url": wine.url,
        "is_active": wine.is_active,
    } for wine in wines])