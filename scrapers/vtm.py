"""
VTM Press Scraper - Full version
Scrapes ALL articles from https://communicatie.vtm.be with complete content
"""
from .base import BaseScraper
import time

class VTMScraper(BaseScraper):
    """Scraper voor VTM persberichten"""
    
    def __init__(self):
        super().__init__('vtm')
        self.scrape_delay = 1.0  # Seconden tussen requests (respecteer de server)
    
    def get_base_url(self):
        return "https://communicatie.vtm.be"
    
    def scrape_article_content(self, url):
        """
        Scrape volledige artikel content van een specifieke URL
        Returns dict met gedetailleerde info
        """
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
        
        # 2. Publicatiedatum - meerdere plekken proberen
        date_found = None
        
        # Probeer time element
        time_elem = soup.find('time')
        if time_elem:
            date_found = time_elem.get('datetime') or time_elem.get_text(strip=True)
        
        # Probeer meta tag
        if not date_found:
            meta_date = soup.find('meta', property='article:published_time')
            if meta_date:
                date_found = meta_date.get('content')
        
        # Probeer class met 'date' of 'published'
        if not date_found:
            date_elem = soup.find(class_=lambda x: x and any(
                word in str(x).lower() for word in ['date', 'published', 'time']
            ))
            if date_elem:
                date_found = date_elem.get_text(strip=True)
        
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
        
        # 4. Meta description (vaak goede samenvatting)
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', property='og:description')
        
        if meta_desc:
            details['meta_description'] = meta_desc.get('content')
        
        # 5. Categorie/Tags
        tags = []
        for tag_elem in soup.find_all(['a'], class_=lambda x: x and 'tag' in str(x).lower()):
            tag_text = tag_elem.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)
        
        if tags:
            details['tags'] = tags
        
        # 6. Auto-detectie van TV-programma namen
        program_keywords = [
            'the voice', 'thuis', 'familie', 'vtm nieuws', 'het nieuws',
            'telefacts', 'love island', 'bestemming x', 'got talent',
            'de box', 'winter vol liefde', 'een echte job', 'florentina',
            'moordzaken', 'so you think you can dance', 'de mol'
        ]
        
        full_text_lower = details.get('full_text', '').lower()
        detected_programs = [kw for kw in program_keywords if kw in full_text_lower]
        
        if detected_programs:
            details['detected_programs'] = detected_programs
        
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
        
        # Process alle links - maak eerst basis items
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
        
        print(f"[VTM] Found {len(items)} article links")
        
        # 🔥 NIEUW: Scrape ALLE artikelen volledig
        print(f"\n[VTM] === Scraping full content for all {len(items)} articles ===")
        
        scraped_count = 0
        failed_count = 0
        
        for i, item in enumerate(items, 1):
            print(f"[VTM] [{i}/{len(items)}] Scraping: {item['title'][:50]}...")
            
            # Wacht tussen requests (respecteer de server)
            if i > 1:
                time.sleep(self.scrape_delay)
            
            try:
                article_details = self.scrape_article_content(item['url'])
                
                if article_details:
                    item['content'] = article_details
                    scraped_count += 1
                    
                    # Short preview
                    if 'summary' in article_details:
                        print(f"[VTM]    ✅ {article_details['summary'][:60]}...")
                    else:
                        print(f"[VTM]    ✅ Content scraped")
                else:
                    failed_count += 1
                    print(f"[VTM]    ⚠️  No content found")
                    
            except Exception as e:
                failed_count += 1
                print(f"[VTM]    ❌ Error: {e}")
        
        print(f"\n[VTM] === Scraping complete ===")
        print(f"[VTM] ✅ Success: {scraped_count}/{len(items)} articles")
        print(f"[VTM] ❌ Failed: {failed_count}/{len(items)} articles")
        
        return items
