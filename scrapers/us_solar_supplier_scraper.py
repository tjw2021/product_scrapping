"""
US Solar Supplier Scraper
Scrapes inverters from ussolarsupplier.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import time


class USSolarSupplierScraper(BaseScraper):
    """Scraper for US Solar Supplier (Inverters)"""

    def __init__(self):
        super().__init__("US Solar Supplier")
        self.base_url = "https://ussolarsupplier.com"

    def scrape_products(self):
        """Scrape the entire US Solar Supplier catalog (all products, all collections)."""
        return self.scrape_shopify_store(self.base_url, shipping_cost='Calculated at Checkout')


if __name__ == "__main__":
    scraper = USSolarSupplierScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} inverter products")
    
    # Show sample product
    if products:
        print("\nSample product:")
        print(f"Title: {products[0]['title']}")
        print(f"Price: ${products[0]['price']}")
        print(f"Brand: {products[0]['brand']}")
