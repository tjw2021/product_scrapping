"""
Solar Cellz USA Scraper
Scrapes products from shop.solarcellzusa.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import time


class SolarCellzScraper(BaseScraper):
    """Scraper for Solar Cellz USA"""

    def __init__(self):
        super().__init__("Solar Cellz USA")
        self.base_url = "https://shop.solarcellzusa.com"

    def scrape_products(self):
        """Scrape the entire Solar Cellz USA catalog (all products, all collections).

        NOTE: as of the last check this host returns 404 on both /products.json
        and /collections/*/products.json — it is no longer a standard Shopify
        storefront, so this will return 0 until the correct storefront URL or a
        dedicated (non-Shopify) scraper is supplied. See scrapers/README notes.
        """
        return self.scrape_shopify_store(self.base_url, shipping_cost='Calculated at Checkout')


if __name__ == "__main__":
    scraper = SolarCellzScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
