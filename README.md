# Media Press Feed

Automated scraper for Belgian media press releases.

## Sources
- ✅ VTM (DPG Media) - https://communicatie.vtm.be
- 🚧 VRT - Coming soon
- 🚧 Play - Coming soon

## Feed URL
https://[jouw-username].github.io/vtm-press-feed/feed.json

## Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run scraper
python main.py
```

## Adding a new source
1. Create `scrapers/newsource.py`
2. Inherit from `BaseScraper`
3. Implement `get_base_url()` and `scrape_articles()`
4. Import in `scrapers/__init__.py`
5. Add to `main.py`

## Feed Format
```json
[
  {
    "title": "Article title",
    "url": "https://...",
    "source": "vtm",
    "date": "12 feb 2026",
    "description": "Optional preview text",
    "scraped_at": "2026-02-12T15:30:00Z"
  }
]
```# press-scraper
een feed om persberichten tv-zenders op te halen
