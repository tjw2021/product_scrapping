#!/usr/bin/env python3
"""Test warehouse inventory extraction from Soligent"""

import requests
from bs4 import BeautifulSoup

def test_warehouse_inventory():
    """Test fetching warehouse inventory from a sample product page"""
    
    # Use a sample product URL (we'll get one from the API first)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Get a sample product from API
    api_url = "https://connect.soligent.net/api/items"
    params = {
        'c': '3510556',
        'fieldset': 'search',
        'n': '1',
        'page': '1'
    }
    
    print("Fetching sample product from API...")
    response = session.get(api_url, params=params, timeout=15)
    data = response.json()
    
    if data.get('items'):
        item = data['items'][0]
        item_id = item.get('internalid')
        product_url = f"https://connect.soligent.net/item/{item_id}"
        title = item.get('salesdescription', 'N/A')
        
        print(f"\n✅ Sample Product:")
        print(f"  Title: {title}")
        print(f"  URL: {product_url}")
        
        print(f"\nFetching product page HTML...")
        page_response = session.get(product_url, timeout=15)
        soup = BeautifulSoup(page_response.text, 'html.parser')
        
        # Find inventory element
        inventory_element = soup.find('p', class_='inventory-display-quantity-availablev1')
        
        if inventory_element:
            print(f"\n✅ Found inventory element!")
            inventory_text = inventory_element.get_text(separator='\n', strip=True)
            print(f"\nRaw inventory text:")
            print(inventory_text)
            
            # Parse warehouse inventory
            warehouse_inventory = {}
            lines = inventory_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if 'Current Stock:' in line or not line:
                    continue
                
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        location = parts[0].strip()
                        try:
                            quantity = int(parts[1].strip().replace(',', ''))
                            warehouse_inventory[location] = quantity
                        except ValueError:
                            continue
            
            print(f"\n✅ Parsed warehouse inventory:")
            for loc, qty in warehouse_inventory.items():
                print(f"  {loc}: {qty}")
            
            total = sum(warehouse_inventory.values())
            print(f"\n📦 Total inventory: {total}")
            
        else:
            print(f"\n❌ No inventory element found on page")
            print(f"\nSearching for any element with 'inventory' class...")
            inv_elements = soup.find_all(class_=lambda x: x and 'inventory' in x.lower())
            if inv_elements:
                print(f"Found {len(inv_elements)} elements with 'inventory' in class:")
                for elem in inv_elements[:5]:
                    print(f"  - {elem.get('class')}")
    
    else:
        print("❌ No items returned from API")

if __name__ == "__main__":
    test_warehouse_inventory()
