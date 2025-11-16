#!/usr/bin/env python3
"""Test Soligent scraper"""

import sys
sys.path.insert(0, '.')

from scrapers.soligent_scraper import SoligentScraper

scraper = SoligentScraper()
products = scraper.scrape_products()

print('\n\nFINAL SUMMARY')
print('='*60)
print(f'Found {len(products)} products')
print('='*60)

if products:
    print('\nFirst 5 products:')
    for p in products[:5]:
        print(f"- {p['title'][:60]}")
        print(f"  Brand: {p['brand']}, Price: ${p['price']}, Stock: {p['stock_status']}")
        print(f"  Wattage: {p['wattage']}, SKU: {p['sku']}")
        print()
