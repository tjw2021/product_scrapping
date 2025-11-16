#!/usr/bin/env python3
"""
Find the inventory API endpoint
"""

import requests
import json
import os


def find_inventory_api():
    """Try to find inventory API endpoints"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    print("=" * 70)
    print("SEARCHING FOR INVENTORY API ENDPOINTS")
    print("=" * 70)

    # Get a sample item to test with
    print("\nGetting sample items...")
    response = session.get(
        'https://connect.soligent.net/api/items',
        params={'c': '3510556', 'n': '10', 'fieldset': 'search'},
        timeout=15
    )

    if response.status_code != 200:
        print(f"❌ Failed to get items: {response.status_code}")
        return

    data = response.json()
    items = data.get('items', [])

    if not items:
        print("❌ No items returned")
        return

    # Use the first item
    item = items[0]
    item_id = item.get('internalid')
    item_name = item.get('salesdescription', 'N/A')[:60]

    print(f"✅ Testing with item: {item_name}")
    print(f"   Item ID: {item_id}")

    # Try different API endpoints and fieldsets
    api_tests = [
        {
            'name': 'Item Details - details fieldset',
            'url': f'https://connect.soligent.net/api/items/{item_id}',
            'params': {'c': '3510556', 'fieldset': 'details'}
        },
        {
            'name': 'Item Details - full fieldset',
            'url': f'https://connect.soligent.net/api/items/{item_id}',
            'params': {'c': '3510556', 'fieldset': 'full'}
        },
        {
            'name': 'Item Details - all fieldset',
            'url': f'https://connect.soligent.net/api/items/{item_id}',
            'params': {'c': '3510556', 'fieldset': 'all'}
        },
        {
            'name': 'Item Details - inventory fieldset',
            'url': f'https://connect.soligent.net/api/items/{item_id}',
            'params': {'c': '3510556', 'fieldset': 'inventory'}
        },
        {
            'name': 'Item Inventory API',
            'url': f'https://connect.soligent.net/api/items/{item_id}/inventory',
            'params': {'c': '3510556'}
        },
        {
            'name': 'Inventory API',
            'url': f'https://connect.soligent.net/api/inventory/{item_id}',
            'params': {'c': '3510556'}
        },
        {
            'name': 'Services Inventory',
            'url': f'https://connect.soligent.net/services/Inventory.Service.ss',
            'params': {'itemid': item_id, 'c': '3510556'}
        },
    ]

    for test in api_tests:
        print(f"\n{'='*70}")
        print(f"Test: {test['name']}")
        print(f"URL: {test['url']}")
        print('-' * 70)

        try:
            resp = session.get(test['url'], params=test['params'], timeout=15)
            print(f"Status: {resp.status_code}")

            if resp.status_code == 200:
                try:
                    json_data = resp.json()
                    print(f"✅ Valid JSON response")

                    # Look for inventory fields
                    def find_inventory_fields(obj, path=""):
                        """Recursively search for inventory-related fields"""
                        results = []

                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if any(kw in key.lower() for kw in ['inventory', 'quantity', 'stock', 'location', 'warehouse', 'available']):
                                    results.append((f"{path}.{key}" if path else key, value))

                                # Recurse into nested structures
                                if isinstance(value, (dict, list)):
                                    results.extend(find_inventory_fields(value, f"{path}.{key}" if path else key))

                        elif isinstance(obj, list):
                            for idx, item in enumerate(obj):
                                if isinstance(item, (dict, list)):
                                    results.extend(find_inventory_fields(item, f"{path}[{idx}]"))

                        return results

                    inventory_fields = find_inventory_fields(json_data)

                    if inventory_fields:
                        print(f"\n📦 Found {len(inventory_fields)} inventory-related fields:")
                        for field_path, value in inventory_fields[:15]:  # Limit output
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                print(f"\n   {field_path}:")
                                print(f"   {json.dumps(value, indent=6)[:400]}")
                            else:
                                print(f"   {field_path}: {value}")
                    else:
                        print(f"\n   No inventory fields found in response")
                        print(f"   Available fields: {list(json_data.keys())[:20]}")

                except json.JSONDecodeError:
                    print(f"   Response is not JSON")
                    print(f"   Preview: {resp.text[:200]}")

            elif resp.status_code == 404:
                print(f"   Endpoint not found")
            else:
                print(f"   Response: {resp.text[:200]}")

        except Exception as e:
            print(f"   Error: {e}")


    # Try to get more info from the basic search API
    print("\n" + "=" * 70)
    print("EXAMINING SEARCH API RESPONSE")
    print("=" * 70)

    print("\nFields in search API response for first item:")
    for key, value in item.items():
        if any(kw in key.lower() for kw in ['qty', 'quantity', 'stock', 'inventory', 'location', 'warehouse', 'available']):
            if isinstance(value, dict):
                print(f"\n📦 {key}:")
                print(json.dumps(value, indent=4)[:300])
            else:
                print(f"📦 {key}: {value}")


if __name__ == "__main__":
    find_inventory_api()

    print("\n" + "=" * 70)
    print("Search Complete!")
    print("=" * 70)
