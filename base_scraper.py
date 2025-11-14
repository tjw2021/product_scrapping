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
        Returns a dictionary with standard fields
        """
        return {
            'distributor': self.distributor_name,
            'product_id': kwargs.get('product_id', 'N/A'),
            'sku': kwargs.get('sku', 'N/A'),
            'title': kwargs.get('title', 'N/A'),
            'brand': kwargs.get('brand', 'N/A'),
            'wattage': kwargs.get('wattage', 'N/A'),
            'efficiency': kwargs.get('efficiency', 'N/A'),
            'price': kwargs.get('price', 0.0),
            'compare_price': kwargs.get('compare_price', 0.0),
            'stock_status': kwargs.get('stock_status', 'Unknown'),
            'inventory_qty': kwargs.get('inventory_qty', 'N/A'),
            'shipping_cost': kwargs.get('shipping_cost', 'N/A'),
            'product_url': kwargs.get('product_url', 'N/A'),
            'image_url': kwargs.get('image_url', 'N/A'),
            'specs': kwargs.get('specs', {}),
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
