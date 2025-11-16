#!/usr/bin/env python3
"""
Test actual Soligent login and warehouse inventory access
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os


def attempt_login(username, password):
    """
    Attempt to login to Soligent using various methods
    """
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://connect.soligent.net',
        'Referer': 'https://connect.soligent.net/login'
    })

    base_url = "https://connect.soligent.net"

    print("=" * 70)
    print("ATTEMPTING LOGIN WITH DIFFERENT METHODS")
    print("=" * 70)

    # Method 1: Try services/Account.Service.ss (NetSuite standard)
    print("\nMethod 1: NetSuite Account Service")
    print("-" * 70)

    try:
        url = f"{base_url}/services/Account.Service.ss"
        payload = {
            "email": username,
            "password": password,
            "redirect": ""
        }

        response = session.post(url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            print("✅ Login successful!")
            return session

    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Try /api/auth
    print("\nMethod 2: API Auth Endpoint")
    print("-" * 70)

    try:
        url = f"{base_url}/api/auth"
        payload = {
            "username": username,
            "password": password
        }

        response = session.post(url, json=payload, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            print("✅ Login successful!")
            return session

    except Exception as e:
        print(f"Error: {e}")

    # Method 3: Form-based POST to main page
    print("\nMethod 3: Form POST to /")
    print("-" * 70)

    try:
        url = base_url
        payload = {
            "email": username,
            "password": password,
            "redirect": ""
        }

        response = session.post(url, data=payload, timeout=15, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Final URL: {response.url}")
        print(f"Cookies: {dict(session.cookies)}")

        if session.cookies:
            print("✅ Got cookies - might be logged in")
            return session

    except Exception as e:
        print(f"Error: {e}")

    # Method 4: Try to find the actual login endpoint by examining the login page
    print("\nMethod 4: Examining login page for API endpoint")
    print("-" * 70)

    try:
        # Get the login page
        login_page = session.get(f"{base_url}/login", timeout=15)
        soup = BeautifulSoup(login_page.text, 'html.parser')

        # Look for script tags that might contain the login API
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'login' in script.string.lower():
                # Look for API endpoints
                api_patterns = [
                    r'"(/services/[^"]+)"',
                    r"'(/services/[^']+)'",
                    r'"(/api/[^"]+)"',
                    r"'(/api/[^']+)'",
                ]

                for pattern in api_patterns:
                    matches = re.findall(pattern, script.string)
                    if matches:
                        print(f"Found potential endpoints: {list(set(matches))[:5]}")

    except Exception as e:
        print(f"Error: {e}")

    return session


def test_warehouse_inventory_access(session, test_urls):
    """
    Test if we can access warehouse inventory with the session
    """
    print("\n" + "=" * 70)
    print("TESTING WAREHOUSE INVENTORY ACCESS")
    print("=" * 70)

    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 70)

        try:
            response = session.get(url, timeout=15)
            print(f"Status: {response.status_code}")
            print(f"Final URL: {response.url}")

            if 'login' in response.url.lower():
                print("❌ Redirected to login - not authenticated")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for inventory element
            inv_elem = soup.find('p', class_='inventory-display-quantity-availablev1')

            if inv_elem:
                print("✅ FOUND INVENTORY ELEMENT!")
                print("Content:")
                print(inv_elem.get_text(strip=False))

                # Parse warehouse inventory
                warehouse_inventory = {}
                inventory_text = inv_elem.get_text(separator='\n', strip=True)
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

                if warehouse_inventory:
                    print("\nParsed warehouse inventory:")
                    for loc, qty in warehouse_inventory.items():
                        print(f"  {loc}: {qty}")
                    print(f"\nTotal: {sum(warehouse_inventory.values())}")
                else:
                    print("\n⚠️  Could not parse warehouse inventory")

            else:
                print("❌ Inventory element not found")

                # Check if there's any inventory-related content
                page_text = soup.get_text()
                if 'Current Stock' in page_text or 'Arlington' in page_text:
                    print("⚠️  Inventory-related text found in page")

                    # Look for script tags that might load inventory via AJAX
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string and ('inventory' in script.string.lower() or 'stock' in script.string.lower()):
                            # Look for API calls
                            api_matches = re.findall(r'["\'](/api/items/[^"\']+)["\']', script.string)
                            if api_matches:
                                print(f"Found item API calls: {list(set(api_matches))[:3]}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Get credentials from environment or use test values
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    if not username or not password:
        print("❌ SOLIGENT_USERNAME and SOLIGENT_PASSWORD not set in environment")
        print("\nPlease set these environment variables and run again:")
        print("  export SOLIGENT_USERNAME='your_username'")
        print("  export SOLIGENT_PASSWORD='your_password'")
        exit(1)

    print(f"Using username: {username[:3]}***{username[-3:]}")

    # Attempt login
    session = attempt_login(username, password)

    # Test warehouse inventory access
    test_urls = [
        "https://connect.soligent.net/Unirac-RoofMount-RM10-EVO-370010-US-Mill-Ballast-Bay",
        "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"
    ]

    test_warehouse_inventory_access(session, test_urls)

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)
