#!/usr/bin/env python3
"""
Media Press Feed Generator - Debug Version
Scrapes multiple media press sites and combines into one JSON feed
"""

import json
import sys
from datetime import datetime
from scrapers import VTMScraper
# Later: from scrapers import VRTScraper

def inspect_html():
    """Debug functie om VTM HTML structuur te inspecteren"""
    import requests
    from bs4 import BeautifulSoup
    
    print("\n=== HTML INSPECTOR ===")
    url = "https://communicatie.vtm.be"
    
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Zoek alle links
        all_links = soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")
        
        # Analyseer welke classes gebruikt worden
        classes_used = set()
        for link in all_links:
            if link.get('class'):
                classes_used.update(link.get('class'))
        
        print(f"Link classes found: {', '.join(sorted(classes_used)[:10])}")
        
        # Print eerste 5 links met hun structure
        print("\nFirst 5 links:")
        for i, link in enumerate(all_links[:5]):
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            classes = ' '.join(link.get('class', []))
            print(f"{i+1}. [{classes}] {text}")
            print(f"   URL: {href}")
        
        # Zoek naar artikel containers
        containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
            word in str(x).lower() for word in ['post', 'article', 'card', 'item']
        ))
        print(f"\nArticle containers found: {len(containers)}")
        
    except Exception as e:
        print(f"Error inspecting HTML: {e}")
    
    print("=== END INSPECTOR ===\n")

def main():
    """Main scraper orchestrator"""
    print(f"=== Media Press Scraper Started at {datetime.now().isoformat()} ===\n")
    
    # Debug mode: inspect HTML first
    import os
    if os.environ.get('DEBUG') == '1':
        inspect_html()
    
    all_items = []
    
    # VTM Scraper
    try:
        vtm = VTMScraper()
        vtm_items = vtm.scrape_articles()
        all_items.extend(vtm_items)
    except Exception as e:
        print(f"[ERROR] VTM scraper failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    
    # VRT Scraper (later activeren)
    # try:
    #     vrt = VRTScraper()
    #     vrt_items = vrt.scrape_articles()
    #     all_items.extend(vrt_items)
    # except Exception as e:
    #     print(f"[ERROR] VRT scraper failed: {e}", file=sys.stderr)
    
    # Sorteer op scraped_at (nieuwste eerst)
    all_items.sort(key=lambda x: x['scraped_at'], reverse=True)
    
    # Schrijf naar feed.json
    output_file = 'feed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Scraping Complete ===")
    print(f"Total items: {len(all_items)}")
    
    if all_items:
        print(f"Output: {output_file}")
        print(f"Sources: {', '.join(set(item['source'] for item in all_items))}")
        return 0
    else:
        print("ERROR: No items scraped!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
