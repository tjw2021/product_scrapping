#!/usr/bin/env python3
"""
Deep dive into product page to find where inventory data is stored
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os


def deep_dive_product_page():
    """Search product page thoroughly for inventory data"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    # Authenticate
    session.get('https://connect.soligent.net/api/items', params={'c': '3510556', 'n': '1'}, timeout=15)

    print("=" * 70)
    print("DEEP DIVE INTO PRODUCT PAGE")
    print("=" * 70)

    url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"
    print(f"\nURL: {url}")

    response = session.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Method 1: Search for warehouse names in entire page text
    print("\n" + "=" * 70)
    print("METHOD 1: Searching for warehouse names")
    print("=" * 70)

    warehouse_names = ['Arlington', 'Fontana', 'Millstone', 'Orlando', 'Sacramento', 'Tampa']
    page_text = soup.get_text()

    for warehouse in warehouse_names:
        if warehouse in page_text:
            print(f"\n✅ Found '{warehouse}' in page!")
            # Find context
            idx = page_text.find(warehouse)
            context = page_text[max(0, idx-100):idx+150]
            print(f"Context: {context}")
            break

    # Method 2: Search all script tags for inventory data
    print("\n" + "=" * 70)
    print("METHOD 2: Searching scripts for inventory/quantity data")
    print("=" * 70)

    scripts = soup.find_all('script')
    for idx, script in enumerate(scripts):
        if not script.string:
            continue

        script_text = script.string

        # Look for inventory-related patterns
        if any(keyword in script_text for keyword in ['quantityavailable', 'inventory', 'stock', 'Arlington', 'Fontana']):
            print(f"\n✅ Script #{idx} contains inventory keywords")

            # Try to find JSON data
            # Look for common patterns of JSON objects
            json_patterns = [
                r'\{[^{}]*(?:"quantityavailable"|"inventory"|"stock")[^{}]*\}',
                r'\{[^{}]*(?:Arlington|Fontana|Sacramento)[^{}]*\}',
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, script_text, re.IGNORECASE)
                for match in matches[:3]:
                    print(f"\nPotential JSON data:")
                    print(match[:300])

            # Also look for simple key-value pairs
            if 'quantityavailable' in script_text.lower():
                lines = script_text.split('\n')
                for i, line in enumerate(lines):
                    if 'quantityavailable' in line.lower():
                        # Print context
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print(f"\nFound 'quantityavailable' at line {i}:")
                        print('\n'.join(lines[start:end]))
                        break

    # Method 3: Look for data attributes
    print("\n" + "=" * 70)
    print("METHOD 3: Searching for data attributes with inventory")
    print("=" * 70)

    for elem in soup.find_all(attrs=lambda x: x and any('data-' in str(k) for k in x)):
        for attr, value in elem.attrs.items():
            if attr.startswith('data-') and value:
                value_str = str(value)
                if any(keyword in value_str.lower() for keyword in ['inventory', 'quantity', 'stock', 'available']):
                    print(f"\n✅ Found data attribute: {attr}")
                    print(f"   Element: <{elem.name}>")
                    print(f"   Value: {value_str[:200]}")

    # Method 4: Check if there's an item ID we can use with the API
    print("\n" + "=" * 70)
    print("METHOD 4: Extracting item ID and checking API")
    print("=" * 70)

    # Try to find item ID
    item_id_patterns = [
        r'"internalid"\s*:\s*"?(\d+)"?',
        r'"itemid"\s*:\s*"?(\d+)"?',
        r'/item/(\d+)',
        r'data-item-id="(\d+)"',
    ]

    item_id = None
    for pattern in item_id_patterns:
        match = re.search(pattern, response.text)
        if match:
            item_id = match.group(1)
            print(f"✅ Found item ID: {item_id}")
            break

    if item_id:
        # Try to get item details via API
        print(f"\nFetching item details from API...")
        api_url = f"https://connect.soligent.net/api/items/{item_id}"
        api_response = session.get(api_url, params={'c': '3510556', 'fieldset': 'details'}, timeout=15)

        if api_response.status_code == 200:
            data = api_response.json()
            print(f"✅ API response received")

            # Look for all fields
            print(f"\nAll available fields ({len(data.keys())} total):")
            for key in sorted(data.keys()):
                value = data[key]
                # Print fields that might contain inventory
                if any(kw in key.lower() for kw in ['qty', 'quantity', 'stock', 'inventory', 'location', 'warehouse', 'available']):
                    if isinstance(value, dict):
                        print(f"\n📦 {key}:")
                        print(json.dumps(value, indent=4)[:500])
                    elif isinstance(value, list):
                        print(f"\n📦 {key}: [{len(value)} items]")
                        if value:
                            print(json.dumps(value[0], indent=4)[:300])
                    else:
                        print(f"📦 {key}: {value}")

    # Method 5: Check for React/Vue data
    print("\n" + "=" * 70)
    print("METHOD 5: Checking for React/Vue component data")
    print("=" * 70)

    # Look for __INITIAL_STATE__ or similar
    state_patterns = [
        r'__INITIAL_STATE__\s*=\s*(\{.+?\});',
        r'window\.initialState\s*=\s*(\{.+?\});',
        r'ENVIRONMENT\s*=\s*(\{.+?\});',
    ]

    for pattern in state_patterns:
        match = re.search(pattern, response.text, re.DOTALL)
        if match:
            print(f"\n✅ Found application state!")
            state_str = match.group(1)
            print(f"State data length: {len(state_str)} characters")

            # Try to parse if it's valid JSON
            try:
                state_data = json.loads(state_str)
                # Look for inventory in state
                def search_dict(d, path=""):
                    for k, v in d.items():
                        if any(kw in k.lower() for kw in ['inventory', 'quantity', 'stock']):
                            print(f"\nFound in state: {path}.{k}")
                            print(f"Value: {json.dumps(v, indent=4)[:300]}")
                        if isinstance(v, dict):
                            search_dict(v, f"{path}.{k}")

                search_dict(state_data)
            except:
                # Just show a snippet
                print(f"Preview: {state_str[:500]}")


if __name__ == "__main__":
    deep_dive_product_page()

    print("\n" + "=" * 70)
    print("Deep Dive Complete!")
    print("=" * 70)
