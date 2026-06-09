import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from app.models.wine import Wine
from app import db
import config #diese Zeite habe ich hinzugefügt, damit ich auf die User-Agent-Konstante zugreifen kann

class WinerySpider:
    def __init__(self, base_url, rate_limit=2):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT})

    def check_robots_txt(self):
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                return "Disallow: /" not in response.text
        except:
            return True  # Standardmäßig erlaubt, falls robots.txt nicht erreichbar
        return False

    def crawl(self):
        if not self.check_robots_txt():
            print(f"⚠️ Crawling von {self.base_url} durch robots.txt blockiert!")
            return

        # Hier kommt die Crawl-Logik hin (z. B. Produkte extrahieren)
        # Beispiel: Alle Links auf der Startseite sammeln
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        product_links = [a["href"] for a in soup.select("a.product-link")]

        for link in product_links:
            product_url = urljoin(self.base_url, link)
            self.parse_product(product_url)
            time.sleep(self.rate_limit)  # Rate Limiting

    def parse_product(self, url):
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Extrahiere Name, Preis, Alkoholgehalt, etc.
        name = soup.select_one("h1.product-title").text.strip()
        price = float(soup.select_one(".price").text.replace("€", "").strip())
        alcohol = soup.select_one(".alcohol-content").text.strip()

        # Speichere in Datenbank
        wine = Wine(
            name=name,
            price=price,
            alcohol_content=alcohol,
            url=url,
            winery=self.base_url,
        )
        db.session.add(wine)
        db.session.commit()