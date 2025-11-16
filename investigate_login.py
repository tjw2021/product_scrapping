#!/usr/bin/env python3
"""Investigate Soligent login process"""

import requests
from bs4 import BeautifulSoup
import os

def investigate_login():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    base_url = "https://connect.soligent.net"
    
    # 1. Get login page to find form fields
    print("="*70)
    print("STEP 1: Investigating login page")
    print("="*70)
    
    login_url = f"{base_url}/login"
    response = session.get(login_url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all forms
    forms = soup.find_all('form')
    print(f"\nFound {len(forms)} forms on login page")
    
    for idx, form in enumerate(forms, 1):
        print(f"\n--- Form {idx} ---")
        print(f"Action: {form.get('action', 'N/A')}")
        print(f"Method: {form.get('method', 'N/A')}")
        print(f"ID: {form.get('id', 'N/A')}")
        
        # Find all input fields
        inputs = form.find_all('input')
        print(f"Input fields ({len(inputs)}):")
        for inp in inputs:
            name = inp.get('name', 'N/A')
            inp_type = inp.get('type', 'text')
            value = inp.get('value', '')
            print(f"  - {name} (type={inp_type}, value='{value[:30]}')")
    
    # 2. Check if there's a login endpoint in the API
    print("\n" + "="*70)
    print("STEP 2: Looking for login-related endpoints")
    print("="*70)
    
    # Check for common login endpoints
    test_endpoints = [
        "/api/login",
        "/api/auth/login",
        "/services/login.ss",
        "/login.ssp"
    ]
    
    for endpoint in test_endpoints:
        url = f"{base_url}{endpoint}"
        try:
            resp = session.get(url, timeout=5)
            if resp.status_code != 404:
                print(f"✅ {endpoint}: Status {resp.status_code}")
        except:
            pass

if __name__ == "__main__":
    investigate_login()
