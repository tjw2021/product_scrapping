#!/usr/bin/env python3
"""Verify the correct domestic content field name"""

import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

api_url = "https://connect.soligent.net/api/items"

# Get products with domestic content using the filter
params = {
    'c': '3510556',
    'fieldset': 'details',
    'n': '1',
    'filter': 'custitem_domestic_content:T'  # This filter works according to my test
}

response = session.get(api_url, params=params, timeout=15)
data = response.json()

if data.get('items'):
    item = data['items'][0]
    
    print("Checking all domestic-related fields in the product:")
    print("="*70)
    
    for key, value in item.items():
        if 'domestic' in key.lower() or 'dom_' in key.lower() or 'content' in key.lower():
            print(f"{key}: {value}")
    
    print("\n" + "="*70)
    print("\nDirect field checks:")
    print(f"custitem_domestic_content: {item.get('custitem_domestic_content', 'NOT FOUND')}")
    print(f"custitem_dom_content: {item.get('custitem_dom_content', 'NOT FOUND')}")

