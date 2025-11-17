#!/usr/bin/env python3
"""
Find the AJAX endpoint that loads warehouse inventory
"""

import requests
import json
import os
import re


def find_inventory_endpoint():
    """Try to find the inventory AJAX endpoint"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    print("=" * 70)
    print("FINDING INVENTORY AJAX ENDPOINT")
    print("=" * 70)

    # First, get the item ID from the product page
    product_url = "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"

    # Try to get item ID from the API first
    # Search for the product in the API
    api_url = "https://connect.soligent.net/api/items"
    params = {
        'c': '3510556',  # Company ID (from previous tests)
        'fieldset': 'search',
        'q': 'DU323RB',  # Part of the product name
    }

    print(f"\n📡 Searching for product in API...")
    response = session.get(api_url, params=params, timeout=15)

    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])

        if items:
            item = items[0]
            item_id = item.get('internalid')
            item_name = item.get('salesdescription', 'N/A')
            print(f"✅ Found item: {item_name}")
            print(f"   Item ID: {item_id}")

            # Try common NetSuite inventory API patterns
            print("\n" + "=" * 70)
            print("TESTING INVENTORY API ENDPOINTS")
            print("=" * 70)

            test_endpoints = [
                f"/api/items/{item_id}/inventory",
                f"/api/items/{item_id}/quantity",
                f"/api/items/{item_id}/locations",
                f"/api/items/{item_id}?fieldset=details",
                f"/api/items/{item_id}?include=inventory",
                f"/services/Item.Service.ss?id={item_id}&action=get",
                f"/services/Item.Service.ss?id={item_id}&action=getInventory",
                f"/api/StockLocationService/{item_id}",
                f"/api/quantityavailable?item={item_id}",
            ]

            for endpoint in test_endpoints:
                url = f"https://connect.soligent.net{endpoint}"
                try:
                    print(f"\n📡 Testing: {endpoint}")
                    resp = session.get(url, timeout=10)
                    print(f"   Status: {resp.status_code}")

                    if resp.status_code == 200:
                        print(f"   ✅ SUCCESS!")

                        # Try to parse as JSON
                        try:
                            data = resp.json()
                            print(f"   📦 Response (JSON): {json.dumps(data, indent=2)[:500]}")

                            # Check if it contains warehouse names
                            resp_text = json.dumps(data).lower()
                            if 'arlington' in resp_text or 'fontana' in resp_text or 'inventory' in resp_text:
                                print(f"\n   🎯 THIS MIGHT BE IT! Found warehouse/inventory data!")
                                print(f"   Full response:")
                                print(json.dumps(data, indent=2))
                                return

                        except:
                            # Not JSON, maybe HTML
                            if len(resp.text) < 1000:
                                print(f"   Response (text): {resp.text[:500]}")

                    elif resp.status_code != 404:
                        print(f"   Response: {resp.text[:200]}")

                except Exception as e:
                    print(f"   Error: {e}")

            # Also try with company parameter
            print("\n" + "=" * 70)
            print("TESTING WITH COMPANY PARAMETER")
            print("=" * 70)

            test_endpoints_with_c = [
                f"/api/items/{item_id}?c=3510556&fieldset=details",
                f"/api/items/{item_id}?c=3510556&include=inventory",
            ]

            for endpoint in test_endpoints_with_c:
                url = f"https://connect.soligent.net{endpoint}"
                try:
                    print(f"\n📡 Testing: {endpoint}")
                    resp = session.get(url, timeout=10)
                    print(f"   Status: {resp.status_code}")

                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            # Check if it contains warehouse names
                            resp_text = json.dumps(data).lower()
                            if 'arlington' in resp_text or 'fontana' in resp_text:
                                print(f"\n   🎯 FOUND IT! This endpoint returns warehouse data!")
                                print(f"   Full response:")
                                print(json.dumps(data, indent=2)[:2000])
                                return
                        except:
                            pass

                except Exception as e:
                    pass

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("❌ Could not find inventory AJAX endpoint")
    print("\nOptions:")
    print("1. Use Selenium/Playwright to render JavaScript and extract HTML")
    print("2. Reverse engineer the SuiteCommerce frontend code")
    print("3. Contact Soligent for API documentation")


if __name__ == "__main__":
    find_inventory_endpoint()
