"""
Solar Cellz USA Inventory Scraper to Google Sheets
Automatically scrapes product data and updates Google Sheet
"""

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
import json
import os

class SolarCellzScraper:
    def __init__(self, google_sheet_name):
        """Initialize scraper with Google Sheet connection"""
        self.base_url = "https://shop.solarcellzusa.com"
        self.sheet_name = google_sheet_name
        self.sheet = None
        self.connect_to_google_sheet()
        
    def connect_to_google_sheet(self):
        """Connect to Google Sheets using credentials"""
        try:
            # Define the scope
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            
            # Load credentials from environment variable or file
            creds_json = os.environ.get('GOOGLE_CREDENTIALS')
            if creds_json:
                creds_dict = json.loads(creds_json)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            else:
                # Fallback to file-based credentials
                creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
            
            client = gspread.authorize(creds)
            
            # Open the Google Sheet
            self.sheet = client.open(self.sheet_name).sheet1
            print(f"✅ Connected to Google Sheet: {self.sheet_name}")
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheet: {e}")
            raise
    
    def scrape_solar_panels(self):
        """Scrape all solar panel products from Solar Cellz USA"""
        print("🔍 Starting to scrape Solar Cellz USA...")
        
        all_products = []
        page = 1
        
        while True:
            try:
                # Use Shopify's JSON endpoint with pagination
                url = f"{self.base_url}/collections/solar-panels/products.json?limit=250&page={page}"
                
                print(f"📄 Fetching page {page}...")
                response = requests.get(url)
                response.raise_for_status()
                
                data = response.json()
                products = data.get('products', [])
                
                if not products:
                    print(f"✅ Completed scraping. Total products: {len(all_products)}")
                    break
                
                for product in products:
                    # Extract relevant product information
                    for variant in product.get('variants', []):
                        product_info = {
                            'product_id': product['id'],
                            'variant_id': variant['id'],
                            'title': product['title'],
                            'vendor': product.get('vendor', 'N/A'),
                            'product_type': product.get('product_type', 'Solar Panel'),
                            'variant_title': variant.get('title', 'Default'),
                            'sku': variant.get('sku', 'N/A'),
                            'price': float(variant.get('price', 0)),
                            'compare_at_price': float(variant.get('compare_at_price', 0)) if variant.get('compare_at_price') else 0,
                            'available': 'In Stock' if variant.get('available') else 'Out of Stock',
                            'inventory_quantity': variant.get('inventory_quantity', 'N/A'),
                            'weight': variant.get('weight', 'N/A'),
                            'weight_unit': variant.get('weight_unit', 'N/A'),
                            'url': f"{self.base_url}/products/{product['handle']}",
                            'image_url': product.get('images', [{}])[0].get('src', 'N/A') if product.get('images') else 'N/A',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        all_products.append(product_info)
                
                page += 1
                time.sleep(1)  # Be respectful to the server
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Error fetching page {page}: {e}")
                break
            except Exception as e:
                print(f"⚠️ Unexpected error on page {page}: {e}")
                break
        
        return all_products
    
    def update_google_sheet(self, products):
        """Update Google Sheet with scraped product data"""
        print(f"📊 Updating Google Sheet with {len(products)} products...")
        
        try:
            # Clear existing data (keeping headers)
            self.sheet.clear()
            
            # Define headers
            headers = [
                'Product ID',
                'Variant ID',
                'Product Title',
                'Vendor',
                'Type',
                'Variant',
                'SKU',
                'Price',
                'Compare Price',
                'Discount %',
                'Status',
                'Inventory Qty',
                'Weight',
                'Weight Unit',
                'Product URL',
                'Image URL',
                'Last Updated'
            ]
            
            # Prepare data rows
            rows = [headers]
            
            for product in products:
                discount = 0
                if product['compare_at_price'] > 0:
                    discount = round(((product['compare_at_price'] - product['price']) / product['compare_at_price']) * 100, 2)
                
                row = [
                    product['product_id'],
                    product['variant_id'],
                    product['title'],
                    product['vendor'],
                    product['product_type'],
                    product['variant_title'],
                    product['sku'],
                    f"${product['price']:.2f}",
                    f"${product['compare_at_price']:.2f}" if product['compare_at_price'] > 0 else '',
                    f"{discount}%" if discount > 0 else '',
                    product['available'],
                    product['inventory_quantity'],
                    product['weight'],
                    product['weight_unit'],
                    product['url'],
                    product['image_url'],
                    product['last_updated']
                ]
                rows.append(row)
            
            # Update sheet with all data at once (more efficient)
            self.sheet.update('A1', rows)
            
            # Format headers (bold)
            self.sheet.format('A1:Q1', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            print(f"✅ Successfully updated Google Sheet!")
            print(f"📈 Total products: {len(products)}")
            
        except Exception as e:
            print(f"❌ Error updating Google Sheet: {e}")
            raise
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("🌞 Solar Cellz USA Inventory Scraper")
        print("=" * 60)
        
        # Scrape products
        products = self.scrape_solar_panels()
        
        if products:
            # Update Google Sheet
            self.update_google_sheet(products)
            
            # Summary statistics
            in_stock = sum(1 for p in products if p['available'] == 'In Stock')
            out_of_stock = len(products) - in_stock
            avg_price = sum(p['price'] for p in products) / len(products)
            
            print("\n📊 Summary Statistics:")
            print(f"   • Total Products: {len(products)}")
            print(f"   • In Stock: {in_stock}")
            print(f"   • Out of Stock: {out_of_stock}")
            print(f"   • Average Price: ${avg_price:.2f}")
            
        else:
            print("⚠️ No products were scraped.")
        
        print("\n✨ Scraping complete!")
        print("=" * 60)


def main():
    """Main entry point"""
    # Get Google Sheet name from environment variable or use default
    sheet_name = os.environ.get('GOOGLE_SHEET_NAME', 'Solar Cellz USA Inventory')
    
    try:
        scraper = SolarCellzScraper(sheet_name)
        scraper.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
