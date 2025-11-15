"""
Essential Parts Scraper
Scrapes transformers and switches from essentialparts.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import time
import re


class EssentialPartsScraper(BaseScraper):
    """Scraper for Essential Parts"""

    def __init__(self):
        super().__init__("Essential Parts")
        self.base_url = "https://essentialparts.com"
        # Collections to scrape
        self.collections = [
            'transformers',
            'switches'
        ]

    def scrape_collection(self, collection_name):
        """Scrape products from a specific collection"""
        products = []
        page = 1
        
        print(f"  📂 Scraping collection: {collection_name}")

        while page <= 20:  # Limit to 20 pages per collection
            try:
                url = f"{self.base_url}/collections/{collection_name}?page={page}"
                
                print(f"    📄 Page {page}...")
                response = self.make_request(url, timeout=15)

                if not response:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product items (adjust selectors based on actual HTML structure)
                product_items = soup.find_all('div', class_=lambda x: x and 'product' in x.lower() if x else False)
                
                if not product_items:
                    # Try alternative selector
                    product_items = soup.find_all('a', href=lambda x: x and '/products/' in x if x else False)
                
                if not product_items or len(product_items) == 0:
                    if page == 1:
                        print(f"    ⚠️ No products found on page 1 for {collection_name}")
                    print(f"    ✅ Completed {collection_name}: {len(products)} products")
                    break

                for item in product_items:
                    try:
                        # Extract product information from HTML
                        product_link = item.find('a', href=lambda x: x and '/products/' in x if x else False)
                        if not product_link and item.name == 'a':
                            product_link = item
                        
                        if not product_link:
                            continue

                        product_url = product_link.get('href', '')
                        if not product_url.startswith('http'):
                            product_url = f"{self.base_url}{product_url}"
                        
                        # Extract product title
                        title_elem = item.find(['h3', 'h2', 'h4'], class_=lambda x: 'title' in x.lower() if x else False)
                        if not title_elem:
                            title_elem = product_link.find(['span', 'div'], class_=lambda x: 'title' in x.lower() if x else False)
                        
                        title = title_elem.get_text(strip=True) if title_elem else product_link.get('title', 'N/A')
                        
                        if title == 'N/A':
                            continue
                        
                        # Extract price
                        price_elem = item.find(['span', 'div'], class_=lambda x: x and 'price' in x.lower() if x else False)
                        price_text = price_elem.get_text(strip=True) if price_elem else '$0'
                        price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                        price = float(price_match.group(1).replace(',', '')) if price_match else 0.0
                        
                        # Extract image
                        img_elem = item.find('img')
                        image_url = img_elem.get('src', 'N/A') if img_elem else 'N/A'
                        if image_url and image_url.startswith('//'):
                            image_url = f"https:{image_url}"
                        
                        # Extract brand/vendor if available
                        brand_elem = item.find(['span', 'div'], class_=lambda x: x and ('vendor' in x.lower() or 'brand' in x.lower()) if x else False)
                        brand = brand_elem.get_text(strip=True) if brand_elem else 'N/A'
                        
                        # Extract KVA for transformers
                        kva = self.extract_kva(title, {'collection': collection_name})
                        wattage = kva if kva != 'N/A' else self.extract_wattage(title)
                        
                        # Determine stock status
                        stock_status = 'Unknown'
                        if 'sold' in item.get_text().lower() or 'out of stock' in item.get_text().lower():
                            stock_status = 'Out of Stock'
                        elif 'in stock' in item.get_text().lower():
                            stock_status = 'In Stock'
                        
                        standardized_product = self.get_standardized_product(
                            product_id='N/A',
                            sku='N/A',
                            title=title,
                            brand=brand,
                            wattage=wattage,
                            efficiency='N/A',
                            price=price,
                            compare_price=0,
                            stock_status=stock_status,
                            inventory_qty='N/A',
                            shipping_cost='Varies',
                            product_url=product_url,
                            image_url=image_url,
                            specs={
                                'product_type': collection_name.rstrip('s').capitalize(),
                                'collection': collection_name
                            }
                        )

                        products.append(standardized_product)

                    except Exception as e:
                        print(f"      ⚠️ Error parsing product: {e}")
                        continue

                page += 1
                time.sleep(2)  # Be respectful with scraping

            except Exception as e:
                print(f"    ❌ Error on page {page}: {e}")
                break

        return products

    def scrape_products(self):
        """Scrape products from all collections"""
        all_products = []
        
        for collection in self.collections:
            collection_products = self.scrape_collection(collection)
            all_products.extend(collection_products)
            time.sleep(2)

        return all_products


if __name__ == "__main__":
    scraper = EssentialPartsScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
