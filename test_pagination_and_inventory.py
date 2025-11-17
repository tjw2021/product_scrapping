#!/usr/bin/env python3
"""
Test Soligent pagination fix and warehouse inventory together
"""

import sys
import os

sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper


def test_pagination_fix():
    """Test that pagination returns different products on each page"""

    print("=" * 70)
    print("TESTING PAGINATION FIX")
    print("=" * 70)

    scraper = SoligentScraper()
    products_seen = {}

    # Test first 3 pages with small page size
    page_size = 10
    for page in [1, 2, 3]:
        print(f"\n📄 Fetching page {page} (offset {(page-1)*page_size})...")

        page_data = scraper._fetch_products_page(page=page, page_size=page_size)

        if page_data and 'items' in page_data:
            items = page_data['items']
            print(f"   Received {len(items)} items")

            # Check first 3 items for uniqueness
            for idx in range(min(3, len(items))):
                item = items[idx]
                if isinstance(item, dict):
                    title = item.get('salesdescription', 'N/A')[:50]
                    item_id = item.get('internalid', 'N/A')

                    # Check for duplicates
                    if item_id in products_seen:
                        print(f"   {idx+1}. ❌ DUPLICATE: {title}")
                    else:
                        products_seen[item_id] = title
                        print(f"   {idx+1}. ✅ NEW: {title}")

    print(f"\n{'='*70}")
    print(f"✅ Total unique products across 3 pages: {len(products_seen)}")
    print(f"   Expected: ~30 (10 per page)")

    if len(products_seen) >= 25:  # Allow some margin
        print("✅ PAGINATION FIX WORKING!")
    else:
        print("❌ PAGINATION STILL BROKEN - Found duplicates")

    return len(products_seen) >= 25


def test_warehouse_inventory():
    """Test warehouse inventory extraction"""

    print("\n" + "=" * 70)
    print("TESTING WAREHOUSE INVENTORY EXTRACTION")
    print("=" * 70)

    scraper = SoligentScraper()

    # Test with known product
    print("\n📦 Testing: Square-D-DU323RB-3-Pole-AC-100A-Disconnect")
    warehouse_inv = scraper._fetch_warehouse_inventory('Square-D-DU323RB-3-Pole-AC-100A-Disconnect')

    if warehouse_inv:
        print("\n✅ SUCCESS! Warehouse inventory:")
        for location, qty in warehouse_inv.items():
            print(f"   {location}: {qty}")
        total = sum(warehouse_inv.values())
        print(f"\n📊 Total: {total} units across {len(warehouse_inv)} warehouses")
        print("✅ WAREHOUSE INVENTORY WORKING!")
        return True
    else:
        print("\n❌ FAILED: No warehouse inventory")
        return False


def test_combined():
    """Test both fixes work together in a real scrape"""

    print("\n" + "=" * 70)
    print("TESTING COMBINED: PAGINATION + WAREHOUSE INVENTORY")
    print("=" * 70)

    scraper = SoligentScraper()

    print("\n📡 Scraping 2 pages of products (20 products)...")

    all_products = []
    for page in [1, 2]:
        page_data = scraper._fetch_products_page(page=page, page_size=10)

        if page_data and 'items' in page_data:
            for item in page_data['items']:
                product = scraper._parse_product(item)
                if product:
                    all_products.append(product)

    print(f"\n✅ Scraped {len(all_products)} products")

    # Check for duplicates
    product_ids = set()
    duplicates = 0
    for product in all_products:
        prod_id = product.get('product_id')
        if prod_id in product_ids:
            duplicates += 1
        else:
            product_ids.add(prod_id)

    print(f"   Unique products: {len(product_ids)}")
    print(f"   Duplicates: {duplicates}")

    if duplicates == 0:
        print("✅ NO DUPLICATES - Pagination working!")
    else:
        print(f"❌ FOUND {duplicates} DUPLICATES - Pagination broken!")

    # Test warehouse inventory on first product
    if all_products:
        first_product = all_products[0]
        url_component = first_product.get('url_component', '')

        if url_component:
            print(f"\n📦 Testing warehouse inventory on first product...")
            print(f"   {first_product['title'][:60]}...")

            warehouse_inv = scraper._fetch_warehouse_inventory(url_component)

            if warehouse_inv:
                print(f"   ✅ Warehouse inventory: {len(warehouse_inv)} locations")
            else:
                print(f"   ℹ️  No warehouse inventory (product may be out of stock or dropship)")

    return duplicates == 0


if __name__ == "__main__":
    print("🔍 COMPREHENSIVE TEST: SOLIGENT SCRAPER FIXES\n")

    test1 = test_pagination_fix()
    test2 = test_warehouse_inventory()
    test3 = test_combined()

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Pagination Fix:          {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Warehouse Inventory:     {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Combined Test:           {'✅ PASS' if test3 else '❌ FAIL'}")

    if test1 and test2 and test3:
        print("\n🎉 ALL TESTS PASSED!")
        print("   The scraper is ready for production.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("   Review the output above for details.")
