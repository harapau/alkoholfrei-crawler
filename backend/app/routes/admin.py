import threading

from flask import Blueprint, jsonify, request, render_template, current_app

bp = Blueprint('admin', __name__)

@bp.route('/', methods=['GET'])
def admin_page():
    """Gibt die Admin-Oberfläche zum Starten von Crawls zurück."""
    return render_template('admin.html')

@bp.route('/crawl/start', methods=['POST'])
def start_crawl():
    """Starte einen neuen Crawl-Vorgang für eine Winzer-URL."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL ist erforderlich"}), 400

    url = data['url']

    try:
        from app.tasks import crawl_winery
        task = crawl_winery.apply_async(args=[url])
        return jsonify({"message": f"Crawl für {url} gestartet!", "task_id": task.id})
    except Exception as exc:
        app = current_app._get_current_object()
        app.logger.warning('Celery konnte den Task nicht starten, wechsle auf Hintergrund-Thread.', exc_info=exc)
        start_crawl_in_background(url, app)
        return jsonify({
            "message": f"Crawl für {url} im Hintergrund gestartet (Fallback ohne Celery).",
            "detail": str(exc),
        }), 202


def start_crawl_in_background(url, app):
    from app.crawler.spider import WinerySpider

    def _run():
        with app.app_context():
            try:
                spider = WinerySpider(url)
                spider.crawl()
            except Exception:
                app.logger.exception('Fehler beim Hintergrund-Crawl')

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

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

@bp.route('/database/clear', methods=['POST'])
def clear_database():
    """Lösche alle Weine aus der Datenbank."""
    try:
        from app.models.wine import Wine
        from app import db
        count = Wine.query.delete()
        db.session.commit()
        return jsonify({
            "message": f"Datenbank geleert: {count} Wein(e) gelöscht.",
        }), 200
    except Exception as exc:
        current_app.logger.exception('Fehler beim Löschen der Datenbank')
        return jsonify({
            "error": "Fehler beim Löschen der Datenbank.",
            "detail": str(exc),
        }), 500
