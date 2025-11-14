"""
Base Scraper Class
All distributor scrapers inherit from this base class
"""

from abc import ABC, abstractmethod
from datetime import datetime
import requests
from typing import List, Dict, Optional
import time


class BaseScraper(ABC):
    """Abstract base class for all distributor scrapers"""

    def __init__(self, distributor_name: str):
        self.distributor_name = distributor_name
        self.products = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    @abstractmethod
    def scrape_products(self) -> List[Dict]:
        """
        Scrape products from the distributor
        Must be implemented by each distributor scraper
        Returns list of product dictionaries
        """
        pass

    def get_standardized_product(self, **kwargs) -> Dict:
        """
        Standardize product data across all distributors
        Returns a dictionary with standard fields including quantity and price per unit
        """
        title = kwargs.get('title', 'N/A')
        specs = kwargs.get('specs', {})
        price = kwargs.get('price', 0.0)
        
        # Extract quantity from title (e.g., "Pallet of 30", "(7) panels")
        quantity = self.extract_quantity(title)
        
        # Calculate price per unit
        price_per_unit = self.calculate_price_per_unit(price, quantity)
        
        # Determine product category
        category = self.extract_product_category(title, specs)
        
        return {
            'distributor': self.distributor_name,
            'category': category,
            'product_id': kwargs.get('product_id', 'N/A'),
            'sku': kwargs.get('sku', 'N/A'),
            'title': title,
            'brand': kwargs.get('brand', 'N/A'),
            'wattage': kwargs.get('wattage', 'N/A'),
            'efficiency': kwargs.get('efficiency', 'N/A'),
            'quantity': quantity,
            'price': price,
            'price_per_unit': price_per_unit,
            'compare_price': kwargs.get('compare_price', 0.0),
            'stock_status': kwargs.get('stock_status', 'Unknown'),
            'inventory_qty': kwargs.get('inventory_qty', 'N/A'),
            'shipping_cost': kwargs.get('shipping_cost', 'N/A'),
            'product_url': kwargs.get('product_url', 'N/A'),
            'image_url': kwargs.get('image_url', 'N/A'),
            'specs': specs,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def make_request(self, url: str, timeout: int = 10, retries: int = 3) -> Optional[requests.Response]:
        """
        Make HTTP request with retry logic
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    print(f"❌ Failed to fetch {url} after {retries} attempts: {e}")
                    return None
                print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def extract_wattage(self, title: str) -> str:
        """Extract wattage from product title"""
        import re
        match = re.search(r'(\d+)\s*[Ww](?:att)?', title)
        return f"{match.group(1)}W" if match else 'N/A'

    def extract_efficiency(self, title: str, specs: dict) -> str:
        """Extract efficiency from title or specs"""
        import re
        # Try to find efficiency in title (e.g., "22.5%" or "22.5 efficiency")
        match = re.search(r'(\d+\.?\d*)\s*%?\s*[Ee]ff', title)
        if match:
            return f"{match.group(1)}%"

        # Try specs dictionary
        if 'efficiency' in specs:
            return specs['efficiency']

        return 'N/A'

    def extract_quantity(self, title: str) -> int:
        """
        Extract quantity from product title for bulk items
        Examples: 
        - "Pallet of 30 Solar Panels" -> 30
        - "Solar Panel - 10 Pack" -> 10
        - "Case of 12 Inverters" -> 12
        - "(7) Solar Panels Pack" -> 7 (only if followed by pack/bundle indicator)
        
        Does NOT match specifications like:
        - "(7600W)" -> 1 (wattage spec)
        - "(30A)" -> 1 (amperage spec)
        - "400W Panel" -> 1 (single unit with wattage)
        """
        import re
        
        # Pattern 1: "pallet of X" or "case of X" or "pack of X" (most reliable)
        match = re.search(r'(?:pallet|case|pack|box|bundle|lot|set)\s+of\s+(\d+)', title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Pattern 2: "X pack" or "X-pack" (e.g., "10 pack", "5-pack")
        match = re.search(r'\b(\d+)[-\s]?pack\b', title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Pattern 3: "quantity: X" or "qty: X"
        match = re.search(r'(?:quantity|qty)[:\s]+(\d+)', title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Pattern 4: "X units" or "X pieces" or "X pcs"
        match = re.search(r'\b(\d+)\s+(?:units|pcs|pieces)\b', title, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Pattern 5: "(X) panels/inverters/batteries" - only if followed by product type
        match = re.search(r'\((\d+)\)\s+(?:solar\s+)?(?:panels?|inverters?|batteries|modules?|controllers?)', title, re.IGNORECASE)
        if match:
            qty = int(match.group(1))
            # Sanity check: reasonable bulk quantities are typically 2-100
            if 2 <= qty <= 100:
                return qty
        
        # Default: single unit
        return 1

    def calculate_price_per_unit(self, price: float, quantity: int) -> float:
        """Calculate price per unit for bulk items"""
        if quantity > 0 and price > 0:
            return round(price / quantity, 2)
        return price

    def extract_product_category(self, title: str, specs: dict) -> str:
        """
        Determine product category from title and specs
        Categories: Solar Panel, Inverter, Battery, Charge Controller, Racking, BOS, Other
        """
        import re
        
        title_lower = title.lower()
        
        # Check specs first if available
        if specs.get('product_type'):
            product_type = specs['product_type'].lower()
            if 'panel' in product_type or 'module' in product_type:
                return 'Solar Panel'
            elif 'inverter' in product_type:
                return 'Inverter'
            elif 'battery' in product_type or 'storage' in product_type:
                return 'Battery/Storage'
            elif 'charge' in product_type or 'controller' in product_type:
                return 'Charge Controller'
            elif 'rack' in product_type or 'mount' in product_type:
                return 'Racking/Mounting'
        
        # Check collection if available
        if specs.get('collection'):
            collection = specs['collection'].lower()
            if 'panel' in collection:
                return 'Solar Panel'
            elif 'inverter' in collection:
                return 'Inverter'
            elif 'batter' in collection or 'storage' in collection:
                return 'Battery/Storage'
            elif 'charge' in collection or 'controller' in collection:
                return 'Charge Controller'
            elif 'rack' in collection or 'mount' in collection:
                return 'Racking/Mounting'
        
        # Fallback to title analysis
        if re.search(r'\b(?:solar\s+)?panel|module|pv\s+panel\b', title_lower):
            return 'Solar Panel'
        elif re.search(r'\binverter|micro[-\s]?inverter|grid[-\s]?tie|off[-\s]?grid\b', title_lower):
            return 'Inverter'
        elif re.search(r'\bbattery|batteries|storage|energy\s+storage|lithium|lifepo4\b', title_lower):
            return 'Battery/Storage'
        elif re.search(r'\bcharge\s+controller|mppt|pwm\s+controller\b', title_lower):
            return 'Charge Controller'
        elif re.search(r'\bracking|mounting|rail|bracket|clamp|flashings?\b', title_lower):
            return 'Racking/Mounting'
        elif re.search(r'\bcombiner|disconnect|breaker|fuse|wire|cable|conduit\b', title_lower):
            return 'BOS/Electrical'
        
        return 'Other'

    def calculate_discount(self, price: float, compare_price: float) -> float:
        """Calculate discount percentage"""
        if compare_price > 0 and price > 0:
            return round(((compare_price - price) / compare_price) * 100, 2)
        return 0.0

    def run(self) -> List[Dict]:
        """
        Main execution method
        Returns list of scraped products
        """
        print(f"\n{'='*60}")
        print(f"🔍 Scraping {self.distributor_name}...")
        print(f"{'='*60}")

        self.products = self.scrape_products()

        print(f"✅ Scraped {len(self.products)} products from {self.distributor_name}")

        return self.products
