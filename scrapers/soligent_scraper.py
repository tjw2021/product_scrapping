"""
Soligent Scraper - API-based scraping for Soligent products
Uses NetSuite SuiteCommerce REST API (no authentication required for public data)
"""

import os
import time
import re
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

try:
    from .base_scraper import BaseScraper
except ImportError:
    from base_scraper import BaseScraper


class SoligentScraper(BaseScraper):
    """Scraper for Soligent (connect.soligent.net) using NetSuite API"""

    BASE_URL = "https://connect.soligent.net"
    API_URL = f"{BASE_URL}/api/items"
    CACHEABLE_API_URL = f"{BASE_URL}/api/cacheable/items"
    COMPANY_ID = "3510556"  # Found in page source

    # Mapping of location internal IDs to warehouse names
    LOCATION_MAP = {
        "123": "Fontana, CA",
        "187": "Las Vegas, NV",
        "220": "Sacramento, CA",
        "244": "Arlington, TX",
        "251": "Orlando, FL",
        "278": "Tampa, FL",
        "285": "Millstone, NJ",
    }

    def __init__(self):
        super().__init__("Soligent")
        self.session = requests.Session()

        # Get credentials from environment
        username = os.environ.get('SOLIGENT_USERNAME', '')
        password = os.environ.get('SOLIGENT_PASSWORD', '')

        # Set up basic auth if credentials are available
        if username and password:
            self.session.auth = (username, password)

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': self.BASE_URL
        })
        
    def _fetch_products_page(self, page: int = 1, page_size: int = 48, category_filter: str = "") -> Dict:
        """
        Fetch products from API
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            category_filter: Category filter (e.g., "category:123")
        Returns:
            API response dictionary
        """
        params = {
            'c': self.COMPANY_ID,
            'fieldset': 'search',  # Can also use 'details' for more info
            'include': 'facets',
            'n': str(page_size),
            'page': str(page)
        }
        
        if category_filter:
            params['filter'] = category_filter
        
        try:
            response = self.session.get(self.API_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ❌ Error fetching page {page}: {e}")
            return {}
    
    def _fetch_product_details(self, item_id: str) -> Optional[Dict]:
        """
        Fetch detailed product information
        Args:
            item_id: Internal item ID
        Returns:
            Product details dictionary
        """
        url = f"{self.API_URL}/{item_id}"
        params = {
            'c': self.COMPANY_ID,
            'fieldset': 'details'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"    ⚠️  Error fetching details for item {item_id}: {e}")
            return None
    
    def _fetch_warehouse_inventory(self, product_url_component: str) -> Dict[str, int]:
        """
        Fetch warehouse-specific inventory using the cacheable items API
        Args:
            product_url_component: URL component/slug for the product
        Returns:
            Dictionary mapping warehouse locations to quantities
        """
        try:
            params = {
                'c': self.COMPANY_ID,
                'country': 'US',
                'currency': 'USD',
                'fieldset': 'details',
                'include': '',
                'language': 'en',
                'n': '2',
                'pricelevel': '5',
                'url': product_url_component,
                'use_pcv': 'T'
            }

            response = self.session.get(self.CACHEABLE_API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Extract warehouse inventory from response
            warehouse_inventory = {}

            if 'items' in data and data['items']:
                item = data['items'][0]
                qty_detail = item.get('quantityavailable_detail', {})
                locations = qty_detail.get('locations', [])

                for location in locations:
                    loc_id = str(location.get('internalid', ''))
                    qty = location.get('quantityavailable', 0)

                    # Map location ID to warehouse name
                    warehouse_name = self.LOCATION_MAP.get(loc_id, f"Location {loc_id}")

                    if qty > 0:  # Only include warehouses with stock
                        warehouse_inventory[warehouse_name] = int(qty)

            return warehouse_inventory

        except Exception as e:
            # Don't print errors for every product to avoid log spam
            return {}
    
    def _parse_product(self, item: Dict) -> Optional[Dict]:
        """
        Parse product from API response
        Args:
            item: Product item from API
        Returns:
            Parsed product dictionary
        """
        # Handle case where item might be a list (skip it silently)
        if not isinstance(item, dict):
            return None
            
        try:
            # Extract basic info
            title = item.get('salesdescription', item.get('storedisplayname2', 'N/A'))
            item_id = str(item.get('internalid', item.get('itemid', 'N/A')))
            sku = item.get('custcol_sol_mfr_part_number', item.get('mpn', 'N/A'))
            
            # Check for domestic content in title (products with domestic content have it in the name)
            has_domestic_content_in_title = 'domestic content' in title.lower()
            
            # Extract manufacturer/brand
            brand = item.get('custitem_sol_manufacturer_for_web', 'N/A')
            
            # Extract pricing
            price_detail = item.get('onlinecustomerprice_detail', {})
            price = float(price_detail.get('onlinecustomerprice', 0.0))
            compare_price = float(item.get('pricelevel1', 0.0))
            
            # Extract stock info
            stock_desc = item.get('stockdescription', '').strip()
            is_in_stock = item.get('isinstock', False)
            is_purchasable = item.get('ispurchasable', False)
            quantity_available = item.get('quantityavailable', 0)
            
            # Determine stock status - Soligent appears to set isinstock=False but items are still purchasable
            if 'dropship' in stock_desc.lower():
                stock_status = 'Dropship'
            elif stock_desc:
                # Use the actual stock description from the site
                stock_status = stock_desc
            elif is_in_stock or quantity_available > 0:
                stock_status = 'In Stock'
            elif is_purchasable:
                stock_status = 'Available'
            else:
                stock_status = 'Out of Stock'
            
            # Extract image
            images = item.get('itemimages_detail', {})
            image_url = ''
            if images:
                first_image = list(images.values())[0]
                image_url = first_image.get('url', '')
            
            # Build product URL
            url_component = item.get('urlcomponent', '')
            product_url = f"{self.BASE_URL}/{url_component}" if url_component else f"{self.BASE_URL}/item/{item_id}"

            # Extract wattage from title or custom fields
            wattage = self.extract_wattage(title)
            if wattage == 'N/A':
                # Check custom fields for wattage
                watt_field = item.get('wattage', item.get('custitem_sol_pv_watts', ''))
                if watt_field:
                    wattage = f"{watt_field}W"
            
            # Extract dimensions if available
            dimensions = item.get('custitem_dimensions', 'N/A')
            weight = item.get('weight', 'N/A')
            
            # Extract domestic content flag (check both API field and title)
            domestic_content_api = item.get('custitem_dom_content', False)
            domestic_content = domestic_content_api or has_domestic_content_in_title
            domestic_content_str = 'Yes' if domestic_content else 'No'
            
            # Extract warehouse/location info
            location = item.get('location', item.get('custitem_location', 'N/A'))
            
            # Build specs dictionary (warehouse inventory will be added during detail fetch)
            specs = {
                'description': item.get('storedetaileddescription', title),
                'manufacturer_part': sku,
                'dimensions': dimensions,
                'weight': str(weight) if weight and weight != 'N/A' else 'N/A',
                'location': str(location) if location and location != 'N/A' else 'N/A',
                'stock_description': stock_desc,
                'domestic_content': domestic_content_str,
                'warehouse_inventory': {}  # Will be populated later
            }
            
            return {
                'product_id': item_id,
                'sku': sku,
                'title': title,
                'brand': brand,
                'wattage': wattage,
                'price': price,
                'compare_price': compare_price,
                'stock_status': stock_status,
                'inventory_qty': str(quantity_available) if quantity_available else 'N/A',
                'product_url': product_url,
                'url_component': url_component,  # For warehouse inventory API
                'image_url': image_url,
                'specs': specs
            }
            
        except Exception as e:
            print(f"    ⚠️  Error parsing product: {e}")
            return None
    
    def scrape_products(self) -> List[Dict]:
        """
        Scrape PV modules from Soligent using API
        Returns list of standardized product dictionaries
        """
        print(f"\n{'='*60}")
        print(f"🔍 SCRAPING: {self.distributor_name}")
        print(f"{'='*60}")
        
        all_products = []
        page = 1
        page_size = 48
        
        try:
            # First request to get total count
            print(f"\n📊 Fetching product count...")
            first_page = self._fetch_products_page(page=1, page_size=page_size)
            
            if not first_page or 'items' not in first_page:
                print("❌ Failed to fetch products from API")
                return []
            
            total_products = first_page.get('total', 0)
            total_pages = (total_products // page_size) + (1 if total_products % page_size else 0)
            
            print(f"  ✅ Found {total_products} total products across {total_pages} pages")
            
            # Process first page
            print(f"\n📄 Processing page 1/{total_pages}...")
            for item in first_page.get('items', []):
                product = self._parse_product(item)
                if product:
                    all_products.append(product)
            
            print(f"  ✅ Extracted {len(all_products)} products from page 1")
            
            # Fetch remaining pages
            for page_num in range(2, total_pages + 1):
                print(f"\n📄 Processing page {page_num}/{total_pages}...")
                
                page_data = self._fetch_products_page(page=page_num, page_size=page_size)
                
                if not page_data or 'items' not in page_data:
                    print(f"  ⚠️  No data returned for page {page_num}, stopping")
                    break
                
                page_products_count = 0
                for item in page_data.get('items', []):
                    product = self._parse_product(item)
                    if product:
                        all_products.append(product)
                        page_products_count += 1
                
                print(f"  ✅ Extracted {page_products_count} products from page {page_num}")
                
                # Respectful delay between requests
                time.sleep(1)
                
                # Safety limit to avoid infinite loops
                if page_num >= 100:
                    print(f"  ⚠️  Reached page limit (100), stopping")
                    break
            
            print(f"\n✅ Scraped {len(all_products)} total products from {self.distributor_name}")
            
            # TODO: Warehouse inventory fetching requires authentication
            # To enable this feature, set SOLIGENT_USERNAME environment variable
            soligent_username = os.environ.get('SOLIGENT_USERNAME', '')
            soligent_password = os.environ.get('SOLIGENT_PASSWORD', '')
            
            if soligent_username and soligent_password:
                print(f"\n📦 Fetching warehouse inventory for {len(all_products)} products...")
                print(f"  ⚠️  This may take several minutes...")
                
                # TODO: Implement login authentication here
                # self._login(soligent_username, soligent_password)
                
                for idx, product in enumerate(all_products, 1):
                    if idx % 50 == 0 or idx == 1:
                        print(f"  📍 Progress: {idx}/{len(all_products)} products...")

                    url_component = product.get('url_component', '')
                    if url_component:
                        warehouse_inv = self._fetch_warehouse_inventory(url_component)
                        if warehouse_inv:
                            product['specs']['warehouse_inventory'] = warehouse_inv

                            # Calculate total inventory from warehouses
                            total_qty = sum(warehouse_inv.values())
                            product['inventory_qty'] = str(total_qty)

                            # Format for location field (show all warehouses)
                            location_str = "; ".join([f"{loc}: {qty}" for loc, qty in warehouse_inv.items()])
                            product['specs']['location'] = location_str

                        # Be respectful with rate limiting
                        if idx % 10 == 0:
                            time.sleep(2)
                        else:
                            time.sleep(0.5)
                
                print(f"  ✅ Completed warehouse inventory fetch")
            else:
                print(f"\n⚠️  Warehouse inventory requires authentication")
                print(f"  💡 Set SOLIGENT_USERNAME and SOLIGENT_PASSWORD to enable this feature")
            
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


if __name__ == "__main__":
    # Test the scraper
    scraper = SoligentScraper()
    products = scraper.scrape_products()
    print(f"\n{'='*60}")
    print(f"SUMMARY: Found {len(products)} products")
    print(f"{'='*60}")
    if products:
        print("\nFirst 3 products:")
        import json
        for p in products[:3]:
            print(json.dumps(p, indent=2))
            print("---")
