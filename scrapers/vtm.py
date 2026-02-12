"""
VTM Press Scraper - Test version with full article scraping
Scrapes https://communicatie.vtm.be
"""
from .base import BaseScraper
import time

class VTMScraper(BaseScraper):
    """Scraper voor VTM persberichten"""
    
    def __init__(self):
        super().__init__('vtm')
    
    def get_base_url(self):
        return "https://communicatie.vtm.be"
    
    def scrape_article_content(self, url):
        """
        Scrape volledige artikel content van een specifieke URL
        Returns dict met gedetailleerde info
        """
        print(f"[VTM] Scraping article details: {url}")
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        details = {}
        
        # 1. Hoofd content - probeer verschillende selectors
        article_content = None
        
        # Probeer verschillende article containers
        for selector in ['article', '.article-content', '.content', 'main', '.post-content']:
            article_content = soup.select_one(selector)
            if article_content:
                print(f"[VTM] Found article content with selector: {selector}")
                break
        
        if article_content:
            # Extract alle paragrafen
            paragraphs = []
            for p in article_content.find_all('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 20:  # Skip hele korte paragraphs
                    paragraphs.append(text)
            
            if paragraphs:
                details['paragraphs'] = paragraphs
                details['full_text'] = ' '.join(paragraphs)
                details['summary'] = paragraphs[0] if paragraphs else None
                print(f"[VTM] Extracted {len(paragraphs)} paragraphs")
        
        # 2. Publicatiedatum - meerdere plekken proberen
        date_found = None
        
        # Probeer time element
        time_elem = soup.find('time')
        if time_elem:
            date_found = time_elem.get('datetime') or time_elem.get_text(strip=True)
            print(f"[VTM] Found date in <time>: {date_found}")
        
        # Probeer meta tag
        if not date_found:
            meta_date = soup.find('meta', property='article:published_time')
            if meta_date:
                date_found = meta_date.get('content')
                print(f"[VTM] Found date in meta: {date_found}")
        
        # Probeer class met 'date' of 'published'
        if not date_found:
            date_elem = soup.find(class_=lambda x: x and any(
                word in str(x).lower() for word in ['date', 'published', 'time']
            ))
            if date_elem:
                date_found = date_elem.get_text(strip=True)
                print(f"[VTM] Found date in element: {date_found}")
        
        if date_found:
            details['published_date'] = date_found
        
        # 3. Hero/Featured image
        img_found = None
        
        # Probeer verschillende image selectors
        for selector in [
            'img.hero-image',
            'img.featured-image', 
            '.article-image img',
            'article img',
            'meta[property="og:image"]'
        ]:
            if selector.startswith('meta'):
                meta_img = soup.select_one(selector)
                if meta_img:
                    img_found = meta_img.get('content')
                    break
            else:
                img_elem = soup.select_one(selector)
                if img_elem:
                    img_found = img_elem.get('src')
                    break
        
        if img_found:
            details['image_url'] = self.make_absolute_url(img_found)
            print(f"[VTM] Found image: {img_found[:50]}...")
        
        # 4. Meta description (vaak goede samenvatting)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', property='og:description')
        
        if meta_desc:
            details['meta_description'] = meta_desc.get('content')
            print(f"[VTM] Found meta description: {details['meta_description'][:60]}...")
        
        # 5. Categorie/Tags
        tags = []
        for tag_elem in soup.find_all(['a'], class_=lambda x: x and 'tag' in str(x).lower()):
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        if tags:
            details['tags'] = tags
            print(f"[VTM] Found tags: {', '.join(tags)}")
        
        # 6. Probeer TV-programma naam te vinden (vaak in titel of eerste paragraph)
        # Dit wordt later verfijnd met AI, maar we kunnen al proberen
        program_keywords = ['the voice', 'thuis', 'familie', 'vtm nieuws', 'telefacts', 
                           'love island', 'bestemming x', 'got talent']
        
        full_text_lower = details.get('full_text', '').lower()
        detected_programs = [kw for kw in program_keywords if kw in full_text_lower]
        
        if detected_programs:
            details['detected_programs'] = detected_programs
            print(f"[VTM] Detected programs: {', '.join(detected_programs)}")
        
        return details
    
    def scrape_articles(self):
        """Scrape alle artikelen van VTM communicatie site"""
        print(f"[VTM] Scraping {self.get_base_url()}...")
        
        soup = self.fetch_page(self.get_base_url())
        if not soup:
            return []
        
        items = []
        
        # Probeer verschillende selectors
        selectors = [
            'a.card__link',
            'article a',
            'a[href*="/"]',
            '.article-card a',
            '.post a',
        ]
        
        article_links = []
        for selector in selectors:
            article_links = soup.select(selector)
            if article_links:
                print(f"[VTM] Selector '{selector}' found {len(article_links)} links")
                break
        
        if not article_links:
            print("[VTM] ERROR: No article links found!")
            return []
        
        # Process alle links
        for link in article_links:
            url = link.get('href', '')
            
            # Skip externe links, anchors, menu items
            if not url or url.startswith('#'):
                continue
            
            if url.startswith('http') and 'communicatie.vtm.be' not in url:
                continue
            
            # Haal titel op
            title = None
            if link.get_text(strip=True):
                title = link.get_text(strip=True)
            
            if not title:
                heading = link.find(['h1', 'h2', 'h3', 'h4'])
                if heading:
                    title = heading.get_text(strip=True)
            
            if not title:
                title = link.get('title', '')
            
            # Skip als geen zinvolle titel
            if not title or len(title) < 10:
                continue
            
            # Probeer datum te vinden
            date = None
            parent = link.find_parent(['article', 'div', 'li'])
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    date = time_elem.get('datetime') or time_elem.get_text(strip=True)
                
                if not date:
                    date_elem = parent.find(class_=lambda x: x and 'date' in str(x).lower())
                    if date_elem:
                        date = date_elem.get_text(strip=True)
            
            # Probeer preview/beschrijving te vinden
            description = None
            if parent:
                desc_elem = parent.find(['p', 'div'], class_=lambda x: x and any(
                    word in str(x).lower() for word in ['excerpt', 'description', 'summary', 'intro']
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
        
        print(f"[VTM] Successfully scraped {len(items)} article links")
        
        # 🔥 NIEUW: Scrape het EERSTE artikel volledig als test
        if items:
            print(f"\n[VTM] === TEST: Scraping first article in full ===")
            first_item = items[0]
            
            # Wacht even (respecteer de website)
            time.sleep(1)
            
            # Haal volledige content op
            article_details = self.scrape_article_content(first_item['url'])
            
            if article_details:
                # Voeg details toe aan eerste item
                first_item['content'] = article_details
                print(f"[VTM] ✅ Successfully added full content to first article")
                print(f"[VTM] Content keys: {list(article_details.keys())}")
                
                # Show preview
                if 'summary' in article_details:
                    print(f"[VTM] Summary preview: {article_details['summary'][:100]}...")
            else:
                print(f"[VTM] ❌ Failed to scrape article content")
            
            print(f"[VTM] === END TEST ===\n")
        
        return items
