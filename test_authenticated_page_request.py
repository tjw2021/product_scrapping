#!/usr/bin/env python3
"""
Test if authenticated request returns the warehouse inventory HTML
"""

import requests
from bs4 import BeautifulSoup
import os
import time


def test_authenticated_request():
    """Test getting warehouse inventory with authenticated request"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    print("=" * 70)
    print("TESTING AUTHENTICATED PAGE REQUEST")
    print("=" * 70)

    # Create session with authentication
    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    # Product that user confirmed HAS inventory
    test_url = "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"

    print(f"\n📡 Fetching: {test_url}")
    print("🔐 Using Basic Auth with credentials...")

    response = session.get(test_url, timeout=15)

    print(f"✅ Status Code: {response.status_code}")
    print(f"📝 Content Length: {len(response.text)} bytes")

    # Check cookies
    cookies = session.cookies.get_dict()
    print(f"🍪 Cookies received: {list(cookies.keys())}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for inventory display
    print("\n" + "=" * 70)
    print("SEARCHING FOR INVENTORY IN RESPONSE")
    print("=" * 70)

    inventory_display = soup.find('div', class_='inventory-display')

    if inventory_display:
        print("\n✅ FOUND INVENTORY DISPLAY DIV!")
        print("=" * 70)

        # Parse warehouse inventory
        warehouse_list = inventory_display.find('ul')
        if warehouse_list:
            print("\n📦 WAREHOUSE INVENTORY:")
            warehouse_inventory = {}

            for li in warehouse_list.find_all('li'):
                text = li.get_text().strip()
                if ':' in text:
                    parts = text.split(':', 1)
                    if len(parts) == 2:
                        location = parts[0].strip()
                        try:
                            quantity = int(parts[1].strip().replace(',', ''))
                            warehouse_inventory[location] = quantity
                            print(f"  {location}: {quantity}")
                        except ValueError:
                            continue

            print(f"\n📊 Total: {sum(warehouse_inventory.values())} units across {len(warehouse_inventory)} warehouses")
            print(f"\n✅ SUCCESS! Warehouse inventory extracted from authenticated request")
        else:
            print("❌ No <ul> found inside inventory-display")
            print(f"HTML: {inventory_display.prettify()}")
    else:
        print("\n❌ NO INVENTORY DISPLAY FOUND")

        # Check if there's any inventory-related content
        print("\nSearching for inventory-related elements...")
        inv_elements = soup.find_all(class_=lambda x: x and 'inventory' in str(x).lower())

        if inv_elements:
            print(f"\nFound {len(inv_elements)} elements with 'inventory' in class:")
            for elem in inv_elements[:10]:
                print(f"\n  <{elem.name}> class={elem.get('class')}")
                text = elem.get_text()[:200]
                print(f"  Text: {text}")
        else:
            print("No elements with 'inventory' in class name")

        # Check if page text contains warehouse names
        page_text = soup.get_text()
        if 'Arlington' in page_text or 'Fontana' in page_text or 'Current Stock' in page_text:
            print("\n⚠️ Found warehouse names or 'Current Stock' in page text!")
            print("This suggests the data exists but may not be in HTML yet")
            print("(Likely loaded via JavaScript/AJAX)")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if inventory_display:
        print("✅ Warehouse inventory can be extracted with authenticated requests!")
        print("   Next: Integrate this into the scraper")
    else:
        print("❌ Warehouse inventory NOT in initial HTML response")
        print("   Options:")
        print("   1. Find the AJAX endpoint that loads the data")
        print("   2. Use Selenium/Playwright to render JavaScript")
        print("   3. Check if data is in page JavaScript variables")

        # Check for data in JavaScript
        print("\n" + "=" * 70)
        print("CHECKING FOR DATA IN PAGE JAVASCRIPT")
        print("=" * 70)

        scripts = soup.find_all('script')
        for script in scripts:
            script_text = str(script.string) if script.string else ''
            if 'Arlington' in script_text or 'inventory' in script_text.lower() or 'quantityavailable' in script_text.lower():
                print("\n✅ Found inventory-related data in JavaScript!")
                # Find the relevant section
                for line in script_text.split('\n'):
                    if 'inventory' in line.lower() or 'Arlington' in line or 'quantityavailable' in line.lower():
                        print(f"  {line.strip()[:200]}")
                break


if __name__ == "__main__":
    test_authenticated_request()
