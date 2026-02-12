"""
Base scraper class - alle scrapers erven hiervan
"""
from abc import ABC, abstractmethod
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class BaseScraper(ABC):
    """Basis class voor alle media scrapers"""
    
    def __init__(self, source_name):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    @abstractmethod
    def get_base_url(self):
        """Return de basis URL van de bron"""
        pass
    
    @abstractmethod
    def scrape_articles(self):
        """Scrape artikelen en return lijst van dicts"""
        pass
    
    def fetch_page(self, url, timeout=10):
        """Helper om pagina op te halen"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"[{self.source_name}] Error fetching {url}: {e}")
            return None
    
    def make_absolute_url(self, url):
        """Maak relatieve URL absoluut"""
        if url.startswith('http'):
            return url
        return self.get_base_url() + url
    
    def create_item(self, title, url, date=None, extra_data=None):
        """Standaard item structuur"""
        item = {
            'title': title,
            'url': self.make_absolute_url(url),
            'source': self.source_name,
            'scraped_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        if date:
            item['date'] = date
        
        if extra_data:
            item.update(extra_data)
        
        return item
