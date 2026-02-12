"""
VTM Press Scraper
Scrapes https://communicatie.vtm.be
"""
from .base import BaseScraper

class VTMScraper(BaseScraper):
    """Scraper voor VTM persberichten"""
    
    def __init__(self):
        super().__init__('vtm')
    
    def get_base_url(self):
        return "https://communicatie.vtm.be"
    
    def scrape_articles(self):
        """Scrape alle artikelen van VTM communicatie site"""
        print(f"[VTM] Scraping {self.get_base_url()}...")
        
        soup = self.fetch_page(self.get_base_url())
        if not soup:
            return []
        
        items = []
        article_links = soup.select('a.card__link')
        
        print(f"[VTM] Found {len(article_links)} article links")
        
        for link in article_links:
            url = link.get('href', '')
            title = link.get_text(strip=True)
            
            if not title or not url:
                continue
            
            # Probeer datum te vinden (optioneel)
            date = None
            card = link.find_parent(class_='card')
            if card:
                date_elem = card.select_one('.card__date, .card__meta time')
                if date_elem:
                    date = date_elem.get_text(strip=True)
            
            # Probeer preview/beschrijving te vinden (optioneel)
            description = None
            if card:
                desc_elem = card.select_one('.card__description, .card__excerpt')
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
            
            extra = {}
            if description:
                extra['description'] = description
            
            items.append(self.create_item(
                title=title,
                url=url,
                date=date,
                extra_data=extra
            ))
        
        print(f"[VTM] Successfully scraped {len(items)} items")
        return items
