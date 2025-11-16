#!/usr/bin/env python3
"""Check if products have domestic content field"""

import requests
import json

def check_domestic_fields():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    api_url = "https://connect.soligent.net/api/items"
    
    # Get a few products WITH domestic content
    print("="*70)
    print("PRODUCTS WITH DOMESTIC CONTENT")
    print("="*70)
    
    params = {
        'c': '3510556',
        'fieldset': 'details',  # Get full details
        'n': '3',
        'filter': 'custitem_domestic_content:T'
    }
    
    response = session.get(api_url, params=params, timeout=15)
    data = response.json()
    
    for item in data.get('items', []):
        print(f"\n✅ Product: {item.get('salesdescription', 'N/A')[:60]}")
        
        # Look for domestic content fields
        domestic_fields = {}
        for key, value in item.items():
            if 'domestic' in key.lower() or 'usa' in key.lower() or ('content' in key.lower() and 'cust' in key.lower()):
                domestic_fields[key] = value
        
        if domestic_fields:
            print("  Domestic content fields:")
            for key, value in domestic_fields.items():
                print(f"    {key}: {value}")
        
        # Also check for percentage or compliance fields
        for key in item.keys():
            if 'percent' in key.lower() or 'compliance' in key.lower() or 'ira' in key.lower():
                print(f"    {key}: {item[key]}")
    
    # Get a few products WITHOUT domestic content
    print("\n" + "="*70)
    print("PRODUCTS WITHOUT DOMESTIC CONTENT")
    print("="*70)
    
    params['filter'] = 'custitem_domestic_content:F'
    response = session.get(api_url, params=params, timeout=15)
    data = response.json()
    
    for item in data.get('items', [])[:2]:
        print(f"\n❌ Product: {item.get('salesdescription', 'N/A')[:60]}")
        
        # Check domestic fields
        for key, value in item.items():
            if 'domestic' in key.lower():
                print(f"    {key}: {value}")

if __name__ == "__main__":
    check_domestic_fields()
