from celery import Celery
from app import create_app
from app.crawler.spider import WinerySpider

app = create_app()
celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])

@celery.task
def crawl_winery(base_url):
    spider = WinerySpider(base_url)
    spider.crawl()
    return f"Crawl für {base_url} abgeschlossen!"