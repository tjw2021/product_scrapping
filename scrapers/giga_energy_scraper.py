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


class GigaEnergyScraper(BaseScraper):
    """Scraper for Giga Energy transformers"""

    def __init__(self):
        super().__init__("Giga Energy")
        self.base_url = "https://www.gigaenergy.com"
        self.shop_url = f"{self.base_url}/shop"

    def parse_voltages_from_title(self, title):
        """
        Parse primary and secondary voltages from title.
        Example: "1500 kVA 3-Phase Padmount Transformer: 20780 D to 480 Y/ 277"
        Returns: (primary_voltage, secondary_voltage)
        """
        primary_voltage = 'N/A'
        secondary_voltage = 'N/A'
        
        # Pattern: "20780 D to 480 Y/ 277" or similar
        voltage_pattern = r'(\d+)\s*([DY])\s*to\s*(\d+)\s*([DY])(?:/\s*(\d+))?'
        match = re.search(voltage_pattern, title, re.IGNORECASE)
        
        if match:
            primary_v = match.group(1)
            primary_type = match.group(2).upper()
            secondary_v = match.group(3)
            secondary_type = match.group(4).upper()
            secondary_neutral = match.group(5) if match.group(5) else ''
            
            primary_voltage = f"{primary_v}V {primary_type}"
            if secondary_neutral:
                secondary_voltage = f"{secondary_v}V {secondary_type}/{secondary_neutral}V"
            else:
                secondary_voltage = f"{secondary_v}V {secondary_type}"
        
        return primary_voltage, secondary_voltage

    def scrape_product_details(self, product_url):
        """
        Scrape detailed product information from individual product page.
        Returns: dict with price, KVA, voltages, description, etc.
        """
        try:
            response = self.make_request(product_url, timeout=15)
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title (full product description)
            title_elem = soup.find('title')
            title = title_elem.text.split('・')[0].strip() if title_elem else 'N/A'
            
            # Extract price from shop_price-number class
            price_elem = soup.find('span', class_='shop_price-number')
            price = 0.0
            if price_elem:
                price_text = price_elem.get_text(strip=True).replace(',', '')
                try:
                    price = float(price_text)
                except ValueError:
                    price = 0.0
            
            # Extract KVA rating from input field
            kva_input = soup.find('input', {'name': 'kva_rating'})
            kva = 'N/A'
            if kva_input and kva_input.get('value'):
                kva = f"{kva_input.get('value')} KVA"
            else:
                # Fallback: parse from title
                kva_match = re.search(r'(\d+)\s*kVA', title, re.IGNORECASE)
                if kva_match:
                    kva = f"{kva_match.group(1)} KVA"
            
            # Parse voltages from title
            primary_voltage, secondary_voltage = self.parse_voltages_from_title(title)
            
            # Extract image
            img_elem = soup.find('img', src=lambda x: x and 'cdn.prod.website-files.com' in x if x else False)
            image_url = 'N/A'
            if img_elem:
                image_url = img_elem.get('src', 'N/A')
                if image_url and not image_url.startswith('http'):
                    if image_url.startswith('//'):
                        image_url = f"https:{image_url}"
                    else:
                        image_url = f"{self.base_url}{image_url}"
            
            # Create description from title
            description = title
            
            return {
                'title': title,
                'price': price,
                'kva': kva,
                'primary_voltage': primary_voltage,
                'secondary_voltage': secondary_voltage,
                'description': description,
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"      ⚠️ Error scraping product details: {e}")
            return None

    def scrape_products(self):
        """Scrape all transformer products from Giga Energy"""
        all_products = []
        page = 1
        product_urls = set()
        
        print(f"  📂 Scraping transformers from Giga Energy")

        # Step 1: Collect all product URLs from listing pages
        while page <= 20:
            try:
                url = f"{self.shop_url}?1cec0fbe_page={page}" if page > 1 else self.shop_url
                
                print(f"    📄 Page {page}...")
                response = self.make_request(url, timeout=15)

                if not response:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find product links
                product_items = soup.find_all('a', href=lambda x: x and '/shop/' in x if x else False)
                
                if not product_items or len(product_items) == 0:
                    print(f"    ✅ Completed URL collection: {len(product_urls)} unique products")
                    break

                found_new = False
                for item in product_items:
                    product_url = item.get('href', '')
                    if not product_url or product_url == '#':
                        continue
                        
                    if not product_url.startswith('http'):
                        product_url = f"{self.base_url}{product_url}"
                    
                    # Only add unique URLs
                    if product_url not in product_urls and '/shop/' in product_url:
                        product_urls.add(product_url)
                        found_new = True

                if not found_new:
                    print(f"    ✅ Completed URL collection: {len(product_urls)} unique products")
                    break

                page += 1
                time.sleep(1)

            except Exception as e:
                print(f"    ❌ Error on page {page}: {e}")
                break
        
        # Step 2: Scrape details from each product page
        print(f"  📋 Scraping details for {len(product_urls)} products...")
        for i, product_url in enumerate(product_urls, 1):
            try:
                print(f"    🔍 Product {i}/{len(product_urls)}...", end='\r')
                
                details = self.scrape_product_details(product_url)
                if not details:
                    continue
                
                # Create standardized product
                standardized_product = self.get_standardized_product(
                    product_id='N/A',
                    sku='N/A',
                    title=details['title'],
                    brand='Giga Energy',
                    wattage=details['kva'],
                    efficiency='N/A',
                    price=details['price'],
                    compare_price=0,
                    stock_status='In Stock',
                    inventory_qty='N/A',
                    shipping_cost='Contact for Quote',
                    product_url=product_url,
                    image_url=details['image_url'],
                    description=details['description'],
                    specs={
                        'product_type': 'Transformer',
                        'kva': details['kva'],
                        'primary_voltage': details['primary_voltage'],
                        'secondary_voltage': details['secondary_voltage']
                    }
                )

                all_products.append(standardized_product)
                time.sleep(1.5)  # Be respectful with scraping

            except Exception as e:
                print(f"\n      ⚠️ Error scraping {product_url}: {e}")
                continue
        
        print(f"\n    ✅ Successfully scraped {len(all_products)} products with full details")
        return all_products


if __name__ == "__main__":
    scraper = GigaEnergyScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
    if products:
        print("\nSample product:")
        p = products[0]
        print(f"  Title: {p.get('title')}")
        print(f"  Price: ${p.get('price', 0):,.2f}")
        print(f"  KVA: {p.get('wattage')}")
        print(f"  Primary Voltage: {p.get('specs', {}).get('primary_voltage')}")
        print(f"  Secondary Voltage: {p.get('specs', {}).get('secondary_voltage')}")
