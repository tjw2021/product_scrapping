#!/usr/bin/env python3
"""
Debug the API response to see what structure we're getting
"""

import sys
sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper
import json


def debug_api_response():
    """Check the actual API response structure"""

    scraper = SoligentScraper()

    print("=" * 70)
    print("DEBUGGING API RESPONSE STRUCTURE")
    print("=" * 70)

    # Fetch first page
    print("\n📡 Fetching page 1...")
    data = scraper._fetch_products_page(page=1, page_size=5)

    print(f"\nTotal products in response: {data.get('total', 'N/A')}")
    print(f"Items in response: {len(data.get('items', []))}")

    if 'items' in data:
        items = data['items']
        print(f"\nFirst 5 items:")

        for idx, item in enumerate(items[:5], 1):
            print(f"\n  Item {idx}:")
            print(f"    Type: {type(item)}")

            if isinstance(item, dict):
                title = item.get('salesdescription', 'N/A')[:50]
                item_id = item.get('internalid', 'N/A')
                print(f"    ID: {item_id}")
                print(f"    Title: {title}")
            elif isinstance(item, list):
                print(f"    ❌ THIS IS A LIST!")
                print(f"    Length: {len(item)}")
                if item:
                    print(f"    First element type: {type(item[0])}")
                    if isinstance(item[0], dict):
                        print(f"    First element keys: {list(item[0].keys())[:5]}")
            else:
                print(f"    ❌ UNEXPECTED TYPE: {type(item)}")

    # Test offset 5
    print("\n" + "=" * 70)
    print("TESTING OFFSET PAGINATION")
    print("=" * 70)

    print("\n📡 Fetching with offset 0...")
    data1 = scraper._fetch_products_page(page=1, page_size=5)

    print("\n📡 Fetching with offset 5...")
    data2 = scraper._fetch_products_page(page=2, page_size=5)

    if data1.get('items') and data2.get('items'):
        item1 = data1['items'][0]
        item2 = data2['items'][0]

        print(f"\nPage 1 first item type: {type(item1)}")
        print(f"Page 2 first item type: {type(item2)}")

        if isinstance(item1, dict) and isinstance(item2, dict):
            id1 = item1.get('internalid')
            id2 = item2.get('internalid')
            title1 = item1.get('salesdescription', 'N/A')[:50]
            title2 = item2.get('salesdescription', 'N/A')[:50]

            print(f"\nPage 1: ID={id1}, Title={title1}")
            print(f"Page 2: ID={id2}, Title={title2}")

            if id1 == id2:
                print("\n❌ SAME ITEM - Offset not working!")
            else:
                print("\n✅ DIFFERENT ITEMS - Offset working!")


if __name__ == "__main__":
    debug_api_response()
