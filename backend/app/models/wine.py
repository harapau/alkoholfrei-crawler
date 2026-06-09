from app import db

class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=True)
    alcohol_content = db.Column(db.String(20), nullable=True)  # z. B. "0,0%"
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    winery = db.Column(db.String(200), nullable=False)
    winery_url = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)  # Für Karte
    longitude = db.Column(db.Float, nullable=True)  # Für Karte
    last_crawled = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)  # Opt-out-Mechanismus

    def __repr__(self):
        return f"<Wine {self.name} ({self.winery})>"