"""
VTM Press Scraper - Improved version with fallback selectors
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
        
        # Probeer verschillende selectors (VTM kan layout veranderen)
        selectors = [
            'a.card__link',           # Originele selector
            'article a',              # Alle links in artikel elementen
            'a[href*="/"]',           # Alle interne links
            '.article-card a',        # Alternatieve card class
            '.post a',                # Post links
        ]
        
        article_links = []
        for selector in selectors:
            article_links = soup.select(selector)
            if article_links:
                print(f"[VTM] Selector '{selector}' found {len(article_links)} links")
                break
        
        if not article_links:
            print("[VTM] ERROR: No article links found with any selector!")
            # Debug: print eerste 500 karakters van HTML
            print(f"[VTM] HTML preview: {str(soup)[:500]}")
            return []
        
        # Filter relevante links (geen menu items, etc)
        for link in article_links:
            url = link.get('href', '')
            
            # Skip externe links, anchors, menu items
            if not url or url.startswith('#') or url.startswith('http'):
                if url.startswith('http') and 'communicatie.vtm.be' not in url:
                    continue
            
            # Haal titel op (probeer verschillende elementen)
            title = None
            
            # Optie 1: Direct text in de link
            if link.get_text(strip=True):
                title = link.get_text(strip=True)
            
            # Optie 2: Heading in de link
            if not title:
                heading = link.find(['h1', 'h2', 'h3', 'h4'])
                if heading:
                    title = heading.get_text(strip=True)
            
            # Optie 3: Title attribuut
            if not title:
                title = link.get('title', '')
            
            # Skip als geen zinvolle titel
            if not title or len(title) < 10:
                continue
            
            # Probeer datum te vinden
            date = None
            parent = link.find_parent(['article', 'div', 'li'])
            if parent:
                # Zoek time element
                time_elem = parent.find('time')
                if time_elem:
                    date = time_elem.get('datetime') or time_elem.get_text(strip=True)
                
                # Of class met 'date' erin
                if not date:
                    date_elem = parent.find(class_=lambda x: x and 'date' in x.lower())
                    if date_elem:
                        date = date_elem.get_text(strip=True)
            
            # Probeer preview/beschrijving te vinden
            description = None
            if parent:
                desc_elem = parent.find(['p', 'div'], class_=lambda x: x and any(
                    word in x.lower() for word in ['excerpt', 'description', 'summary', 'intro']
                ))
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
        
        # Debug: print eerste 3 items
        if items:
            print(f"[VTM] Sample items:")
            for i, item in enumerate(items[:3]):
                print(f"  {i+1}. {item['title'][:60]}...")
        
        return items
