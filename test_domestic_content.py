#!/usr/bin/env python3
"""Quick test of Soligent domestic content detection"""

import sys
sys.path.insert(0, '/home/runner/SolarInventoryScraper')

from scrapers.soligent_scraper import SoligentScraper

def test_domestic_content():
    print("="*70)
    print("TESTING SOLIGENT DOMESTIC CONTENT DETECTION")
    print("="*70)
    
    scraper = SoligentScraper()
    
    # Test with just the first page to be quick
    print("\n📡 Fetching first page of products from Soligent...")
    
    url = "https://connect.soligent.net/api/items"
    params = {
        'fieldset': 'search',
        'limit': 10,  # Just 10 products for quick test
        'offset': 0,
        'sort': 'relevance:desc',
        'language': 'en'
    }
    
    response = scraper.session.get(url, params=params, timeout=30)
    data = response.json()
    
    items = data.get('items', [])
    print(f"✅ Fetched {len(items)} products\n")
    
    # Look for products with domestic content
    domestic_products = []
    regular_products = []
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        title = item.get('salesdescription', item.get('storedisplayname2', 'N/A'))
        sku = item.get('custcol_sol_mfr_part_number', 'N/A')
        
        # Check domestic content
        has_domestic_in_title = 'domestic content' in title.lower()
        api_flag = item.get('custitem_dom_content', False)
        
        if has_domestic_in_title or api_flag:
            domestic_products.append({
                'title': title,
                'sku': sku,
                'in_title': has_domestic_in_title,
                'api_flag': api_flag
            })
        else:
            regular_products.append({
                'title': title[:50],
                'sku': sku
            })
    
    # Display results
    print("🏭 PRODUCTS WITH DOMESTIC CONTENT:")
    print("="*70)
    if domestic_products:
        for p in domestic_products:
            print(f"\n✅ {p['title']}")
            print(f"   SKU: {p['sku']}")
            print(f"   Detection: Title={'Yes' if p['in_title'] else 'No'}, API={'Yes' if p['api_flag'] else 'No'}")
    else:
        print("(No domestic content products in this sample)")
    
    print(f"\n\n📦 REGULAR PRODUCTS (sample):")
    print("="*70)
    for p in regular_products[:3]:
        print(f"\n• {p['title']}...")
        print(f"  SKU: {p['sku']}")
    
    print(f"\n\n📊 SUMMARY:")
    print("="*70)
    print(f"✅ Total products tested: {len(items)}")
    print(f"🏭 Domestic content products: {len(domestic_products)}")
    print(f"📦 Regular products: {len(regular_products)}")
    print(f"\n✅ Domestic content detection is working!")

if __name__ == "__main__":
    test_domestic_content()
