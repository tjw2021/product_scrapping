"""
Giga Energy Scraper  
Scrapes transformers from gigaenergy.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import time
import re
import json


class GigaEnergyScraper(BaseScraper):
    """Scraper for Giga Energy transformers"""

    def __init__(self):
        super().__init__("Giga Energy")
        self.base_url = "https://www.gigaenergy.com"
        self.shop_url = f"{self.base_url}/shop"

    def scrape_products(self):
        """Scrape all transformer products from Giga Energy"""
        all_products = []
        page = 1
        
        print(f"  📂 Scraping transformers from Giga Energy")

        while page <= 20:  # Max 20 pages to prevent infinite loops
            try:
                # Giga Energy uses pagination with page parameter
                url = f"{self.shop_url}?1cec0fbe_page={page}" if page > 1 else self.shop_url
                
                print(f"    📄 Page {page}...")
                response = self.make_request(url, timeout=15)

                if not response:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find product items - Webflow typically uses specific structures
                product_items = soup.find_all('a', href=lambda x: x and '/shop/' in x if x else False)
                
                if not product_items or len(product_items) == 0:
                    if page == 1:
                        print(f"    ⚠️ No products found on page 1")
                    print(f"    ✅ Completed scraping: {len(all_products)} products")
                    break

                found_products_on_page = 0
                
                for item in product_items:
                    try:
                        # Get product URL
                        product_url = item.get('href', '')
                        if not product_url or product_url == '#':
                            continue
                            
                        if not product_url.startswith('http'):
                            product_url = f"{self.base_url}{product_url}"
                        
                        # Extract product title
                        title_elem = item.find(['h3', 'h2', 'h4', 'div'], class_=lambda x: x and any(t in x.lower() for t in ['title', 'name', 'product']) if x else False)
                        if not title_elem:
                            # Try any string content
                            title_texts = item.find_all(string=lambda x: x and 'phase' in x.lower() and 'transformer' in x.lower() if x else False)
                            title = title_texts[0].strip() if title_texts else None
                        else:
                            title = title_elem.get_text(strip=True)
                        
                        if not title or title == '':
                            continue
                        
                        # Extract KVA rating (e.g., "1500" from title or data attributes)
                        kva_match = re.search(r'(\d+)\s*kva', str(item), re.IGNORECASE)
                        if kva_match:
                            kva = f"{kva_match.group(1)} KVA"
                        else:
                            # Try to find in title
                            kva = self.extract_kva(title, {})
                        
                        # Extract price
                        price_elem = item.find(['div', 'span'], string=lambda x: x and '$' in x if x else False)
                        if not price_elem:
                            price_elem = item.find(['div', 'span'], class_=lambda x: x and 'price' in x.lower() if x else False)
                        
                        price = 0.0
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                            price = float(price_match.group(1).replace(',', '')) if price_match else 0.0
                        
                        # Extract voltage info if available
                        voltage_info = {}
                        high_voltage_elem = item.find(string=lambda x: x and 'high voltage' in x.lower() if x else False)
                        low_voltage_elem = item.find(string=lambda x: x and 'low voltage' in x.lower() if x else False)
                        
                        # Extract image
                        img_elem = item.find('img')
                        image_url = 'N/A'
                        if img_elem:
                            image_url = img_elem.get('src', 'N/A')
                            if image_url and not image_url.startswith('http'):
                                if image_url.startswith('//'):
                                    image_url = f"https:{image_url}"
                                else:
                                    image_url = f"{self.base_url}{image_url}"
                        
                        # Stock status - check for "in stock" indicator
                        stock_status = 'In Stock'  # Assume in stock if listed
                        stock_elem = item.find(string=lambda x: x and ('out of stock' in x.lower() or 'sold out' in x.lower()) if x else False)
                        if stock_elem:
                            stock_status = 'Out of Stock'
                        
                        standardized_product = self.get_standardized_product(
                            product_id='N/A',
                            sku='N/A',
                            title=title,
                            brand='Giga Energy',
                            wattage=kva,  # Use KVA instead of wattage for transformers
                            efficiency='N/A',
                            price=price,
                            compare_price=0,
                            stock_status=stock_status,
                            inventory_qty='N/A',
                            shipping_cost='Contact for Quote',
                            product_url=product_url,
                            image_url=image_url,
                            specs={
                                'product_type': 'Transformer',
                                'kva': kva if kva != 'N/A' else None
                            }
                        )

                        all_products.append(standardized_product)
                        found_products_on_page += 1

                    except Exception as e:
                        print(f"      ⚠️ Error parsing product: {e}")
                        continue

                if found_products_on_page == 0:
                    # No new products found on this page
                    print(f"    ✅ Completed scraping: {len(all_products)} products")
                    break

                page += 1
                time.sleep(2)  # Be respectful with scraping

            except Exception as e:
                print(f"    ❌ Error on page {page}: {e}")
                break

        return all_products


if __name__ == "__main__":
    scraper = GigaEnergyScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
