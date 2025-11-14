"""
Solar Electric Supply Scraper
Scrapes products from solarelectricsupply.com
Uses HTML parsing since the site uses custom platform (not Shopify)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from bs4 import BeautifulSoup
import time
import re


class SolarElectricSupplyScraper(BaseScraper):
    """Scraper for Solar Electric Supply"""

    def __init__(self):
        super().__init__("Solar Electric Supply")
        self.base_url = "https://www.solarelectricsupply.com"

    def scrape_products(self):
        """Scrape solar panel products from Solar Electric Supply"""
        all_products = []
        
        # Main solar panel listing page with product tables
        print(f"  📂 Scraping main solar panel catalog...")
        url = f"{self.base_url}/solar-panel"
        
        response = self.make_request(url)
        if not response:
            print(f"  ❌ Failed to fetch main catalog page")
            return all_products
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables containing product information
        tables = soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            try:
                products_from_table = self.parse_product_table(table)
                all_products.extend(products_from_table)
                if products_from_table:
                    print(f"    ✅ Extracted {len(products_from_table)} products from table {table_idx + 1}")
            except Exception as e:
                print(f"    ⚠️ Error parsing table {table_idx + 1}: {e}")
                continue
        
        return all_products

    def parse_product_table(self, table):
        """Parse a product table and extract product information"""
        products = []
        
        # Find all rows in the table
        rows = table.find_all('tr')
        
        # Skip header row, process data rows
        for row in rows[1:]:  # Skip first row (usually headers)
            try:
                cells = row.find_all('td')
                if len(cells) < 4:  # Need at least manufacturer, wattage, model info
                    continue
                
                product = self.extract_product_from_row(cells)
                if product:
                    products.append(product)
                    
            except Exception as e:
                continue
        
        return products

    def extract_product_from_row(self, cells):
        """Extract product data from table row cells"""
        try:
            # Typical table structure:
            # [Manufacturer, STC Wattage, PTC, Model Info/Link, Frame Color, Cell Type, Origin, Manufactured, Availability]
            
            if len(cells) < 4:
                return None
            
            # Extract manufacturer/brand (usually first cell)
            brand = cells[0].get_text(strip=True)
            if not brand or len(brand) > 50:  # Skip invalid brands
                return None
            
            # Extract wattage (usually second cell)
            wattage_text = cells[1].get_text(strip=True)
            wattage_match = re.search(r'(\d+)\s*[Ww]', wattage_text)
            wattage = f"{wattage_match.group(1)}W" if wattage_match else 'N/A'
            
            # Extract PTC rating (usually third cell)
            ptc_text = cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A'
            
            # Extract model info and product URL (usually fourth cell with link)
            model_cell = cells[3] if len(cells) > 3 else cells[0]
            model_link = model_cell.find('a')
            
            if not model_link:
                return None
                
            title = model_link.get_text(strip=True)
            product_url = model_link.get('href', '')
            
            # Make URL absolute
            if product_url and not product_url.startswith('http'):
                product_url = f"{self.base_url}{product_url}" if product_url.startswith('/') else f"{self.base_url}/{product_url}"
            
            # Extract frame color (usually fifth cell)
            frame_color = cells[4].get_text(strip=True) if len(cells) > 4 else 'N/A'
            
            # Extract cell type (usually sixth cell)
            cell_type = cells[5].get_text(strip=True) if len(cells) > 5 else 'N/A'
            
            # Extract origin (usually seventh cell)
            origin = cells[6].get_text(strip=True) if len(cells) > 6 else 'N/A'
            
            # Extract manufacturing location (usually eighth cell)
            manufactured = cells[7].get_text(strip=True) if len(cells) > 7 else 'N/A'
            
            # Extract availability status (usually ninth cell)
            availability = cells[8].get_text(strip=True) if len(cells) > 8 else 'Unknown'
            stock_status = 'In Stock' if 'IN STOCK' in availability.upper() else 'Contact for Availability'
            
            # Build specs dictionary
            specs = {
                'ptc_rating': ptc_text,
                'frame_color': frame_color,
                'cell_type': cell_type,
                'origin': origin,
                'manufactured': manufactured
            }
            
            # Extract SKU from URL or model name
            sku = product_url.split('/')[-1] if product_url else title.replace(' ', '-').lower()
            
            # Generate product ID from SKU
            product_id = sku
            
            standardized_product = self.get_standardized_product(
                product_id=product_id,
                sku=sku,
                title=title,
                brand=brand,
                wattage=wattage,
                efficiency='N/A',  # Not provided in table listing
                price=0.0,  # Wholesale pricing - contact required
                compare_price=0.0,
                stock_status=stock_status,
                inventory_qty='Contact for Quote',
                shipping_cost='Min 8 panels for freight',
                product_url=product_url,
                image_url='N/A',  # Would need to fetch individual product pages
                specs=specs
            )
            
            return standardized_product
            
        except Exception as e:
            return None


if __name__ == "__main__":
    scraper = SolarElectricSupplyScraper()
    products = scraper.run()
    print(f"\nScraped {len(products)} products")
    
    # Show sample products
    if products:
        print("\nSample products:")
        for i, product in enumerate(products[:3]):
            print(f"\n{i+1}. {product['title']}")
            print(f"   Brand: {product['brand']}")
            print(f"   Wattage: {product['wattage']}")
            print(f"   Stock: {product['stock_status']}")
            print(f"   URL: {product['product_url']}")
