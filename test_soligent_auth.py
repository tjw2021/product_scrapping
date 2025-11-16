#!/usr/bin/env python3
"""
Test Soligent authentication mechanism
This script investigates how to properly authenticate to Soligent's NetSuite platform
"""

import requests
from bs4 import BeautifulSoup
import re
import json


def test_login_page():
    """Investigate the login page structure"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    })

    base_url = "https://connect.soligent.net"

    print("=" * 70)
    print("STEP 1: Investigating Login Page")
    print("=" * 70)

    # Get the main page to see if there's a login link
    print("\nFetching main page...")
    response = session.get(base_url, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for login links
    login_links = []
    for link in soup.find_all('a', href=True):
        if 'login' in link.get('href', '').lower() or 'signin' in link.get('href', '').lower():
            login_links.append({
                'text': link.get_text(strip=True),
                'href': link['href']
            })

    print(f"\nFound {len(login_links)} login-related links:")
    for link in login_links[:5]:
        print(f"  - {link['text']}: {link['href']}")

    # Try common login URLs
    print("\n" + "=" * 70)
    print("STEP 2: Testing Common Login URLs")
    print("=" * 70)

    login_urls = [
        f"{base_url}/login",
        f"{base_url}/login.ssp",
        f"{base_url}/signin",
        f"{base_url}/account/login"
    ]

    for url in login_urls:
        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
            print(f"\n{url}")
            print(f"  Status: {resp.status_code}")
            print(f"  Final URL: {resp.url}")

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')

                # Look for forms
                forms = soup.find_all('form')
                if forms:
                    print(f"  Forms found: {len(forms)}")
                    for idx, form in enumerate(forms, 1):
                        action = form.get('action', 'N/A')
                        method = form.get('method', 'GET')
                        print(f"    Form {idx}: action='{action}', method={method}")

                        # Find input fields
                        inputs = form.find_all('input')
                        if inputs:
                            print(f"      Input fields:")
                            for inp in inputs:
                                name = inp.get('name', 'N/A')
                                inp_type = inp.get('type', 'text')
                                print(f"        - {name} ({inp_type})")

                # Look for login-related text
                page_text = soup.get_text()
                if 'email' in page_text.lower() and 'password' in page_text.lower():
                    print(f"  ✅ Page contains login-related content")

        except Exception as e:
            print(f"\n{url}")
            print(f"  Error: {e}")

    # Check for API endpoints in JavaScript
    print("\n" + "=" * 70)
    print("STEP 3: Searching for Login API in JavaScript")
    print("=" * 70)

    response = session.get(f"{base_url}/login", timeout=15, allow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script', src=True)
    print(f"\nFound {len(scripts)} external scripts")

    # Look for inline scripts with login/auth keywords
    inline_scripts = soup.find_all('script', src=False)
    print(f"Found {len(inline_scripts)} inline scripts")

    for script in inline_scripts:
        if script.string:
            # Look for authentication-related patterns
            if any(keyword in script.string.lower() for keyword in ['login', 'auth', 'session', 'credentials']):
                # Look for API endpoints
                api_matches = re.findall(r'["\'](/api/[^"\']+)["\']', script.string)
                service_matches = re.findall(r'["\'](/services/[^"\']+)["\']', script.string)

                if api_matches or service_matches:
                    print("\nFound authentication-related endpoints:")
                    for match in set(api_matches + service_matches):
                        print(f"  - {match}")


def test_product_page_authentication():
    """Test if we can access warehouse inventory without login"""
    print("\n" + "=" * 70)
    print("STEP 4: Testing Product Page Access (No Auth)")
    print("=" * 70)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })

    # Test with the URL the user provided
    test_url = "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay"

    print(f"\nFetching: {test_url}")
    response = session.get(test_url, timeout=15)

    print(f"Status: {response.status_code}")
    print(f"Final URL: {response.url}")

    # Check if redirected to login
    if 'login' in response.url.lower():
        print("❌ Redirected to login page - authentication required")
        return False

    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for the inventory element
    inv_elem = soup.find('p', class_='inventory-display-quantity-availablev1')

    if inv_elem:
        print("✅ Found inventory element!")
        print(f"Content: {inv_elem.get_text()[:200]}")
        return True
    else:
        print("❌ Inventory element not found")

        # Look for any element that might contain inventory
        page_text = soup.get_text()
        if 'Current Stock' in page_text:
            print("⚠️  'Current Stock' text found in page - might be loaded via JavaScript")
            # Find context
            idx = page_text.find('Current Stock')
            print(f"Context: {page_text[max(0, idx-50):idx+150]}")

        # Check if there are any inventory-related classes
        inv_classes = soup.find_all(class_=lambda x: x and 'inventory' in str(x).lower())
        if inv_classes:
            print(f"\nFound {len(inv_classes)} elements with 'inventory' in class name:")
            for elem in inv_classes[:5]:
                print(f"  <{elem.name}> class={elem.get('class')}")
                print(f"    Text: {elem.get_text()[:100]}")

        return False


if __name__ == "__main__":
    print("🔍 Soligent Authentication Investigation")
    print("=" * 70)

    test_login_page()
    test_product_page_authentication()

    print("\n" + "=" * 70)
    print("Investigation Complete!")
    print("=" * 70)
