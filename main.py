#!/usr/bin/env python3
"""
Media Press Feed Generator
Scrapes multiple media press sites and combines into one JSON feed
"""

import json
import sys
from datetime import datetime
from scrapers import VTMScraper
# Later: from scrapers import VRTScraper

def main():
    """Main scraper orchestrator"""
    print(f"=== Media Press Scraper Started at {datetime.now().isoformat()} ===\n")
    
    all_items = []
    
    # VTM Scraper
    try:
        vtm = VTMScraper()
        vtm_items = vtm.scrape_articles()
        all_items.extend(vtm_items)
    except Exception as e:
        print(f"[ERROR] VTM scraper failed: {e}", file=sys.stderr)
    
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
    print(f"Output: {output_file}")
    print(f"Sources: {', '.join(set(item['source'] for item in all_items))}")
    
    return 0 if all_items else 1

if __name__ == '__main__':
    sys.exit(main())
