#!/usr/bin/env python3
"""Find products WITH domestic content = True"""

import requests

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

api_url = "https://connect.soligent.net/api/items"

# Get products where domestic content is explicitly True
params = {
    'c': '3510556',
    'fieldset': 'search',
    'n': '10',
    'page': '1'
}

print("Fetching 10 products to find ones with domestic content...")
response = session.get(api_url, params=params, timeout=15)
data = response.json()

yes_count = 0
no_count = 0

for item in data.get('items', []):
    dom_content = item.get('custitem_dom_content', False)
    title = item.get('salesdescription', 'N/A')[:50]
    
    if dom_content == True:
        print(f"✅ YES: {title}")
        yes_count += 1
    else:
        print(f"❌ NO: {title}")
        no_count += 1

print(f"\n{'='*70}")
print(f"Summary: {yes_count} with domestic content, {no_count} without")
print(f"Field name: custitem_dom_content")

