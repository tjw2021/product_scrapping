"""
The Solar Store Scraper
Scrapes solar panels from thesolarstore.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import time


class SolarStoreScraper(BaseScraper):
    """Scraper for The Solar Store"""

    def __init__(self):
        super().__init__("The Solar Store")
        self.base_url = "https://thesolarstore.com"

    def scrape_products(self):
        """Scrape the entire Solar Store catalog (all products, all collections)."""
        return self.scrape_shopify_store(self.base_url, shipping_cost='Calculated at Checkout')


if __name__ == "__main__":
    scraper = SolarStoreScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
    
    # Show sample product
    if products:
        print("\nSample product:")
        print(f"Title: {products[0]['title']}")
        print(f"Price: ${products[0]['price']}")
        print(f"Brand: {products[0]['brand']}")
        print(f"Wattage: {products[0]['wattage']}")
