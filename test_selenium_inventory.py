#!/usr/bin/env python3
"""
Test warehouse inventory extraction using Selenium to render JavaScript
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def test_selenium_inventory():
    """Test extracting warehouse inventory with Selenium"""
    username = os.environ.get('SOLIGENT_USERNAME', '')
    password = os.environ.get('SOLIGENT_PASSWORD', '')

    print("=" * 70)
    print("TESTING WAREHOUSE INVENTORY WITH SELENIUM")
    print("=" * 70)

    # Setup Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = None
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Test with product that HAS inventory (user confirmed)
        test_url = "https://connect.soligent.net/Square-D-DU323RB-3-Pole-AC-100A-Disconnect"

        print(f"\n📡 Loading product page: {test_url}")
        driver.get(test_url)

        # Wait for page to load and JavaScript to execute
        print("⏳ Waiting for JavaScript to load inventory data...")
        time.sleep(3)  # Wait for the half-second delay plus extra time

        # Try to find the inventory element
        try:
            inventory_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "inventory-display"))
            )
            print("✅ Found inventory-display div!")
        except TimeoutException:
            print("❌ Timeout waiting for inventory-display div")
            inventory_div = None

        # Get the page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Search for the inventory display
        inventory_display = soup.find('div', class_='inventory-display')

        if inventory_display:
            print("\n✅ FOUND INVENTORY DISPLAY!")
            print("=" * 70)

            # Find the warehouse list
            warehouse_list = inventory_display.find('ul')
            if warehouse_list:
                print("\n📦 WAREHOUSE INVENTORY:")
                warehouse_inventory = {}

                for li in warehouse_list.find_all('li'):
                    text = li.get_text().strip()
                    if ':' in text:
                        parts = text.split(':', 1)
                        location = parts[0].strip().replace('<b>', '').replace('</b>', '')
                        try:
                            quantity = int(parts[1].strip().replace(',', ''))
                            warehouse_inventory[location] = quantity
                            print(f"  {location}: {quantity}")
                        except ValueError:
                            continue

                total = sum(warehouse_inventory.values())
                print(f"\n📊 TOTAL INVENTORY: {total}")
                print(f"📍 WAREHOUSES: {len(warehouse_inventory)}")

                # Display the data structure we'll use
                print("\n" + "=" * 70)
                print("DATA STRUCTURE FOR SCRAPER:")
                print("=" * 70)
                print(f"warehouse_inventory = {warehouse_inventory}")

            else:
                print("❌ No <ul> found inside inventory-display")
                print(f"HTML content:\n{inventory_display.prettify()[:500]}")
        else:
            print("\n❌ NO INVENTORY DISPLAY FOUND")
            print("\nSearching for any inventory-related elements...")

            # Search for any element with "inventory" in class
            inv_elements = soup.find_all(class_=lambda x: x and 'inventory' in str(x).lower())
            if inv_elements:
                print(f"Found {len(inv_elements)} elements with 'inventory' in class:")
                for elem in inv_elements[:5]:
                    print(f"  - {elem.name}: {elem.get('class')}")
                    print(f"    Text: {elem.get_text()[:100]}")

            # Search for warehouse names
            page_text = soup.get_text()
            if 'Arlington' in page_text or 'Fontana' in page_text:
                print("\n⚠️ Found warehouse names in page text!")
                print("This suggests inventory might be in a different location")

        print("\n" + "=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    test_selenium_inventory()
