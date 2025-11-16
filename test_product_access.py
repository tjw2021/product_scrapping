#!/usr/bin/env python3
"""Test accessing product page with and without auth"""

import requests
from bs4 import BeautifulSoup
import os
import re

def test_product_access():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Test product URLs provided by user
    test_urls = [
        "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay",
        "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"
    ]
    
    print("="*70)
    print("Testing product page access WITHOUT authentication")
    print("="*70)
    
    for url in test_urls:
        print(f"\nURL: {url}")
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for login redirect or requirement
        if 'login' in response.url.lower():
            print("  ⚠️  Redirected to login page")
        else:
            print("  ✅ Page accessible")
            
            # Look for inventory display
            inv_elem = soup.find('p', class_='inventory-display-quantity-availablev1')
            if inv_elem:
                print(f"  📦 Found inventory element!")
                print(f"     Content: {inv_elem.get_text()[:100]}")
            else:
                print(f"  ❌ No inventory element found")
                
                # Search for any text containing warehouse names
                page_text = soup.get_text()
                if 'Arlington' in page_text or 'Fontana' in page_text:
                    print(f"  ⚠️  Warehouse names found in page text (may need auth to see details)")
                
            # Look for domestic content indicators
            if 'Domestic Content' in soup.get_text():
                print(f"  ✅ Found 'Domestic Content' text in page")
            
        print()

if __name__ == "__main__":
    test_product_access()
