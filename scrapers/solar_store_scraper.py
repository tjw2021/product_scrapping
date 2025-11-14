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
        """Scrape all solar panel products from The Solar Store"""
        all_products = []
        page = 1

        while True:
            try:
                # Use Shopify's JSON endpoint with pagination
                url = f"{self.base_url}/collections/all-solar-panels/products.json?limit=250&page={page}"

                print(f"  📄 Fetching page {page}...")
                response = self.make_request(url)

                if not response:
                    break

                data = response.json()
                products = data.get('products', [])

                if not products:
                    print(f"  ✅ Completed. Total products: {len(all_products)}")
                    break

                for product in products:
                    # Extract relevant product information
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
                            shipping_cost='Calculated at Checkout',
                            product_url=f"{self.base_url}/products/{product['handle']}",
                            image_url=product.get('images', [{}])[0].get('src', 'N/A') if product.get('images') else 'N/A',
                            specs={
                                'product_type': product.get('product_type', 'Solar Panel'),
                                'tags': ', '.join(product.get('tags', [])),
                                'weight': variant.get('weight', 'N/A'),
                                'weight_unit': variant.get('weight_unit', 'N/A')
                            }
                        )

                        all_products.append(standardized_product)

                page += 1
                time.sleep(1)  # Be respectful to the server

            except Exception as e:
                print(f"  ⚠️ Error on page {page}: {e}")
                break

        return all_products


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
