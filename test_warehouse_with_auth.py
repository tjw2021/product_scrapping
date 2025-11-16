#!/usr/bin/env python3
"""
Test warehouse inventory access with authenticated session
"""

import requests
from bs4 import BeautifulSoup
import os
import json


def test_authenticated_warehouse_access():
    """Test if authenticated session can access warehouse inventory"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    print("=" * 70)
    print("TESTING AUTHENTICATED WAREHOUSE INVENTORY ACCESS")
    print("=" * 70)

    # Create session with authentication
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    # Set up Basic Auth
    session.auth = (username, password)

    print("\n1. Authenticating via API call...")
    api_response = session.get(
        'https://connect.soligent.net/api/items',
        params={'c': '3510556', 'n': '1'},
        timeout=15
    )

    print(f"   Status: {api_response.status_code}")
    print(f"   Cookies: {dict(session.cookies)}")

    if api_response.status_code != 200:
        print("   ❌ Authentication failed")
        return

    print("   ✅ Authentication successful!")

    # Test product pages
    test_urls = [
        "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay",
        "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"
    ]

    for url in test_urls:
        print(f"\n{'='*70}")
        print(f"Testing: {url}")
        print('='*70)

        # Access product page with authenticated session
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for inventory element
        inv_elem = soup.find('p', class_='inventory-display-quantity-availablev1')

        if inv_elem:
            print("\n✅ FOUND WAREHOUSE INVENTORY ELEMENT!")
            print("\nRaw content:")
            print(inv_elem.get_text())

            # Parse warehouse inventory
            warehouse_inventory = {}
            inventory_text = inv_elem.get_text(separator='\n', strip=True)
            lines = inventory_text.split('\n')

            for line in lines:
                line = line.strip()
                if 'Current Stock:' in line or not line:
                    continue

                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        location = parts[0].strip()
                        try:
                            quantity = int(parts[1].strip().replace(',', ''))
                            warehouse_inventory[location] = quantity
                        except ValueError:
                            continue

            if warehouse_inventory:
                print("\n📦 Parsed warehouse inventory:")
                for loc, qty in warehouse_inventory.items():
                    print(f"   {loc}: {qty}")
                print(f"\n   Total: {sum(warehouse_inventory.values())}")
            else:
                print("\n⚠️  Could not parse warehouse data")

        else:
            print("\n❌ Inventory element not found")

            # Check all elements with 'inventory' in class
            inv_elements = soup.find_all(class_=lambda x: x and 'inventory' in str(x).lower())
            if inv_elements:
                print(f"\nFound {len(inv_elements)} elements with 'inventory' in class:")
                for elem in inv_elements[:5]:
                    print(f"   <{elem.name}> class={elem.get('class')}")
                    text = elem.get_text(strip=True)[:100]
                    if text:
                        print(f"   Text: {text}")

            # Check page text
            page_text = soup.get_text()
            if 'Current Stock' in page_text or 'Arlington' in page_text:
                print("\n⚠️  Found inventory-related text in page")
                idx = page_text.find('Current Stock')
                if idx >= 0:
                    print(f"   Context: {page_text[max(0,idx-50):idx+200]}")


def test_item_api_for_inventory():
    """Check if item detail API returns warehouse inventory"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    print("\n" + "=" * 70)
    print("CHECKING ITEM API FOR WAREHOUSE INVENTORY")
    print("=" * 70)

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    # Get a sample item
    print("\nFetching sample items...")
    response = session.get(
        'https://connect.soligent.net/api/items',
        params={'c': '3510556', 'n': '5', 'fieldset': 'search'},
        timeout=15
    )

    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])

        if items:
            # Get detailed info for first item
            item = items[0]
            item_id = item.get('internalid')

            print(f"\nFetching details for item {item_id}...")
            detail_response = session.get(
                f'https://connect.soligent.net/api/items/{item_id}',
                params={'c': '3510556', 'fieldset': 'details'},
                timeout=15
            )

            if detail_response.status_code == 200:
                detail_data = detail_response.json()

                print(f"\n✅ Got item details")
                print(f"Total fields: {len(detail_data.keys())}")

                # Look for inventory/location fields
                inventory_keywords = ['inventory', 'stock', 'qty', 'quantity', 'location', 'warehouse', 'available']

                matching_fields = {}
                for key, value in detail_data.items():
                    for keyword in inventory_keywords:
                        if keyword in key.lower():
                            matching_fields[key] = value
                            break

                if matching_fields:
                    print(f"\n📦 Inventory-related fields:")
                    for key, value in matching_fields.items():
                        if isinstance(value, (dict, list)):
                            print(f"   {key}: {json.dumps(value, indent=6)[:300]}")
                        else:
                            print(f"   {key}: {value}")
                else:
                    print("\n⚠️  No obvious inventory fields found")
                    print("\nAll available fields:")
                    for key in sorted(detail_data.keys())[:30]:
                        print(f"   - {key}")


if __name__ == "__main__":
    test_authenticated_warehouse_access()
    test_item_api_for_inventory()

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)
