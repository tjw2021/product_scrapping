#!/usr/bin/env python3
"""
Advanced authentication testing - examine JavaScript and find the real login API
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os


def find_login_api():
    """Examine the login page JavaScript to find the actual API endpoint"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })

    print("=" * 70)
    print("EXAMINING LOGIN PAGE JAVASCRIPT")
    print("=" * 70)

    # Get the login page
    response = session.get("https://connect.soligent.net/login", timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all script tags
    scripts = soup.find_all('script', src=True)

    print(f"\nFound {len(scripts)} external scripts")

    # Download and search through JavaScript files
    for script in scripts[:10]:  # Limit to first 10 to avoid too much downloading
        src = script.get('src')
        if not src:
            continue

        # Make absolute URL
        if src.startswith('/'):
            src = f"https://connect.soligent.net{src}"
        elif not src.startswith('http'):
            continue

        try:
            print(f"\nChecking: {src[:80]}...")
            js_response = session.get(src, timeout=10)
            js_content = js_response.text

            # Look for login-related endpoints
            if 'login' in js_content.lower() or 'auth' in js_content.lower():
                # Find API endpoints
                api_patterns = [
                    r'["\'](/services/[A-Za-z]+\.Service\.ss)["\']',
                    r'["\'](/api/[a-z/]+)["\']',
                ]

                found_endpoints = set()
                for pattern in api_patterns:
                    matches = re.findall(pattern, js_content)
                    found_endpoints.update(matches)

                if found_endpoints:
                    print(f"  ✅ Found endpoints: {list(found_endpoints)[:5]}")

        except Exception as e:
            pass


def check_product_page_scripts():
    """Check if inventory is loaded via AJAX on product pages"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    print("\n" + "=" * 70)
    print("CHECKING PRODUCT PAGE FOR INVENTORY API")
    print("=" * 70)

    url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"
    response = session.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get the item ID from the URL or page
    item_id_match = re.search(r'/item/(\d+)', response.text)
    if item_id_match:
        item_id = item_id_match.group(1)
        print(f"\n✅ Found item ID: {item_id}")

        # Try to fetch item details via API
        print(f"\nTrying to fetch item details via API...")
        api_url = f"https://connect.soligent.net/api/items/{item_id}"

        params = {
            'c': '3510556',  # Company ID
            'fieldset': 'details'
        }

        api_response = session.get(api_url, params=params, timeout=15)
        print(f"Status: {api_response.status_code}")

        if api_response.status_code == 200:
            data = api_response.json()
            print(f"\nAPI Response keys: {list(data.keys())[:20]}")

            # Look for inventory-related fields
            inventory_fields = [k for k in data.keys() if 'inv' in k.lower() or 'stock' in k.lower() or 'qty' in k.lower() or 'quantit' in k.lower()]

            if inventory_fields:
                print(f"\n✅ Inventory-related fields in API:")
                for field in inventory_fields:
                    print(f"  - {field}: {data.get(field)}")

            # Check for location-specific inventory
            location_fields = [k for k in data.keys() if 'location' in k.lower() or 'warehouse' in k.lower()]
            if location_fields:
                print(f"\n📍 Location-related fields:")
                for field in location_fields:
                    value = data.get(field)
                    if isinstance(value, dict):
                        print(f"  - {field}: {json.dumps(value, indent=4)[:200]}")
                    else:
                        print(f"  - {field}: {value}")

    # Look for AJAX calls in scripts
    print("\n" + "=" * 70)
    print("SEARCHING FOR INVENTORY AJAX CALLS")
    print("=" * 70)

    scripts = soup.find_all('script')
    for script in scripts:
        if script.string:
            # Look for inventory-related AJAX calls
            if 'inventory' in script.string.lower() or 'quantityavailable' in script.string.lower():
                # Look for URLs
                urls = re.findall(r'["\'](https?://[^"\']+)["\']', script.string)
                api_paths = re.findall(r'["\'](?:/api/[^"\']+|/services/[^"\']+)["\']', script.string)

                if urls or api_paths:
                    print("\n✅ Found inventory-related code with endpoints:")
                    for url in list(set(urls))[:3]:
                        print(f"  - {url}")
                    for path in list(set(api_paths))[:3]:
                        print(f"  - {path}")


def test_authenticated_session():
    """Test if we can authenticate and access inventory"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    print("\n" + "=" * 70)
    print("TESTING AUTHENTICATED SESSION")
    print("=" * 70)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    # Try different NetSuite login endpoints
    login_attempts = [
        {
            'name': 'Services Login',
            'url': 'https://connect.soligent.net/services/Account.Service.ss',
            'method': 'POST',
            'data_type': 'json',
            'payload': {
                'email': username,
                'password': password,
                'redirect': ''
            }
        },
        {
            'name': 'API Items with Basic Auth',
            'url': 'https://connect.soligent.net/api/items',
            'method': 'GET',
            'auth': (username, password),
        }
    ]

    for attempt in login_attempts:
        print(f"\nAttempt: {attempt['name']}")
        print(f"URL: {attempt['url']}")

        try:
            if attempt['method'] == 'POST':
                if attempt.get('data_type') == 'json':
                    response = session.post(attempt['url'], json=attempt['payload'], timeout=15)
                else:
                    response = session.post(attempt['url'], data=attempt['payload'], timeout=15)
            else:
                if 'auth' in attempt:
                    response = session.get(attempt['url'], auth=attempt['auth'], timeout=15)
                else:
                    response = session.get(attempt['url'], timeout=15)

            print(f"Status: {response.status_code}")
            print(f"Cookies: {dict(session.cookies)}")

            if response.status_code == 200:
                print(f"Response preview: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    find_login_api()
    check_product_page_scripts()
    test_authenticated_session()

    print("\n" + "=" * 70)
    print("Investigation Complete!")
    print("=" * 70)
