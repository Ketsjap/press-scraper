#!/usr/bin/env python3
"""
Media Press Feed Generator - Test Mode
Scrapes articles and fully scrapes first article as test
"""

import json
import sys
from datetime import datetime
from scrapers import VTMScraper

def print_test_results(items):
    """Print gedetailleerde test resultaten"""
    if not items:
        print("❌ No items scraped")
        return
    
    print("\n" + "="*70)
    print("📊 SCRAPING RESULTS")
    print("="*70)
    
    print(f"\nTotal articles found: {len(items)}")
    
    # Check eerste item voor volledige content
    first_item = items[0]
    has_content = 'content' in first_item
    
    print(f"\n{'✅' if has_content else '❌'} First article has full content: {has_content}")
    
    if has_content:
        content = first_item['content']
        print(f"\n📄 FIRST ARTICLE DETAILS:")
        print(f"   Title: {first_item['title'][:60]}...")
        print(f"   URL: {first_item['url']}")
        
        if 'published_date' in content:
            print(f"   Published: {content['published_date']}")
        
        if 'paragraphs' in content:
            print(f"   Paragraphs: {len(content['paragraphs'])}")
            print(f"   First paragraph: {content['paragraphs'][0][:100]}...")
        
        if 'image_url' in content:
            print(f"   Image: {content['image_url'][:60]}...")
        
        if 'meta_description' in content:
            print(f"   Meta desc: {content['meta_description'][:80]}...")
        
        if 'detected_programs' in content:
            print(f"   Detected TV programs: {', '.join(content['detected_programs'])}")
        
        if 'tags' in content:
            print(f"   Tags: {', '.join(content['tags'])}")
        
        print(f"\n   Available fields: {', '.join(content.keys())}")
    
    print(f"\n📋 OTHER ARTICLES (without full content):")
    for i, item in enumerate(items[1:6], 2):  # Show next 5
        print(f"   {i}. {item['title'][:60]}...")
    
    if len(items) > 6:
        print(f"   ... and {len(items) - 6} more")
    
    print("\n" + "="*70)

def main():
    """Main scraper orchestrator"""
    print(f"=== Media Press Scraper (TEST MODE) ===")
    print(f"Started at {datetime.now().isoformat()}\n")
    
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
        return 1
    
    # Sort by scraped_at
    all_items.sort(key=lambda x: x['scraped_at'], reverse=True)
    
    # Print test results
    print_test_results(all_items)
    
    # Write to feed.json
    output_file = 'feed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Output written to: {output_file}")
    
    if all_items:
        print(f"✅ Success! {len(all_items)} items scraped")
        if 'content' in all_items[0]:
            print(f"✅ First article has full content")
        return 0
    else:
        print("❌ ERROR: No items scraped!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
