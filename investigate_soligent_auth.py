#!/usr/bin/env python3
"""Investigate Soligent authentication and domestic content"""

import requests
from bs4 import BeautifulSoup
import re

def investigate_login_and_domestic():
    """Check login form and domestic content filter"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    base_url = "https://connect.soligent.net"
    
    # 1. Check login page
    print("="*70)
    print("INVESTIGATING LOGIN")
    print("="*70)
    
    login_page_url = f"{base_url}/login"
    print(f"\nFetching login page: {login_page_url}")
    
    try:
        response = session.get(login_page_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find login form
        login_form = soup.find('form', id=re.compile(r'login', re.I)) or soup.find('form', class_=re.compile(r'login', re.I))
        
        if not login_form:
            # Try finding any form
            login_form = soup.find('form')
        
        if login_form:
            print("\n✅ Found login form")
            print(f"Form action: {login_form.get('action')}")
            print(f"Form method: {login_form.get('method')}")
            
            # Find input fields
            inputs = login_form.find_all('input')
            print(f"\nForm fields:")
            for inp in inputs:
                name = inp.get('name', 'N/A')
                inp_type = inp.get('type', 'text')
                placeholder = inp.get('placeholder', '')
                print(f"  - {name} (type={inp_type}, placeholder='{placeholder}')")
        else:
            print("\n❌ No login form found")
            
    except Exception as e:
        print(f"❌ Error fetching login page: {e}")
    
    # 2. Check for domestic content filter in API
    print("\n" + "="*70)
    print("INVESTIGATING DOMESTIC CONTENT")
    print("="*70)
    
    api_url = f"{base_url}/api/items"
    
    # Try searching with domestic content filter
    print(f"\nTesting API with potential domestic content filters...")
    
    test_filters = [
        "custitem_domestic_content:T",
        "domestic_content:true",
        "domestic:true",
        "made_in_usa:true",
        "us_content:true"
    ]
    
    for filter_param in test_filters:
        params = {
            'c': '3510556',
            'fieldset': 'search',
            'n': '5',
            'page': '1',
            'filter': filter_param
        }
        
        try:
            response = session.get(api_url, params=params, timeout=10)
            data = response.json()
            item_count = len(data.get('items', []))
            total = data.get('total', 0)
            
            if total > 0:
                print(f"\n✅ Filter '{filter_param}' returned {total} products!")
                if data.get('items'):
                    sample = data['items'][0]
                    print(f"   Sample product: {sample.get('salesdescription', 'N/A')[:60]}")
                    
                    # Look for domestic content fields
                    for key, value in sample.items():
                        if 'domestic' in key.lower() or 'usa' in key.lower() or 'content' in key.lower():
                            print(f"   Found field: {key} = {value}")
            else:
                print(f"  Filter '{filter_param}': No results")
                
        except Exception as e:
            print(f"  Filter '{filter_param}': Error - {e}")
    
    # 3. Check facets for domestic content
    print(f"\nChecking facets from API...")
    params = {'c': '3510556', 'fieldset': 'search', 'include': 'facets', 'n': '1'}
    
    try:
        response = session.get(api_url, params=params, timeout=15)
        data = response.json()
        
        facets = data.get('facets', [])
        print(f"\nFound {len(facets)} facets:")
        
        for facet in facets:
            facet_id = facet.get('id', 'N/A')
            facet_name = facet.get('name', 'N/A')
            
            if 'domestic' in facet_name.lower() or 'usa' in facet_name.lower() or 'content' in facet_name.lower():
                print(f"\n✅ FOUND DOMESTIC CONTENT FACET!")
                print(f"   ID: {facet_id}")
                print(f"   Name: {facet_name}")
                print(f"   Values: {facet.get('values', [])}")
    
    except Exception as e:
        print(f"Error checking facets: {e}")

if __name__ == "__main__":
    investigate_login_and_domestic()
