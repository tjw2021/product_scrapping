"""
Wholesale Solar Scraper
Scrapes products from wholesalesolar.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
import time


class WholesaleSolarScraper(BaseScraper):
    """Scraper for Wholesale Solar"""

    def __init__(self):
        super().__init__("Wholesale Solar")
        self.base_url = "https://www.wholesalesolar.com"

    def scrape_products(self):
        """Scrape solar panel products from Wholesale Solar"""
        all_products = []

        # Wholesale Solar uses a different structure
        # Try common collection paths
        collections = [
            'solar-panels',
            'grid-tie-solar-panels',
            'off-grid-solar-panels'
        ]

        for collection in collections:
            page = 1
            found_products = False

            while page <= 10:  # Limit to 10 pages per collection
                try:
                    # Try Shopify JSON API
                    url = f"{self.base_url}/collections/{collection}/products.json?limit=250&page={page}"

                    print(f"  📄 Trying {collection}, page {page}...")
                    response = self.make_request(url)

                    if not response:
                        break

                    data = response.json()
                    products = data.get('products', [])

                    if not products:
                        if page == 1:
                            print(f"  ⚠️ No products in collection '{collection}'")
                        break

                    found_products = True

                    for product in products:
                        for variant in product.get('variants', []):
                            wattage = self.extract_wattage(product['title'])
                            efficiency = self.extract_efficiency(product['title'], {})

                            # Extract specs from product description if available
                            specs = {}
                            if product.get('body_html'):
                                # Could parse HTML for additional specs
                                pass

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
                                shipping_cost='Free Shipping on Orders $5000+',
                                product_url=f"{self.base_url}/products/{product['handle']}",
                                image_url=product.get('images', [{}])[0].get('src', 'N/A') if product.get('images') else 'N/A',
                                specs=specs
                            )

                            all_products.append(standardized_product)

                    page += 1
                    time.sleep(1)

                except Exception as e:
                    print(f"  ⚠️ Error on {collection}, page {page}: {e}")
                    break

            if found_products:
                print(f"  ✅ Found products in '{collection}'")
                break

        return all_products


if __name__ == "__main__":
    scraper = WholesaleSolarScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
