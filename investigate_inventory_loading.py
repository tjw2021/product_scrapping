#!/usr/bin/env python3
"""Investigate how inventory data is loaded on the page"""

import requests
from bs4 import BeautifulSoup
import re
import os

def investigate():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    # Try to login
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')
    
    form_payload = {
        'email': username,
        'password': password,
        'redirect': ''
    }
    
    session.post("https://connect.soligent.net/", data=form_payload, timeout=10)
    
    # Get product page
    url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"
    response = session.get(url, timeout=15)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("="*70)
    print("SEARCHING FOR INVENTORY IN SCRIPTS")
    print("="*70)
    
    # Look in scripts for inventory data
    scripts = soup.find_all('script')
    for script in scripts:
        script_text = str(script.string) if script.string else ''
        
        # Look for inventory-related data
        if 'inventory' in script_text.lower() or 'stock' in script_text.lower() or 'Arlington' in script_text:
            print(f"\n✅ Found inventory-related script!")
            # Find the relevant section
            lines = script_text.split('\n')
            for i, line in enumerate(lines):
                if 'inventory' in line.lower() or 'stock' in line.lower() or 'Arlington' in line:
                    # Print context
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    print('\n'.join(lines[start:end]))
                    print("---")
    
    print("\n" + "="*70)
    print("SEARCHING FOR ALL DIVS WITH 'inventory' or 'stock' IN TEXT")
    print("="*70)
    
    # Search all divs
    for div in soup.find_all(['div', 'p', 'span']):
        text = div.get_text()
        if ('stock' in text.lower() or 'inventory' in text.lower() or 'Arlington' in text.lower()) and len(text) < 500:
            print(f"\n<{div.name}> class={div.get('class')}")
            print(f"Text: {text[:200]}")

if __name__ == "__main__":
    investigate()
