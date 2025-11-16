#!/usr/bin/env python3
"""
Test the /api/cacheable/items endpoint found in the HTML
"""

import requests
import json
import os


def test_cacheable_api():
    """Test the cacheable items API endpoint"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    session = requests.Session()
    session.auth = (username, password)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })

    print("=" * 70)
    print("TESTING /api/cacheable/items ENDPOINT")
    print("=" * 70)

    # URL found in the HTML (line 19)
    url = "https://connect.soligent.net/api/cacheable/items"
    params = {
        'c': '3510556',
        'country': 'US',
        'currency': 'USD',
        'fieldset': 'details',
        'include': '',
        'language': 'en',
        'n': '2',
        'pricelevel': '5',
        'url': 'Square-D-DU323RB-3-Pole-AC-100A-Disconnect',
        'use_pcv': 'T'
    }

    print(f"\n📡 Fetching: {url}")
    print(f"   Params: {params}")

    response = session.get(url, params=params, timeout=15)

    print(f"\n✅ Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("\n📦 JSON Response:")
            print(json.dumps(data, indent=2)[:3000])

            # Look for inventory data
            json_str = json.dumps(data).lower()

            if 'arlington' in json_str or 'fontana' in json_str:
                print("\n\n🎯 FOUND WAREHOUSE DATA IN JSON!")
                print("="  * 70)

                # Try to extract inventory details
                if 'items' in data:
                    for item in data['items']:
                        print(f"\nItem: {item.get('displayname', 'N/A')}")

                        # Look for inventory fields
                        for key in item.keys():
                            if 'inventory' in key.lower() or 'location' in key.lower() or 'quantity' in key.lower():
                                print(f"  {key}: {item[key]}")

            else:
                print("\n❌ No warehouse names found in response")

                # Show all keys to help identify the inventory field
                if 'items' in data and data['items']:
                    item = data['items'][0]
                    print("\nAvailable fields:")
                    for key in sorted(item.keys()):
                        print(f"  - {key}")

        except Exception as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Response text: {response.text[:500]}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")


if __name__ == "__main__":
    test_cacheable_api()
