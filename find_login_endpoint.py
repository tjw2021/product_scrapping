#!/usr/bin/env python3
"""Find NetSuite login endpoint"""

import requests
from bs4 import BeautifulSoup
import re
import os

def find_login():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    base_url = "https://connect.soligent.net"
    
    # Get credentials
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')
    
    if not username or not password:
        print("❌ Credentials not found in environment")
        return
    
    print(f"✅ Found credentials for user: {username[:3]}***")
    print()
    
    # Try common NetSuite/SuiteCommerce login endpoints
    login_endpoints = [
        "/api/auth/login",
        "/services/login.ss",
        "/services/Account.Service.ss",
        "/api/account/login",
        "/login.ssp"
    ]
    
    print("Testing login endpoints...")
    print("="*70)
    
    for endpoint in login_endpoints:
        url = f"{base_url}{endpoint}"
        
        # Try POST with credentials
        payload = {
            'email': username,
            'password': password
        }
        
        try:
            resp = session.post(url, json=payload, timeout=10)
            if resp.status_code != 404:
                print(f"\n✅ {endpoint}")
                print(f"   Status: {resp.status_code}")
                print(f"   Response: {resp.text[:200]}")
        except Exception as e:
            pass
    
    # Also try form-based login
    print("\n" + "="*70)
    print("Trying form-based login...")
    
    form_payload = {
        'email': username,
        'password': password,
        'redirect': ''
    }
    
    try:
        resp = session.post(f"{base_url}/", data=form_payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Cookies: {session.cookies.get_dict()}")
        
        # Try accessing a product page
        product_url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"
        prod_resp = session.get(product_url, timeout=10)
        
        soup = BeautifulSoup(prod_resp.text, 'html.parser')
        inv_elem = soup.find('p', class_='inventory-display-quantity-availablev1')
        
        if inv_elem:
            print("✅ FOUND INVENTORY ELEMENT AFTER LOGIN!")
            print(f"Content: {inv_elem.get_text()}")
        else:
            print("❌ Inventory element still not found")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_login()
