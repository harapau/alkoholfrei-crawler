from app import create_app
from celery import Celery

# Celery-Instanz erstellen
celery = Celery(__name__)

def init_celery(app):
    """Initialisiert Celery mit der Flask-App."""
    celery.conf.update(app.config)
    # Unterstütze eine einfache Entwicklungs-Fallback-Option: "eager" Ausführung
    # Setze in der .env/Config: CELERY_TASK_ALWAYS_EAGER=1 oder True
    eager = app.config.get("CELERY_TASK_ALWAYS_EAGER", app.config.get("TASK_ALWAYS_EAGER", False))
    if isinstance(eager, str):
        eager = eager.lower() in ("1", "true", "yes")
    celery.conf.task_always_eager = bool(eager)
    return celery

# Task direkt registrieren (nicht in einer Funktion verstecken)
@celery.task(bind=True, max_retries=3)
def crawl_winery(self, base_url):
    from app.crawler.spider import WinerySpider
    from app import db
    try:
        spider = WinerySpider(base_url)
        success = spider.crawl()
        if success:
            return f"✅ Crawl für {base_url} erfolgreich abgeschlossen!"
        else:
            return f"⚠️ Crawl für {base_url} wurde blockiert (robots.txt)."
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return f"❌ Crawl für {base_url} fehlgeschlagen: {str(e)}"