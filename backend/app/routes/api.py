from flask import Blueprint, jsonify, request
from app.models.wine import Wine
from app import db

bp = Blueprint('api', __name__)

@bp.route('/wines', methods=['GET'])
def get_wines():
    """Gibe eine gefilterte Liste aller Weine zurück."""
    # Filter-Parameter aus der Anfrage
    alcohol = request.args.get('alcohol', type=float)  # z. B. ?alcohol=0.0
    winery = request.args.get('winery')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Basis-Abfrage
    query = Wine.query.filter_by(is_active=True)

    # Filter anwenden
    if alcohol is not None:
        query = query.filter(Wine.alcohol_content == alcohol)
    if winery:
        query = query.filter(Wine.winery.ilike(f"%{winery}%"))
    if min_price is not None:
        query = query.filter(Wine.price >= min_price)
    if max_price is not None:
        query = query.filter(Wine.price <= max_price)

    # Ergebnisse zurückgeben
    wines = query.all()
    return jsonify([{
        "id": wine.id,
        "name": wine.name,
        "price": wine.price,
        "alcohol_content": wine.alcohol_content,
        "url": wine.url,
        "winery": wine.winery,
        "latitude": wine.latitude,
        "longitude": wine.longitude,
    } for wine in wines])

@bp.route('/wines/<int:wine_id>', methods=['GET'])
def get_wine(wine_id):
    """Gibe Details zu einem bestimmten Wein zurück."""
    wine = Wine.query.get_or_404(wine_id)
    return jsonify({
        "id": wine.id,
        "name": wine.name,
        "price": wine.price,
        "alcohol_content": wine.alcohol_content,
        "description": wine.description,
        "url": wine.url,
        "winery": wine.winery,
        "winery_url": wine.winery_url,
        "latitude": wine.latitude,
        "longitude": wine.longitude,
        "last_crawled": wine.last_crawled.isoformat(),
    })