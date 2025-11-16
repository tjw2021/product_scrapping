#!/usr/bin/env python3
"""Investigate Soligent page structure"""

import requests
from bs4 import BeautifulSoup
import re

def investigate_page():
    """Investigate actual page structure for inventory"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Get a sample product
    api_url = "https://connect.soligent.net/api/items"
    params = {'c': '3510556', 'fieldset': 'search', 'n': '5', 'page': '1'}
    
    print("Fetching sample products from API...")
    response = session.get(api_url, params=params, timeout=15)
    data = response.json()
    
    for item in data.get('items', [])[:3]:
        item_id = item.get('internalid')
        product_url = f"https://connect.soligent.net/item/{item_id}"
        title = item.get('salesdescription', 'N/A')[:60]
        
        print(f"\n{'='*70}")
        print(f"Product: {title}")
        print(f"URL: {product_url}")
        
        page_response = session.get(product_url, timeout=15)
        soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Look for any text containing "Current Stock" or warehouse names
        page_text = soup.get_text()
        
        if 'Current Stock' in page_text or 'Arlington' in page_text:
            print("\n✅ Found inventory-related text on page")
            
            # Find the context around "Current Stock"
            if 'Current Stock' in page_text:
                idx = page_text.find('Current Stock')
                context = page_text[max(0, idx-50):idx+300]
                print(f"\nContext around 'Current Stock':")
                print(context)
            
            # Search for all elements containing "Current Stock"
            for elem in soup.find_all(string=re.compile(r'Current Stock|Arlington|Fontana|Sacramento')):
                parent = elem.parent
                print(f"\nFound element: {parent.name} with class={parent.get('class')}")
                print(f"Text: {elem[:100]}")
                
                # Check parent's parent too
                if parent.parent:
                    gp = parent.parent
                    print(f"Grandparent: {gp.name} with class={gp.get('class')}")
        else:
            print("\n❌ No inventory text found on page")
            
            # Check if there's any JavaScript that might be loading it
            scripts = soup.find_all('script')
            for script in scripts:
                script_text = script.string or ''
                if 'inventory' in script_text.lower() or 'stock' in script_text.lower():
                    print(f"\n⚡ Found inventory-related JavaScript")
                    # Show a snippet
                    idx = script_text.lower().find('inventory')
                    if idx < 0:
                        idx = script_text.lower().find('stock')
                    if idx >= 0:
                        print(script_text[max(0,idx-100):idx+200])
                    break

if __name__ == "__main__":
    investigate_page()
