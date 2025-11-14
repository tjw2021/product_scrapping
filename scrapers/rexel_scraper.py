"""
Rexel USA Scraper
Scrapes products from rexelusa.com with authentication
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import pickle


class RexelScraper(BaseScraper):
    """Scraper for Rexel USA (Authenticated)"""

    def __init__(self):
        super().__init__("Rexel USA")
        self.base_url = "https://www.rexelusa.com"
        self.driver = None
        self.wait = None
        
        # Product categories to scrape
        self.categories = [
            {
                'name': 'Solar Panels & Clean Energy',
                'url': f'{self.base_url}/s/solar-panels-clean-energy?cat=7wi4hw'
            },
            {
                'name': 'Safety Switches & Disconnect Switches',
                'url': f'{self.base_url}/s/safety-switches-disconnect-switches?cat=61imh9m'
            },
            {
                'name': 'Electric Meters & Temporary Power',
                'url': f'{self.base_url}/s/electric-meters-temporary-power?cat=kqi4hl0'
            }
        ]
        
        self.username = os.environ.get('REXEL_USERNAME')
        self.password = os.environ.get('REXEL_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("REXEL_USERNAME and REXEL_PASSWORD must be set in environment variables")

    def setup_driver(self):
        """Setup headless Chrome driver using undetected-chromedriver"""
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Find Chromium binary
        import subprocess
        try:
            chromium_path = subprocess.check_output(['which', 'chromium']).decode().strip()
            if chromium_path:
                options.binary_location = chromium_path
                print(f"  📍 Found Chromium at: {chromium_path}")
        except subprocess.CalledProcessError:
            print(f"  ⚠️ Chromium not found in PATH")
        
        # Create undetected chromedriver instance
        self.driver = uc.Chrome(options=options, version_main=138)
        self.driver.set_page_load_timeout(60)
        self.wait = WebDriverWait(self.driver, 20)
        print(f"  🌐 Undetected ChromeDriver initialized")

    def login(self):
        """Login to Rexel USA account"""
        try:
            print(f"  🔐 Logging into Rexel USA...")
            
            # Navigate to login URL
            login_url = "https://auth.rexelusa.com/login?returnUrl=/connect/authorize/callback?protocol=oauth2%26response_type=code%26access_type=offline%26client_id=storefront-web-v2%26redirect_uri=https%253A%252F%252Fwww.rexelusa.com%252Fcallback%26scope=sf.web%2520offline_access%26state=cWOoKHVuNpCne2b2SchKv%26code_challenge_method=S256%26banner=REXEL%26code_challenge=ZcDgZhNjZuYBqIqyMmX8wtITz4lcM63hXRBgyiHfYMQ"
            self.driver.get(login_url)
            
            # Wait for login page to load
            time.sleep(3)
            
            # Find and fill username field
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "Input_Username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.ID, "Input_Password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect to main site
            print(f"  ⏳ Waiting for authentication...")
            time.sleep(5)
            
            # Check if we're redirected to the main site
            if "rexelusa.com" in self.driver.current_url and "auth.rexelusa.com" not in self.driver.current_url:
                print(f"  ✅ Successfully logged in!")
                return True
            else:
                print(f"  ⚠️ Login may have failed. Current URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"  ❌ Login error: {e}")
            return False

    def wait_for_page_load(self):
        """Wait for Vue.js/Nuxt.js page to finish loading"""
        try:
            # Wait for page ready state
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # Additional wait for Vue hydration
            time.sleep(2)
        except TimeoutException:
            pass

    def extract_product_data(self, product_element):
        """Extract product data from a product card element"""
        try:
            product_data = {}
            
            # Extract title
            try:
                title_elem = product_element.find_element(By.CSS_SELECTOR, "[class*='title'], [class*='name'], h2, h3")
                product_data['title'] = title_elem.text.strip()
            except NoSuchElementException:
                product_data['title'] = 'N/A'
            
            # Extract SKU/Item Number
            try:
                sku_elem = product_element.find_element(By.CSS_SELECTOR, "[class*='sku'], [class*='item'], [class*='product-id']")
                product_data['sku'] = sku_elem.text.strip()
            except NoSuchElementException:
                product_data['sku'] = 'N/A'
            
            # Extract price
            try:
                price_elem = product_element.find_element(By.CSS_SELECTOR, "[class*='price']")
                price_text = price_elem.text.strip()
                # Extract numeric price
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                if price_match:
                    product_data['price'] = float(price_match.group(1).replace(',', ''))
                else:
                    product_data['price'] = 0.0
            except (NoSuchElementException, ValueError):
                product_data['price'] = 0.0
            
            # Extract availability/stock
            try:
                stock_elem = product_element.find_element(By.CSS_SELECTOR, "[class*='stock'], [class*='availability'], [class*='inventory']")
                stock_text = stock_elem.text.strip().lower()
                
                # Check if zero inventory
                if any(term in stock_text for term in ['out of stock', 'unavailable', '0 in stock', 'not available']):
                    return None  # Skip zero inventory items
                
                product_data['stock_status'] = stock_text
                
                # Try to extract numeric quantity
                qty_match = re.search(r'(\d+)\s*(in stock|available)', stock_text)
                if qty_match:
                    product_data['inventory_qty'] = int(qty_match.group(1))
                else:
                    product_data['inventory_qty'] = 'Available'
                    
            except NoSuchElementException:
                product_data['stock_status'] = 'Unknown'
                product_data['inventory_qty'] = 'Unknown'
            
            # Extract product URL
            try:
                link_elem = product_element.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                product_data['url'] = link_elem.get_attribute('href')
            except NoSuchElementException:
                product_data['url'] = 'N/A'
            
            # Extract brand
            try:
                brand_elem = product_element.find_element(By.CSS_SELECTOR, "[class*='brand'], [class*='manufacturer']")
                product_data['brand'] = brand_elem.text.strip()
            except NoSuchElementException:
                # Try to extract from title
                if product_data['title'] != 'N/A':
                    words = product_data['title'].split()
                    product_data['brand'] = words[0] if words else 'N/A'
                else:
                    product_data['brand'] = 'N/A'
            
            return product_data
            
        except Exception as e:
            print(f"  ⚠️ Error extracting product data: {e}")
            return None

    def scrape_category(self, category_url, category_name):
        """Scrape products from a specific category"""
        products = []
        
        try:
            print(f"  📂 Scraping category: {category_name}")
            self.driver.get(category_url)
            self.wait_for_page_load()
            
            # Scroll to load all products (if infinite scroll)
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 10
            
            while scroll_attempts < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            # Wait for product elements to load
            time.sleep(2)
            
            # Try different selectors for product cards
            product_selectors = [
                "[class*='product-card']",
                "[class*='product-item']",
                "[class*='ProductCard']",
                ".product",
                "[data-testid*='product']"
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    product_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if product_elements:
                        print(f"  ✅ Found {len(product_elements)} products using selector: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not product_elements:
                print(f"  ⚠️ No products found in {category_name}")
                return products
            
            # Extract data from each product
            for idx, product_elem in enumerate(product_elements, 1):
                product_data = self.extract_product_data(product_elem)
                
                # Skip if zero inventory or extraction failed
                if product_data is None:
                    continue
                
                # Convert to standardized format
                standardized = self.get_standardized_product(
                    product_id=product_data.get('sku', f'REXEL-{idx}'),
                    sku=product_data.get('sku', 'N/A'),
                    title=product_data.get('title', 'N/A'),
                    brand=product_data.get('brand', 'N/A'),
                    wattage=self.extract_wattage(product_data.get('title', '')),
                    efficiency='N/A',
                    price=product_data.get('price', 0.0),
                    compare_price=0.0,
                    stock_status=product_data.get('stock_status', 'Available'),
                    inventory_qty=product_data.get('inventory_qty', 'Available'),
                    shipping_cost='Calculated at Checkout',
                    product_url=product_data.get('url', 'N/A'),
                    image_url='N/A',
                    specs={'category': category_name}
                )
                
                products.append(standardized)
            
            print(f"  ✅ Extracted {len(products)} products from {category_name}")
            
        except Exception as e:
            print(f"  ❌ Error scraping {category_name}: {e}")
        
        return products

    def scrape_products(self):
        """Scrape all products from configured categories"""
        all_products = []
        
        try:
            # Setup Selenium driver
            self.setup_driver()
            
            # Login to Rexel
            if not self.login():
                print(f"  ❌ Failed to login. Cannot proceed with scraping.")
                return all_products
            
            # Scrape each category
            for category in self.categories:
                category_products = self.scrape_category(
                    category['url'],
                    category['name']
                )
                all_products.extend(category_products)
                
                # Be respectful - wait between categories
                time.sleep(2)
            
            print(f"  ✅ Total products scraped: {len(all_products)}")
            
        except Exception as e:
            print(f"  ❌ Error during scraping: {e}")
        
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                print(f"  🔒 Browser closed")
        
        return all_products


if __name__ == "__main__":
    scraper = RexelScraper()
    products = scraper.run()
    print(f"\n✅ Scraped {len(products)} products total")
    
    # Show sample product
    if products:
        print("\nSample product:")
        print(f"Title: {products[0]['title']}")
        print(f"SKU: {products[0]['sku']}")
        print(f"Price: ${products[0]['price']}")
        print(f"Stock: {products[0]['stock_status']}")
