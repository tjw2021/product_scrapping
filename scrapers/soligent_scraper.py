"""
Soligent Scraper - Authenticated scraping for Soligent products
Uses Selenium for JavaScript-based authentication
"""

import os
import time
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

from .base_scraper import BaseScraper


class SoligentScraper(BaseScraper):
    """Scraper for Soligent (connect.soligent.net) with authentication"""
    
    BASE_URL = "https://connect.soligent.net"
    LOGIN_URL = f"{BASE_URL}/login"
    PV_URL = f"{BASE_URL}/pv"
    
    def __init__(self):
        super().__init__("Soligent")
        self.username = "admin@infrasale.com"
        self.password = os.environ.get('SOLIGENT_PASSWORD', '')
        self.driver = None
        self.is_authenticated = False
        
    def _setup_driver(self):
        """Initialize Selenium WebDriver with headless Chrome"""
        if self.driver:
            return
            
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True)
            print("✅ Selenium WebDriver initialized")
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            raise
    
    def _login(self) -> bool:
        """
        Authenticate with Soligent using Selenium
        Returns True if login successful
        """
        if self.is_authenticated:
            return True
            
        if not self.password:
            print("❌ SOLIGENT_PASSWORD not set in environment variables")
            return False
        
        try:
            print(f"🔐 Logging in to {self.LOGIN_URL}...")
            self._setup_driver()
            
            # Navigate to login page
            self.driver.get(self.LOGIN_URL)
            time.sleep(3)  # Wait for page load
            
            # Try to find and click the login button/link to open login modal
            try:
                login_link = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
                )
                login_link.click()
                print("  📝 Clicked login link")
                time.sleep(2)
            except (TimeoutException, NoSuchElementException):
                print("  ⚠️  Login link not found, trying direct form")
            
            # Wait for email input field
            try:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input#email"))
                )
                email_input.clear()
                email_input.send_keys(self.username)
                print(f"  📧 Entered email: {self.username}")
                time.sleep(1)
                
                # Find password field
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password'], input#password")
                password_input.clear()
                password_input.send_keys(self.password)
                print("  🔑 Entered password")
                time.sleep(1)
                
                # Find and click submit button
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button.login-submit")
                submit_button.click()
                print("  ✅ Clicked submit button")
                time.sleep(5)  # Wait for authentication to process
                
                # Check if login was successful by looking for logout link or user menu
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Logout"))
                    )
                    print("✅ Successfully authenticated!")
                    self.is_authenticated = True
                    return True
                except TimeoutException:
                    # Alternative check: see if we're no longer on login page
                    current_url = self.driver.current_url
                    if "login" not in current_url.lower():
                        print(f"✅ Redirected to {current_url} - authentication likely successful")
                        self.is_authenticated = True
                        return True
                    else:
                        print("❌ Login failed - still on login page")
                        return False
                        
            except (TimeoutException, NoSuchElementException) as e:
                print(f"❌ Could not find login form elements: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def _get_page_html(self, url: str) -> Optional[str]:
        """Get page HTML using authenticated Selenium session"""
        if not self.is_authenticated and not self._login():
            return None
            
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for dynamic content
            return self.driver.page_source
        except Exception as e:
            print(f"❌ Error fetching page {url}: {e}")
            return None
    
    def _parse_product_listing(self, html: str) -> List[Dict]:
        """Parse product listing page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all product items in the listing
        product_items = soup.find_all('div', class_=re.compile(r'product|item'))
        
        if not product_items:
            # Try alternative selectors
            product_items = soup.find_all('article')
        
        print(f"  📦 Found {len(product_items)} product elements on page")
        
        for item in product_items:
            try:
                product_data = self._parse_product_item(item, soup)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                print(f"  ⚠️  Error parsing product item: {e}")
                continue
        
        return products
    
    def _parse_product_item(self, item, soup) -> Optional[Dict]:
        """Parse individual product from listing"""
        try:
            # Extract title
            title_elem = item.find(['h2', 'h3', 'a'], class_=re.compile(r'title|name|product'))
            if not title_elem:
                title_elem = item.find('a', href=re.compile(r'/[^/]+$'))
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            product_url = title_elem.get('href', '')
            if product_url and not product_url.startswith('http'):
                product_url = self.BASE_URL + product_url
            
            # Extract manufacturer
            brand_elem = item.find(string=re.compile(r'Manufacturer:'))
            brand = 'N/A'
            if brand_elem:
                brand_link = brand_elem.find_next('a')
                if brand_link:
                    brand = brand_link.get_text(strip=True)
            
            # Extract SKU
            sku_elem = item.find(string=re.compile(r'SKU #:'))
            sku = 'N/A'
            if sku_elem:
                sku = sku_elem.split(':')[-1].strip()
            
            # Extract manufacturer part number
            mfr_part_elem = item.find(string=re.compile(r'Manufacturer Part #:'))
            mfr_part = 'N/A'
            if mfr_part_elem:
                mfr_part = mfr_part_elem.split(':')[-1].strip()
            
            # Extract stock status
            stock_elem = item.find(class_=re.compile(r'stock|availability'))
            stock_status = stock_elem.get_text(strip=True) if stock_elem else 'Unknown'
            
            # Extract price - will be visible after login
            price_elem = item.find(class_=re.compile(r'price'))
            price = 0.0
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract image
            img_elem = item.find('img')
            image_url = ''
            if img_elem:
                image_url = img_elem.get('src', '')
                if image_url and not image_url.startswith('http'):
                    image_url = self.BASE_URL + image_url
            
            # Extract wattage from title
            wattage = self.extract_wattage(title)
            
            # Build specs dictionary
            specs = {
                'manufacturer_part': mfr_part,
                'description': title
            }
            
            return {
                'product_id': sku,
                'sku': sku,
                'title': title,
                'brand': brand,
                'wattage': wattage,
                'price': price,
                'stock_status': stock_status,
                'product_url': product_url,
                'image_url': image_url,
                'specs': specs
            }
            
        except Exception as e:
            print(f"    ⚠️  Error parsing product: {e}")
            return None
    
    def scrape_products(self) -> List[Dict]:
        """
        Scrape PV modules from Soligent
        Returns list of standardized product dictionaries
        """
        print(f"\n{'='*60}")
        print(f"🔍 SCRAPING: {self.distributor_name}")
        print(f"{'='*60}")
        
        all_products = []
        
        try:
            # Login first
            if not self._login():
                print("❌ Authentication failed, cannot scrape products")
                return []
            
            # Start with PV modules page (show 48 items)
            page_num = 1
            items_per_page = 48
            
            while True:
                url = f"{self.PV_URL}?show={items_per_page}&page={page_num}"
                print(f"\n📄 Fetching page {page_num}: {url}")
                
                html = self._get_page_html(url)
                if not html:
                    print(f"  ❌ Failed to fetch page {page_num}")
                    break
                
                # Parse products from this page
                page_products = self._parse_product_listing(html)
                
                if not page_products:
                    print(f"  ℹ️  No products found on page {page_num}, stopping")
                    break
                
                all_products.extend(page_products)
                print(f"  ✅ Extracted {len(page_products)} products from page {page_num}")
                
                # Check if there's a next page
                soup = BeautifulSoup(html, 'html.parser')
                next_link = soup.find('a', class_=re.compile(r'next|pagination'))
                
                if not next_link or page_num >= 100:  # Safety limit
                    print(f"  ℹ️  No more pages found")
                    break
                
                page_num += 1
                time.sleep(2)  # Respectful delay between pages
            
            print(f"\n✅ Scraped {len(all_products)} total products from {self.distributor_name}")
            
            # Standardize all products
            standardized_products = []
            for product in all_products:
                standardized = self.get_standardized_product(**product)
                standardized_products.append(standardized)
            
            self.products = standardized_products
            return standardized_products
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            # Clean up driver
            if self.driver:
                try:
                    self.driver.quit()
                    print("🔒 Browser session closed")
                except:
                    pass


if __name__ == "__main__":
    # Test the scraper
    scraper = SoligentScraper()
    products = scraper.scrape_products()
    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {len(products)} products")
    print(f"{'='*60}")
    if products:
        print("\nSample product:")
        import json
        print(json.dumps(products[0], indent=2))
