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
        # Multiple product categories
        self.collections = [
            'solar-panels',
            'off-grid-solar-inverters',
            'hybrid-inverters',
            'charge-controllers'
        ]

    def scrape_collection(self, collection_name):
        """Scrape products from a specific collection"""
        products = []
        page = 1

        print(f"  📂 Scraping collection: {collection_name}")

        while page <= 10:
            try:
                url = f"{self.base_url}/collections/{collection_name}/products.json?limit=250&page={page}"
                
                print(f"    📄 Page {page}...")
                response = self.make_request(url)

                if not response:
                    break

                data = response.json()
                collection_products = data.get('products', [])

                if not collection_products:
                    print(f"    ✅ Completed {collection_name}: {len(products)} products")
                    break

                for product in collection_products:
                    for variant in product.get('variants', []):
                        wattage = self.extract_wattage(product['title'])
                        efficiency = self.extract_efficiency(product['title'], {})

                        standardized_product = self.get_standardized_product(
                            product_id=str(product['id']),
                            sku=variant.get('sku', 'N/A'),
                            title=product['title'],
                            brand=product.get('vendor', 'N/A'),
                            wattage=wattage,
                            efficiency=efficiency,
                            price=float(variant.get('price', 0)),
                            compare_price=float(variant.get('compare_at_price', 0)) if variant.get('compare_at_price') else 0,
                            stock_status='In Stock' if variant.get('available') else 'Out of Stock',
                            inventory_qty=variant.get('inventory_quantity', 'N/A'),
                            shipping_cost='Varies by Product',
                            product_url=f"{self.base_url}/products/{product['handle']}",
                            image_url=product.get('images', [{}])[0].get('src', 'N/A') if product.get('images') else 'N/A',
                            specs={
                                'product_type': product.get('product_type', 'N/A'),
                                'collection': collection_name
                            }
                        )

                        products.append(standardized_product)

                page += 1
                time.sleep(1)

            except Exception as e:
                print(f"    ⚠️ Error on page {page}: {e}")
                break

        return products

    def scrape_products(self):
        """Scrape products from all collections"""
        all_products = []
        
        for collection in self.collections:
            collection_products = self.scrape_collection(collection)
            all_products.extend(collection_products)
            time.sleep(1)

        return all_products


if __name__ == "__main__":
    scraper = AltEScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
