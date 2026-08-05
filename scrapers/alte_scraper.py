"""
altE Store Scraper
Scrapes products from altestore.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import time


class AltEScraper(BaseScraper):
    """Scraper for altE Store"""

    def __init__(self):
        super().__init__("altE Store")
        self.base_url = "https://www.altestore.com"

    def scrape_products(self):
        """Scrape the entire altE Store catalog (all products, all collections)."""
        return self.scrape_shopify_store(self.base_url, shipping_cost='Varies by Product')


if __name__ == "__main__":
    scraper = AltEScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
