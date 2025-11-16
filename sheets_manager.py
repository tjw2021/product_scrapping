"""
Google Sheets Manager
Handles multi-tab spreadsheet operations for all distributors
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.credentials import Credentials
import json
import os
import requests
from typing import List, Dict
from datetime import datetime


class SheetsManager:
    """Manages Google Sheets with multiple tabs for different distributors"""

    def __init__(self, sheet_name: str):
        self.sheet_name = sheet_name
        self.client = None
        self.spreadsheet = None
        self.connect()

    def get_replit_credentials(self):
        """Get OAuth credentials from Replit's Google Sheets connector"""
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        x_replit_token = None
        
        if os.environ.get('REPL_IDENTITY'):
            x_replit_token = 'repl ' + os.environ.get('REPL_IDENTITY', '')
        elif os.environ.get('WEB_REPL_RENEWAL'):
            x_replit_token = 'depl ' + os.environ.get('WEB_REPL_RENEWAL', '')
        
        if not hostname or not x_replit_token:
            return None
        
        try:
            response = requests.get(
                f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet',
                headers={
                    'Accept': 'application/json',
                    'X_REPLIT_TOKEN': x_replit_token
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    settings = items[0].get('settings', {})
                    oauth_data = settings.get('oauth', {})
                    credentials_data = oauth_data.get('credentials', {})
                    
                    if credentials_data:
                        return Credentials(
                            token=credentials_data.get('access_token'),
                            refresh_token=credentials_data.get('refresh_token'),
                            token_uri='https://oauth2.googleapis.com/token',
                            client_id=credentials_data.get('client_id'),
                            client_secret=credentials_data.get('client_secret'),
                            scopes=credentials_data.get('scopes')
                        )
                    
                    access_token = settings.get('access_token')
                    if access_token:
                        return Credentials(token=access_token)
                        
        except Exception as e:
            print(f"  ⚠️ Could not get Replit connector credentials: {e}")
        
        return None

    def connect(self):
        """Connect to Google Sheets using credentials"""
        try:
            # Try Replit's Google Sheets integration first
            creds = self.get_replit_credentials()
            
            if creds:
                print("  🔗 Using Replit Google Sheets integration...")
                self.client = gspread.authorize(creds)
            else:
                # Fallback to traditional service account credentials
                print("  🔗 Using service account credentials...")
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]

                creds_json = os.environ.get('GOOGLE_CREDENTIALS')
                if creds_json:
                    creds_dict = json.loads(creds_json)
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                else:
                    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

                self.client = gspread.authorize(creds)
            
            # Try to open the spreadsheet or create it
            try:
                self.spreadsheet = self.client.open(self.sheet_name)
                print(f"✅ Connected to existing Google Sheet: {self.sheet_name}")
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"  📄 Spreadsheet '{self.sheet_name}' not found. Creating new spreadsheet...")
                self.spreadsheet = self.client.create(self.sheet_name)
                print(f"✅ Created and connected to new Google Sheet: {self.sheet_name}")
                print(f"  🔗 Share this sheet with others or view it at: https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}")

        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f"❌ Error: Spreadsheet '{self.sheet_name}' not found.")
            print(f"  💡 Tip: Create a Google Sheet named '{self.sheet_name}' or set GOOGLE_SHEET_NAME environment variable.")
            raise
        except Exception as e:
            print(f"❌ Error connecting to Google Sheet: {e}")
            raise

    def get_or_create_worksheet(self, worksheet_name: str, rows: int = 1000, cols: int = 20):
        """Get existing worksheet or create new one"""
        try:
            worksheet = self.spreadsheet.worksheet(worksheet_name)
            print(f"  📄 Using existing worksheet: {worksheet_name}")
            return worksheet
        except gspread.exceptions.WorksheetNotFound:
            print(f"  📄 Creating new worksheet: {worksheet_name}")
            worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=rows, cols=cols)
            return worksheet

    def update_distributor_tab(self, distributor_name: str, products: List[Dict]):
        """Update a distributor's tab with product data"""
        print(f"\n📊 Updating {distributor_name} tab with {len(products)} products...")

        if not products:
            print(f"  ⚠️ No products to update for {distributor_name}")
            return

        try:
            worksheet = self.get_or_create_worksheet(distributor_name)
            worksheet.clear()

            # Define headers with new columns (24 total)
            headers = [
                'Distributor',
                'Category',
                'Product Title',
                'Brand',
                'SKU',
                'Wattage/KVA',
                'Primary Voltage',
                'Secondary Voltage',
                'Efficiency',
                'Quantity',
                'Total Price',
                'Price Per Unit',
                'Compare Price',
                'Discount %',
                'Stock Status',
                'Inventory Qty',
                'Location/Warehouse',
                'Dimensions',
                'Domestic Content',
                'Shipping Cost',
                'Product URL',
                'Image URL',
                'Product ID',
                'Last Updated'
            ]

            rows = [headers]

            for product in products:
                # Calculate discount
                discount = 0
                if product.get('compare_price', 0) > 0:
                    discount = round(
                        ((product['compare_price'] - product['price']) / product['compare_price']) * 100,
                        2
                    )

                # Get quantity and calculate per-unit price
                quantity = product.get('quantity', 1)
                total_price = product.get('price', 0)
                price_per_unit = product.get('price_per_unit', total_price)

                # Get voltage specs from product specs
                primary_voltage = product.get('specs', {}).get('primary_voltage', 'N/A')
                secondary_voltage = product.get('specs', {}).get('secondary_voltage', 'N/A')
                
                # Get new fields: location, dimensions, and domestic content
                location = product.get('specs', {}).get('location', 'N/A')
                dimensions = product.get('specs', {}).get('dimensions', 'N/A')
                domestic_content = product.get('specs', {}).get('domestic_content', 'N/A')
                
                row = [
                    product.get('distributor', 'N/A'),
                    product.get('category', 'N/A'),
                    product.get('title', 'N/A'),
                    product.get('brand', 'N/A'),
                    product.get('sku', 'N/A'),
                    product.get('wattage', 'N/A'),
                    primary_voltage,
                    secondary_voltage,
                    product.get('efficiency', 'N/A'),
                    quantity if quantity > 1 else '',
                    f"${total_price:.2f}",
                    f"${price_per_unit:.2f}" if quantity > 1 else '',
                    f"${product.get('compare_price', 0):.2f}" if product.get('compare_price', 0) > 0 else '',
                    f"{discount}%" if discount > 0 else '',
                    product.get('stock_status', 'Unknown'),
                    product.get('inventory_qty', 'N/A'),
                    location,
                    dimensions,
                    domestic_content,
                    product.get('shipping_cost', 'N/A'),
                    product.get('product_url', 'N/A'),
                    product.get('image_url', 'N/A'),
                    product.get('product_id', 'N/A'),
                    product.get('last_updated', '')
                ]
                rows.append(row)

            # Update sheet with all data
            worksheet.update('A1', rows, value_input_option='USER_ENTERED')

            # Format headers (now 24 columns: A to X)
            worksheet.format('A1:X1', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.2, "green": 0.5, "blue": 0.8},
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })

            # Freeze header row
            worksheet.freeze(rows=1)
            
            # Auto-resize columns for better readability
            worksheet.columns_auto_resize(0, len(headers) - 1)

            print(f"  ✅ Successfully updated {distributor_name} tab with enhanced data")

        except Exception as e:
            print(f"  ❌ Error updating {distributor_name} tab: {e}")

    def create_comparison_tab(self, all_products: List[Dict]):
        """Create master comparison tab showing best prices"""
        print(f"\n📊 Creating Master Comparison tab...")

        if not all_products:
            print(f"  ⚠️ No products to compare")
            return

        try:
            worksheet = self.get_or_create_worksheet("🏆 Best Prices", rows=2000, cols=20)
            worksheet.clear()

            # Group products by similar titles (fuzzy matching would be better)
            product_groups = {}

            for product in all_products:
                # Create a simplified key based on wattage and brand
                key = f"{product.get('brand', 'unknown')}_{product.get('wattage', 'unknown')}"

                if key not in product_groups:
                    product_groups[key] = []

                product_groups[key].append(product)

            # Find best prices for each product group
            best_deals = []

            for key, products in product_groups.items():
                if not products:
                    continue

                # Sort by price (lowest first)
                sorted_products = sorted(
                    [p for p in products if p.get('price', 0) > 0],
                    key=lambda x: x.get('price', float('inf'))
                )

                if sorted_products:
                    best_deal = sorted_products[0]
                    all_prices = [p for p in sorted_products if p.get('stock_status') == 'In Stock']

                    best_deal['competitors_count'] = len(all_prices)
                    best_deal['price_range'] = f"${min(p['price'] for p in all_prices):.2f} - ${max(p['price'] for p in all_prices):.2f}" if len(all_prices) > 1 else f"${best_deal['price']:.2f}"

                    best_deals.append(best_deal)

            # Sort by price (best deals first)
            best_deals.sort(key=lambda x: x.get('price', float('inf')))

            # Create headers
            headers = [
                '🏆 Rank',
                'Product Title',
                'Brand',
                'Wattage/KVA',
                'Primary Voltage',
                'Secondary Voltage',
                'Efficiency',
                '💰 Best Price',
                '🏪 Best Distributor',
                'Stock Status',
                'Price Range',
                'Competitors',
                'Product URL',
                'Last Updated'
            ]

            rows = [headers]

            for idx, product in enumerate(best_deals, 1):
                # Get voltage specs from product specs
                primary_voltage = product.get('specs', {}).get('primary_voltage', 'N/A')
                secondary_voltage = product.get('specs', {}).get('secondary_voltage', 'N/A')
                
                row = [
                    f"#{idx}",
                    product.get('title', 'N/A'),
                    product.get('brand', 'N/A'),
                    product.get('wattage', 'N/A'),
                    primary_voltage,
                    secondary_voltage,
                    product.get('efficiency', 'N/A'),
                    f"${product.get('price', 0):.2f}",
                    product.get('distributor', 'N/A'),
                    product.get('stock_status', 'Unknown'),
                    product.get('price_range', 'N/A'),
                    product.get('competitors_count', 0),
                    product.get('product_url', 'N/A'),
                    product.get('last_updated', '')
                ]
                rows.append(row)

            # Update sheet
            worksheet.update('A1', rows, value_input_option='USER_ENTERED')

            # Format headers (now 14 columns: A to N)
            worksheet.format('A1:N1', {
                "textFormat": {"bold": True, "fontSize": 11},
                "backgroundColor": {"red": 0.85, "green": 0.65, "blue": 0.13},
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })

            # Highlight top 10 deals
            if len(best_deals) >= 10:
                worksheet.format('A2:N11', {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 0.7}
                })

            worksheet.freeze(rows=1)

            print(f"  ✅ Created comparison tab with {len(best_deals)} product groups")

        except Exception as e:
            print(f"  ❌ Error creating comparison tab: {e}")

    def create_summary_tab(self, distributor_stats: Dict):
        """Create summary statistics tab"""
        print(f"\n📊 Creating Summary Statistics tab...")

        try:
            worksheet = self.get_or_create_worksheet("📈 Summary", rows=100, cols=10)
            worksheet.clear()

            rows = [
                ['📊 Solar Inventory Summary Dashboard'],
                ['Last Updated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                [],
                ['Distributor', 'Total Products', 'In Stock', 'Out of Stock', 'Avg Price', 'Min Price', 'Max Price'],
            ]

            for distributor, stats in distributor_stats.items():
                row = [
                    distributor,
                    stats.get('total', 0),
                    stats.get('in_stock', 0),
                    stats.get('out_of_stock', 0),
                    f"${stats.get('avg_price', 0):.2f}",
                    f"${stats.get('min_price', 0):.2f}",
                    f"${stats.get('max_price', 0):.2f}"
                ]
                rows.append(row)

            worksheet.update('A1', rows, value_input_option='USER_ENTERED')

            # Format title
            worksheet.format('A1', {
                "textFormat": {"bold": True, "fontSize": 14},
                "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.7},
                "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })

            # Format headers
            worksheet.format('A4:G4', {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })

            print(f"  ✅ Created summary tab")

        except Exception as e:
            print(f"  ❌ Error creating summary tab: {e}")
