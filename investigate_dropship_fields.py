#!/usr/bin/env python3
"""
Investigate Soligent API fields for dropship and delivery date information
"""

import sys
sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper
import json


def investigate_fields():
    """Check what fields are available for dropship and delivery dates"""

    print("=" * 70)
    print("INVESTIGATING DROPSHIP AND DELIVERY DATE FIELDS")
    print("=" * 70)

    scraper = SoligentScraper()

    # Fetch a few products with detailed info
    print("\n📡 Fetching products with detailed fields...")
    data = scraper._fetch_products_page(page=1, page_size=10)

    if data and 'items' in data:
        print(f"✅ Fetched {len(data['items'])} items\n")

        # Look for relevant fields
        relevant_keywords = [
            'dropship', 'drop', 'ship', 'delivery', 'available', 'stock',
            'date', 'eta', 'expected', 'backorder', 'delay', 'lead',
            'time', 'incoming', 'purchase', 'order'
        ]

        # Check first item in detail
        for idx, item in enumerate(data['items'][:3], 1):
            if not isinstance(item, dict):
                continue

            print(f"\n{'='*70}")
            print(f"ITEM {idx}: {item.get('salesdescription', 'N/A')[:60]}")
            print('='*70)

            # Find all relevant fields
            relevant_fields = {}
            for key, value in item.items():
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in relevant_keywords):
                    relevant_fields[key] = value

            if relevant_fields:
                print("\n📦 Relevant fields found:")
                for key, value in sorted(relevant_fields.items()):
                    # Format value nicely
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value, indent=2)[:200]
                    else:
                        value_str = str(value)[:200]
                    print(f"\n  {key}:")
                    print(f"    {value_str}")
            else:
                print("\n⚠️  No relevant fields found in this item")

        # Also check the detailed API endpoint
        print("\n" + "=" * 70)
        print("CHECKING DETAILED API ENDPOINT")
        print("=" * 70)

        first_item = data['items'][0]
        if isinstance(first_item, dict):
            item_id = first_item.get('internalid')
            url_component = first_item.get('urlcomponent', '')

            print(f"\n📡 Fetching detailed data for item {item_id}...")

            # Use cacheable API (same one we use for warehouse inventory)
            if url_component:
                import requests
                params = {
                    'c': scraper.COMPANY_ID,
                    'country': 'US',
                    'currency': 'USD',
                    'fieldset': 'details',
                    'include': '',
                    'language': 'en',
                    'n': '2',
                    'pricelevel': '5',
                    'url': url_component,
                    'use_pcv': 'T'
                }

                response = scraper.session.get(scraper.CACHEABLE_API_URL, params=params, timeout=15)
                if response.status_code == 200:
                    detailed_data = response.json()

                    if 'items' in detailed_data and detailed_data['items']:
                        detailed_item = detailed_data['items'][0]

                        print("\n📦 Additional fields in detailed API:")
                        detailed_relevant = {}
                        for key, value in detailed_item.items():
                            key_lower = key.lower()
                            if any(keyword in key_lower for keyword in relevant_keywords):
                                detailed_relevant[key] = value

                        for key, value in sorted(detailed_relevant.items()):
                            if isinstance(value, (dict, list)):
                                value_str = json.dumps(value, indent=2)[:300]
                            else:
                                value_str = str(value)[:200]
                            print(f"\n  {key}:")
                            print(f"    {value_str}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nLooking for fields like:")
    print("  • Dropship status (isdropshipitem, etc.)")
    print("  • Delivery/availability dates (expecteddate, deliverydate, etc.)")
    print("  • Backorder info (isbackorderable, backorderdate, etc.)")
    print("  • Lead time (leadtime, days, etc.)")


if __name__ == "__main__":
    investigate_fields()
