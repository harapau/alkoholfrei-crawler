from app import create_app
from celery import Celery

# Celery-Instanz erstellen
celery = Celery(__name__)

def init_celery(app):
    """Initialisiert Celery mit der Flask-App."""
    celery.conf.update(app.config)
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