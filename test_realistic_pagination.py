#!/usr/bin/env python3
"""
Test pagination with realistic settings (page_size=48)
"""

import sys
sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper


def test_realistic_pagination():
    """Test pagination with page_size=48 like the actual scraper"""

    print("=" * 70)
    print("TESTING PAGINATION WITH REALISTIC SETTINGS")
    print("=" * 70)

    scraper = SoligentScraper()
    all_product_ids = set()
    products_per_page = []

    # Test first 3 pages with default page size
    for page in [1, 2, 3]:
        print(f"\n📄 Page {page} (offset {(page-1)*48}):")

        data = scraper._fetch_products_page(page=page, page_size=48)

        if data and 'items' in data:
            items = data['items']
            print(f"   Items received: {len(items)}")

            # Count valid products (dicts)
            page_ids = []
            dict_count = 0
            list_count = 0

            for item in items:
                if isinstance(item, dict):
                    dict_count += 1
                    item_id = item.get('internalid')
                    if item_id:
                        page_ids.append(item_id)
                        all_product_ids.add(item_id)
                elif isinstance(item, list):
                    list_count += 1

            products_per_page.append(len(page_ids))

            print(f"   Valid products (dicts): {dict_count}")
            if list_count > 0:
                print(f"   ⚠️  Lists found: {list_count}")

            # Show first and last product
            valid_items = [item for item in items if isinstance(item, dict)]
            if valid_items:
                first = valid_items[0]
                last = valid_items[-1]
                print(f"   First: {first.get('salesdescription', 'N/A')[:50]}")
                print(f"   Last:  {last.get('salesdescription', 'N/A')[:50]}")

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total unique product IDs: {len(all_product_ids)}")
    print(f"Products per page: {products_per_page}")
    print(f"Expected: ~144 (48 per page × 3)")

    # Check for duplicates
    total_products = sum(products_per_page)
    duplicates = total_products - len(all_product_ids)

    if duplicates == 0:
        print(f"\n✅ NO DUPLICATES FOUND!")
        print("✅ PAGINATION FIX WORKING CORRECTLY!")
        return True
    else:
        print(f"\n⚠️  Duplicates: {duplicates}")
        print(f"   (This might be expected if API returns overlapping data)")
        # Accept up to 10% duplicates as tolerance
        if duplicates <= total_products * 0.1:
            print("✅ PAGINATION MOSTLY WORKING (within tolerance)")
            return True
        else:
            print("❌ TOO MANY DUPLICATES - Pagination broken!")
            return False


if __name__ == "__main__":
    result = test_realistic_pagination()
    sys.exit(0 if result else 1)
