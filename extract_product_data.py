#!/usr/bin/env python3
"""Extract warehouse inventory and domestic content from product page"""

import requests
from bs4 import BeautifulSoup
import re

def extract_product_data():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"
    
    print(f"Fetching: {url}")
    response = session.get(url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n" + "="*70)
    print("SEARCHING FOR WAREHOUSE INVENTORY")
    print("="*70)
    
    # Search for elements containing "Stock" or warehouse names
    for elem in soup.find_all(string=re.compile(r'Current Stock|Arlington|Fontana|Sacramento|Orlando|Tampa|Millstone', re.I)):
        parent = elem.parent
        print(f"\nFound in: <{parent.name}> with class={parent.get('class')}")
        print(f"Text: {elem.strip()[:200]}")
        
        # Get surrounding context
        if parent.parent:
            print(f"Parent context: {parent.parent.get_text()[:300]}")
    
    print("\n" + "="*70)
    print("SEARCHING FOR DOMESTIC CONTENT")
    print("="*70)
    
    # Search for domestic content
    for elem in soup.find_all(string=re.compile(r'Domestic Content', re.I)):
        parent = elem.parent
        print(f"\nFound in: <{parent.name}> with class={parent.get('class')}")
        print(f"Text: {elem.strip()}")
        
        # Get next siblings to see the value
        if parent.parent:
            print(f"Parent: {parent.parent.name} class={parent.parent.get('class')}")
            print(f"Parent text: {parent.parent.get_text()[:200]}")
    
    # Also search for all elements with "inventory" in class
    print("\n" + "="*70)
    print("ALL ELEMENTS WITH 'INVENTORY' IN CLASS")
    print("="*70)
    
    inv_elements = soup.find_all(class_=lambda x: x and 'inventory' in str(x).lower())
    print(f"Found {len(inv_elements)} elements")
    for elem in inv_elements[:10]:
        print(f"\n<{elem.name}> class={elem.get('class')}")
        print(f"Text: {elem.get_text()[:150]}")

if __name__ == "__main__":
    extract_product_data()
