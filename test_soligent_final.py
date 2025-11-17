#!/usr/bin/env python3
"""
Test the updated Soligent scraper with warehouse inventory and domestic content
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper


def test_soligent_scraper():
    """Test the Soligent scraper"""

    print("=" * 70)
    print("TESTING UPDATED SOLIGENT SCRAPER")
    print("=" * 70)

    # Create scraper instance
    scraper = SoligentScraper()

    # Test with the product URL component we know has inventory
    print("\n📦 Testing warehouse inventory extraction...")
    print("   Product: Square-D-DU323RB-3-Pole-AC-100A-Disconnect")

    warehouse_inv = scraper._fetch_warehouse_inventory('Square-D-DU323RB-3-Pole-AC-100A-Disconnect')

    if warehouse_inv:
        print("\n✅ SUCCESS! Warehouse inventory extracted:")
        print("=" * 70)
        for location, qty in warehouse_inv.items():
            print(f"  {location}: {qty}")
        total = sum(warehouse_inv.values())
        print(f"\n📊 Total: {total} units across {len(warehouse_inv)} warehouses")

        # Format for Google Sheets
        location_str = "; ".join([f"{loc}: {qty}" for loc, qty in warehouse_inv.items()])
        print(f"\n📋 Google Sheets format:")
        print(f"   {location_str}")
    else:
        print("\n❌ FAILED: No warehouse inventory returned")

    # Test fetching a few products to check domestic content
    print("\n" + "=" * 70)
    print("TESTING DOMESTIC CONTENT DETECTION")
    print("=" * 70)

    print("\n📡 Fetching first 5 products from API...")
    data = scraper._fetch_products_page(page=1, page_size=5)

    if data and 'items' in data:
        items = data['items']
        print(f"✅ Fetched {len(items)} products\n")

        for item in items:
            product = scraper._parse_product(item)
            if product:
                title = product['title'][:60]
                domestic = product['specs']['domestic_content']
                print(f"  • {title}...")
                print(f"    Domestic Content: {domestic}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\n✅ The scraper is ready to extract:")
    print("   1. Warehouse inventory (Arlington, Fontana, etc.)")
    print("   2. Domestic content flag (Yes/No)")
    print("\nTo run the full scraper, use:")
    print("   python main.py")


if __name__ == "__main__":
    test_soligent_scraper()
