from app import db
from sqlalchemy import Index

class Wine(db.Model):
    __tablename__ = "wines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=True)
    alcohol_content = db.Column(db.Float, nullable=True)  # z. B. 0.0 statt "0,0%"
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False, unique=True)  # UNIQUE-Constraint
    winery = db.Column(db.String(200), nullable=False, index=True)  # Index für schnelle Abfragen
    winery_url = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    last_crawled = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)  # Opt-out-Mechanismus

    # Index für häufige Abfragen
    __table_args__ = (
        Index("idx_wine_alcohol", "alcohol_content"),
        Index("idx_wine_winery", "winery"),
    )

    def __repr__(self):
        return f"<Wine {self.name} ({self.winery})>"