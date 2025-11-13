"""
Main Solar Inventory Automation System
Orchestrates all scrapers, tracking, and reporting
"""

from scrapers import (
    SolarCellzScraper,
    SolarElectricSupplyScraper,
    WholesaleSolarScraper,
    AltEScraper
)
from sheets_manager import SheetsManager
from price_tracker import PriceTracker
from alerting import AlertingSystem
from config import Config
from datetime import datetime
from typing import List, Dict


class SolarInventorySystem:
    """Main system orchestrator"""

    def __init__(self):
        self.config = Config()
        self.scrapers = self.initialize_scrapers()
        self.sheets_manager = None
        self.price_tracker = None
        self.alerting = None

    def initialize_scrapers(self) -> Dict:
        """Initialize all distributor scrapers"""
        all_scrapers = {
            'solar_cellz': SolarCellzScraper(),
            'solar_electric': SolarElectricSupplyScraper(),
            'wholesale_solar': WholesaleSolarScraper(),
            'alte': AltEScraper()
        }

        # Filter based on config
        enabled_scrapers = {}
        for key, scraper in all_scrapers.items():
            if key in self.config.DISTRIBUTORS_TO_SCRAPE:
                enabled_scrapers[key] = scraper

        return enabled_scrapers

    def run_scraping(self) -> Dict[str, List[Dict]]:
        """Run all enabled scrapers"""
        print("\n" + "="*60)
        print("🌞 SOLAR INVENTORY AUTOMATION SYSTEM")
        print("="*60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scraping {len(self.scrapers)} distributor(s)")
        print("="*60)

        all_products = {}

        for key, scraper in self.scrapers.items():
            try:
                products = scraper.run()
                all_products[scraper.distributor_name] = products
            except Exception as e:
                print(f"❌ Error scraping {scraper.distributor_name}: {e}")
                all_products[scraper.distributor_name] = []

        return all_products

    def update_sheets(self, all_products: Dict[str, List[Dict]]):
        """Update Google Sheets with all data"""
        print("\n" + "="*60)
        print("📊 UPDATING GOOGLE SHEETS")
        print("="*60)

        try:
            self.sheets_manager = SheetsManager(self.config.GOOGLE_SHEET_NAME)

            # Update individual distributor tabs
            for distributor_name, products in all_products.items():
                self.sheets_manager.update_distributor_tab(distributor_name, products)

            # Create comparison tab
            if self.config.CREATE_COMPARISON_TAB:
                flat_products = [p for products in all_products.values() for p in products]
                self.sheets_manager.create_comparison_tab(flat_products)

            # Create summary tab
            if self.config.CREATE_SUMMARY_TAB:
                stats = self.calculate_statistics(all_products)
                self.sheets_manager.create_summary_tab(stats)

            print("\n✅ All sheets updated successfully!")

        except Exception as e:
            print(f"\n❌ Error updating sheets: {e}")

    def track_prices_and_alert(self, all_products: Dict[str, List[Dict]]):
        """Track price changes and send alerts"""
        if not self.config.ENABLE_PRICE_TRACKING:
            return

        print("\n" + "="*60)
        print("📈 PRICE TRACKING & ALERTS")
        print("="*60)

        try:
            self.price_tracker = PriceTracker(self.config.PRICE_HISTORY_FILE)

            # Flatten all products
            flat_products = [p for products in all_products.values() for p in products]

            # Track changes
            changes = self.price_tracker.track_products(flat_products)

            print(f"\n📊 Changes Detected:")
            print(f"  • Price Drops: {len(changes['price_drops'])}")
            print(f"  • Price Increases: {len(changes['price_increases'])}")
            print(f"  • New Products: {len(changes['new_products'])}")
            print(f"  • Stock Changes: {len(changes['stock_changes'])}")

            # Send alerts if enabled
            if self.config.ENABLE_EMAIL_ALERTS:
                self.alerting = AlertingSystem(self.config.get_smtp_config())

                if changes['price_drops']:
                    print(f"\n📧 Sending price drop alert...")
                    self.alerting.send_price_drop_alert(changes['price_drops'])

                if changes['new_products'] and self.config.SEND_NEW_PRODUCT_ALERTS:
                    print(f"📧 Sending new products alert...")
                    self.alerting.send_new_products_alert(changes['new_products'])

                if changes['stock_changes'] and self.config.SEND_STOCK_ALERTS:
                    print(f"📧 Sending stock change alert...")
                    self.alerting.send_stock_change_alert(changes['stock_changes'])

        except Exception as e:
            print(f"\n❌ Error in price tracking: {e}")

    def calculate_statistics(self, all_products: Dict[str, List[Dict]]) -> Dict:
        """Calculate statistics for each distributor"""
        stats = {}

        for distributor_name, products in all_products.items():
            if not products:
                stats[distributor_name] = {
                    'total': 0,
                    'in_stock': 0,
                    'out_of_stock': 0,
                    'avg_price': 0,
                    'min_price': 0,
                    'max_price': 0
                }
                continue

            prices = [p['price'] for p in products if p.get('price', 0) > 0]

            stats[distributor_name] = {
                'total': len(products),
                'in_stock': sum(1 for p in products if p.get('stock_status') == 'In Stock'),
                'out_of_stock': sum(1 for p in products if p.get('stock_status') != 'In Stock'),
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0
            }

        return stats

    def print_summary(self, all_products: Dict[str, List[Dict]]):
        """Print execution summary"""
        print("\n" + "="*60)
        print("✨ EXECUTION SUMMARY")
        print("="*60)

        total_products = sum(len(products) for products in all_products.values())

        print(f"\n📦 Total Products Scraped: {total_products}")
        print(f"\nBreakdown by Distributor:")

        for distributor_name, products in all_products.items():
            in_stock = sum(1 for p in products if p.get('stock_status') == 'In Stock')
            print(f"  • {distributor_name}: {len(products)} products ({in_stock} in stock)")

        print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

    def run(self):
        """Main execution method"""
        # Print configuration
        self.config.print_config()

        # Run scraping
        all_products = self.run_scraping()

        # Update Google Sheets
        self.update_sheets(all_products)

        # Track prices and send alerts
        self.track_prices_and_alert(all_products)

        # Print summary
        self.print_summary(all_products)


def main():
    """Entry point"""
    try:
        system = SolarInventorySystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
