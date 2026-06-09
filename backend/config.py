import os
from dotenv import load_dotenv

load_dotenv()  # Lädt Umgebungsvariablen aus .env

class Config:
    # Datenbank
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///wines.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery (für Hintergrund-Crawls)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Crawler-Einstellungen
    RATE_LIMIT = 2  # Sekunden zwischen Anfragen pro Domain
    USER_AGENT = "AlkoholfreiCrawler/1.0 (+https://deine-plattform.de/bot-info)"