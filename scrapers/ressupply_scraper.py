"""
RES Supply Scraper
Scrapes products from ressupply.com
Uses HTML parsing since no public API is available
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import time
import re


class RessupplyScraper(BaseScraper):
    """Scraper for RES Supply (ressupply.com)"""

    def __init__(self):
        super().__init__("RES Supply")
        self.base_url = "https://ressupply.com"
        self.categories = [
            "/solar-panels",
            "/solar-panel-pallets"
        ]

    def scrape_products(self):
        """Scrape all solar panel products from RES Supply"""
        all_products = []
        
        for category in self.categories:
            print(f"  📂 Scraping category: {category}")
            category_products = self.scrape_category(category)
            all_products.extend(category_products)
            time.sleep(2)  # Be respectful to the server

        return all_products

    def scrape_category(self, category_url):
        """Scrape all products from a specific category"""
        products = []
        page = 1
        
        while True:
            # Construct page URL (OpenCart uses ?page= query parameter)
            if page == 1:
                url = f"{self.base_url}{category_url}"
            else:
                url = f"{self.base_url}{category_url}?page={page}"
            
            print(f"    📄 Fetching page {page}...")
            response = self.make_request(url)
            
            if not response:
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all product containers
            product_containers = soup.find_all('div', class_='product-layout')
            
            if not product_containers:
                print(f"    ✅ No more products found. Processed {len(products)} products from this category.")
                break
            
            for container in product_containers:
                try:
                    product = self.extract_product_data(container)
                    if product:
                        products.append(product)
                except Exception as e:
                    print(f"    ⚠️ Error extracting product: {e}")
                    continue
            
            # Check if there's a next page
            next_page = soup.find('a', text='>')
            if not next_page:
                print(f"    ✅ Completed category. Total products: {len(products)}")
                break
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        return products

    def extract_product_data(self, container):
        """Extract product data from a product container"""
        try:
            # Extract product name and URL
            name_element = container.find('div', class_='name')
            if not name_element or not name_element.find('a'):
                return None
            
            link = name_element.find('a')
            title = link.get_text(strip=True)
            product_url = link.get('href', '')
            
            # Extract price
            price_container = container.find('div', class_='price-row')
            price = 0.0
            if price_container:
                price_text = price_container.get_text(strip=True)
                price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract description (contains specs)
            description_element = container.find('div', class_='description')
            description = description_element.get_text(strip=True) if description_element else ''
            
            # Extract image URL
            image_element = container.find('div', class_='image')
            image_url = 'N/A'
            if image_element and image_element.find('img'):
                image_url = image_element.find('img').get('src', 'N/A')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.base_url}/{image_url}"
            
            # Extract minimum quantity from data-min attribute
            qty_input = container.find('input', class_='quantity')
            min_qty = qty_input.get('data-min', '1') if qty_input else '1'
            
            # Extract wattage from title or description
            wattage = self.extract_wattage(f"{title} {description}")
            
            # Extract efficiency if available
            efficiency = self.extract_efficiency(f"{title} {description}", {})
            
            # Extract brand from title (usually first word or part before model number)
            brand = self.extract_brand(title)
            
            # Parse specs from description
            specs = self.parse_specs(description)
            
            # Determine stock status (if min qty exists, assume in stock)
            stock_status = 'In Stock' if int(min_qty) > 0 else 'Unknown'
            
            # Generate product ID from URL
            product_id = product_url.split('/')[-1] if product_url else 'N/A'
            
            standardized_product = self.get_standardized_product(
                product_id=product_id,
                sku=product_id,  # RES Supply doesn't expose SKU in listings
                title=title,
                brand=brand,
                wattage=wattage,
                efficiency=efficiency,
                price=price,
                compare_price=0.0,  # No compare prices visible in listings
                stock_status=stock_status,
                inventory_qty=f"Min Order: {min_qty}",
                shipping_cost='Calculated at Checkout',
                product_url=product_url,
                image_url=image_url,
                specs=specs
            )
            
            return standardized_product
            
        except Exception as e:
            print(f"    ⚠️ Error parsing product: {e}")
            return None

    def extract_brand(self, title):
        """Extract brand name from product title"""
        # Common solar panel brands
        brands = [
            'Jinko', 'JA Solar', 'REC', 'HT-SAAE', 'Canadian Solar', 
            'Longi', 'Trina', 'SunPower', 'Q CELLS', 'Panasonic',
            'Silfab', 'Aptos', 'Maxeon', 'Mission Solar'
        ]
        
        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
        
        # If no known brand found, try to extract first word
        first_word = title.split()[0] if title.split() else 'N/A'
        return first_word

    def parse_specs(self, description):
        """Parse specifications from product description"""
        specs = {}
        
        # Extract cell count (e.g., "132 Half Cell")
        cell_match = re.search(r'(\d+)\s+(?:Half\s+)?Cell', description, re.IGNORECASE)
        if cell_match:
            specs['cells'] = cell_match.group(0)
        
        # Extract frame info (e.g., "30mm Black Frame")
        frame_match = re.search(r'(\d+mm)\s+(\w+)\s+Frame', description, re.IGNORECASE)
        if frame_match:
            specs['frame'] = frame_match.group(0)
        
        # Extract cell type (e.g., "Mono PERC")
        if 'Mono PERC' in description:
            specs['cell_type'] = 'Mono PERC'
        elif 'Monocrystalline' in description:
            specs['cell_type'] = 'Monocrystalline'
        elif 'Polycrystalline' in description:
            specs['cell_type'] = 'Polycrystalline'
        
        # Extract voltage rating (e.g., "1500VDC")
        voltage_match = re.search(r'(\d+)VDC', description)
        if voltage_match:
            specs['voltage'] = f"{voltage_match.group(1)}VDC"
        
        # Extract connector type (e.g., "MC4")
        if 'MC4' in description:
            specs['connector'] = 'MC4'
        
        # Extract PTC rating (e.g., "377.8W PTC")
        ptc_match = re.search(r'([\d.]+)W\s+PTC', description)
        if ptc_match:
            specs['ptc_rating'] = f"{ptc_match.group(1)}W"
        
        # Check if bifacial
        if 'Bifacial' in description:
            specs['bifacial'] = 'Yes'
        
        return specs


if __name__ == "__main__":
    scraper = RessupplyScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
    
    # Show sample product
    if products:
        print("\nSample product:")
        print(f"Title: {products[0]['title']}")
        print(f"Price: ${products[0]['price']}")
        print(f"Brand: {products[0]['brand']}")
        print(f"Wattage: {products[0]['wattage']}")
