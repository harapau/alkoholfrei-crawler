import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import re
from app.models.wine import Wine
from app import db
from config import Config
from requests.exceptions import RequestException

class WinerySpider:
    def __init__(self, base_url, rate_limit=None):
        self.base_url = base_url
        self.rate_limit = rate_limit if rate_limit else Config.RATE_LIMIT
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})
        self.domain = "/".join(base_url.split("/")[:3])

    def check_robots_txt(self):
        """Prüfe, ob Crawling erlaubt ist."""
        robots_url = urljoin(self.domain, "/robots.txt")
        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                return "Disallow: /" not in response.text
            return True  # Erlaube Crawling, falls robots.txt nicht existiert
        except RequestException:
            return True  # Im Zweifel erlauben (konservativ)

    def fetch_page(self, url, max_retries=3):
        """Lade eine Seite mit Retry-Logik."""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()  # HTTP-Errors (4xx/5xx) auslösen
                return response
            except RequestException as e:
                print(f"⚠️ Versuch {attempt + 1}/{max_retries} für {url} fehlgeschlagen: {e}")
                time.sleep(2 ** attempt)  # Exponentielles Backoff
        return None

    def parse_product(self, url):
        """Extrahiere Wein-Daten von einer Produktseite."""
        response = self.fetch_page(url)
        if not response:
            print(f"❌ Konnte {url} nicht laden.")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Flexible Selektoren (Beispiel: Mehrere mögliche Klassen)
        name_selectors = ["h1.product-title", "h1", ".product-name"]
        price_selectors = [".price", ".product-price", "[itemprop=price]"]
        alcohol_selectors = [".alcohol-content", ".alcohol", "[itemprop=alcohol]"]

        name = self._extract_text(soup, name_selectors)
        price = self._extract_price(soup, price_selectors)
        alcohol = self._extract_text(soup, alcohol_selectors)

        if not name:
            print(f"⚠️ Kein Name gefunden für {url}")
            return None

        # Prüfe, ob der Wein bereits in der DB existiert
        existing_wine = Wine.query.filter_by(url=url).first()
        if existing_wine:
            print(f"ℹ️ Wein {name} bereits in der DB (URL: {url})")
            return None

        # Speichere in der DB
        wine = Wine(
            name=name,
            price=price,
            alcohol_content=alcohol,
            url=url,
            winery=self.base_url,
            winery_url=self.domain,
        )
        db.session.add(wine)
        db.session.commit()
        print(f"✅ Wein gespeichert: {name} ({url})")
        return wine

    def _extract_text(self, soup, selectors):
        """Extrahiere Text aus dem ersten passenden Selektor."""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None

    def _extract_price(self, soup, selectors):
        """Extrahiere Preis und konvertiere zu Float."""
        text = self._extract_text(soup, selectors)
        if not text:
            return None
        # Entferne Währungssymbole und Tausendertrennzeichen
        price_str = re.sub(r"[€\$,]", "", text).replace(".", "").strip()
        try:
            return float(price_str.replace(",", "."))
        except ValueError:
            return None

    def crawl(self):
        """Starte den Crawl-Vorgang."""
        if not self.check_robots_txt():
            print(f"⚠️ Crawling von {self.base_url} durch robots.txt blockiert!")
            return False

        print(f"🔍 Starte Crawl für {self.base_url}")
        response = self.fetch_page(self.base_url)
        if not response:
            print(f"❌ Konnte Startseite {self.base_url} nicht laden.")
            return False

        soup = BeautifulSoup(response.text, "html.parser")
        # Beispiel: Finde alle Produkt-Links (anpassbar)
        product_links = []
        for a in soup.select("a[href]"):
            href = a["href"]
            if re.search(r"/wein|/produkt|/shop", href, re.IGNORECASE):
                product_links.append(urljoin(self.base_url, href))

        # Entferne Duplikate
        product_links = list(set(product_links))

        for link in product_links:
            self.parse_product(link)
            time.sleep(self.rate_limit)

        print(f"✅ Crawl für {self.base_url} abgeschlossen.")
        return True