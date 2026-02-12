#!/usr/bin/env python3
"""
Media Press Feed Generator - Full Production Version
Scrapes all articles with complete content
"""

import json
import sys
from datetime import datetime
from scrapers import VTMScraper

def print_statistics(items):
    """Print gedetailleerde statistieken"""
    if not items:
        print("❌ No items scraped")
        return
    
    print("\n" + "="*70)
    print("📊 SCRAPING STATISTICS")
    print("="*70)
    
    total = len(items)
    with_content = sum(1 for item in items if 'content' in item)
    with_images = sum(1 for item in items if 'content' in item and 'image_url' in item['content'])
    with_programs = sum(1 for item in items if 'content' in item and 'detected_programs' in item['content'])
    
    print(f"\n📈 Overall:")
    print(f"   Total articles: {total}")
    print(f"   With full content: {with_content} ({100*with_content//total}%)")
    print(f"   With images: {with_images} ({100*with_images//total if total else 0}%)")
    print(f"   With detected programs: {with_programs} ({100*with_programs//total if total else 0}%)")
    
    # Collect all detected programs
    all_programs = []
    for item in items:
        if 'content' in item and 'detected_programs' in item['content']:
            all_programs.extend(item['content']['detected_programs'])
    
    if all_programs:
        from collections import Counter
        program_counts = Counter(all_programs)
        print(f"\n📺 Detected TV Programs:")
        for prog, count in program_counts.most_common(10):
            print(f"   {prog}: {count} article(s)")
    
    # Average content length
    text_lengths = [
        len(item['content'].get('full_text', '')) 
        for item in items 
        if 'content' in item and 'full_text' in item['content']
    ]
    
    if text_lengths:
        avg_length = sum(text_lengths) // len(text_lengths)
        print(f"\n📝 Content Stats:")
        print(f"   Average article length: {avg_length} characters")
        print(f"   Shortest: {min(text_lengths)} chars")
        print(f"   Longest: {max(text_lengths)} chars")
    
    # Sample articles
    print(f"\n📄 Sample Articles (first 3 with content):")
    count = 0
    for item in items:
        if 'content' in item and count < 3:
            count += 1
            content = item['content']
            print(f"\n   {count}. {item['title'][:60]}...")
            print(f"      URL: {item['url'][:50]}...")
            if 'published_date' in content:
                print(f"      Date: {content['published_date']}")
            if 'detected_programs' in content:
                print(f"      Programs: {', '.join(content['detected_programs'])}")
            if 'paragraphs' in content:
                print(f"      Paragraphs: {len(content['paragraphs'])}")
    
    print("\n" + "="*70)

def main():
    """Main scraper orchestrator"""
    print(f"=== Media Press Scraper (FULL VERSION) ===")
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
    
    # Future: VRT Scraper
    # try:
    #     vrt = VRTScraper()
    #     vrt_items = vrt.scrape_articles()
    #     all_items.extend(vrt_items)
    # except Exception as e:
    #     print(f"[ERROR] VRT scraper failed: {e}", file=sys.stderr)
    
    # Sort by scraped_at (newest first)
    all_items.sort(key=lambda x: x['scraped_at'], reverse=True)
    
    # Print statistics
    print_statistics(all_items)
    
    # Write to feed.json
    output_file = 'feed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Output written to: {output_file}")
    
    # Calculate file size
    import os
    file_size = os.path.getsize(output_file)
    file_size_kb = file_size / 1024
    print(f"📦 File size: {file_size_kb:.1f} KB")
    
    if all_items:
        with_content = sum(1 for item in all_items if 'content' in item)
        print(f"\n✅ Success! {len(all_items)} articles scraped")
        print(f"✅ {with_content} articles with full content")
        return 0
    else:
        print("\n❌ ERROR: No items scraped!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
