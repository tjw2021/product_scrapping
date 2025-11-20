"""
Solar Equipment Scraper - Complete System
Main orchestrator for solar equipment scraping with AVL matching and Excel export
"""

import os
import yaml
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from tqdm import tqdm

# Import scrapers
from scrapers import (
    SolarCellzScraper,
    AltEScraper,
    RessupplyScraper,
    USSolarSupplierScraper,
    SolarStoreScraper,
    GigaEnergyScraper,
    EssentialPartsScraper,
    SoligentScraper
)

# Import new modules
from avl_handler import AVLHandler
from spec_sheet_downloader import SpecSheetDownloader
from excel_exporter import ExcelExporter


class SolarEquipmentScraper:
    """Main orchestrator for solar equipment scraping"""

    def __init__(self, config_file: str = 'scraper_config.yaml'):
        """
        Initialize scraper system

        Args:
            config_file: Path to YAML configuration file
        """
        print("\n" + "="*60)
        print("🌞 SOLAR EQUIPMENT SCRAPER SYSTEM")
        print("="*60)

        # Load configuration
        self.config = self.load_config(config_file)

        # Initialize components
        self.scrapers = self.initialize_scrapers()
        self.avl_handler = self.initialize_avl_handler()
        self.spec_downloader = self.initialize_spec_downloader()

        print(f"✅ System initialized with {len(self.scrapers)} active scrapers")
        print("="*60 + "\n")

    def load_config(self, config_file: str) -> Dict:
        """
        Load configuration from YAML file

        Args:
            config_file: Path to config file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_file):
            print(f"⚠️  Config file not found: {config_file}")
            print("Using default configuration")
            return self.get_default_config()

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded configuration from {config_file}")
            return config
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            print("Using default configuration")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            'distributors': {
                'solar_cellz': {'enabled': True},
                'soligent': {'enabled': True},
                'giga_energy': {'enabled': True},
                'alte': {'enabled': True},
                'ressupply': {'enabled': True},
                'us_solar_supplier': {'enabled': True},
                'solar_store': {'enabled': True},
                'essential_parts': {'enabled': False}
            },
            'avl': {
                'enabled': True,
                'thrive_file': 'THRIVE_AVL.xlsx',
                'goodleap_file': 'GOODLEAP_AVL.xlsx'
            },
            'spec_sheets': {
                'enabled': False,
                'output_directory': 'spec_sheets',
                'max_pdfs_per_product': 3,
                'delay_between_downloads': 1.0
            },
            'output': {
                'excel': {
                    'enabled': True,
                    'directory': './output',
                    'filename_pattern': 'solar_equipment_database_{timestamp}.xlsx',
                    'include_summary_sheet': True,
                    'include_domestic_only_sheet': True
                }
            }
        }

    def initialize_scrapers(self) -> Dict:
        """
        Initialize all enabled distributor scrapers

        Returns:
            Dictionary of scraper instances
        """
        scraper_map = {
            'solar_cellz': SolarCellzScraper,
            'soligent': SoligentScraper,
            'giga_energy': GigaEnergyScraper,
            'alte': AltEScraper,
            'ressupply': RessupplyScraper,
            'us_solar_supplier': USSolarSupplierScraper,
            'solar_store': SolarStoreScraper,
            'essential_parts': EssentialPartsScraper
        }

        enabled_scrapers = {}

        distributors_config = self.config.get('distributors', {})

        for key, scraper_class in scraper_map.items():
            dist_config = distributors_config.get(key, {})
            if dist_config.get('enabled', False):
                try:
                    scraper = scraper_class()
                    enabled_scrapers[key] = scraper
                except Exception as e:
                    print(f"⚠️  Failed to initialize {key}: {e}")

        return enabled_scrapers

    def initialize_avl_handler(self) -> Optional[AVLHandler]:
        """
        Initialize AVL handler

        Returns:
            AVLHandler instance or None if disabled
        """
        avl_config = self.config.get('avl', {})

        if not avl_config.get('enabled', False):
            print("⚠️  AVL matching disabled in config")
            return None

        thrive_file = avl_config.get('thrive_file', 'THRIVE_AVL.xlsx')
        goodleap_file = avl_config.get('goodleap_file', 'GOODLEAP_AVL.xlsx')

        return AVLHandler(thrive_file, goodleap_file)

    def initialize_spec_downloader(self) -> Optional[SpecSheetDownloader]:
        """
        Initialize spec sheet downloader

        Returns:
            SpecSheetDownloader instance or None if disabled
        """
        spec_config = self.config.get('spec_sheets', {})

        if not spec_config.get('enabled', False):
            return None

        output_dir = spec_config.get('output_directory', 'spec_sheets')
        return SpecSheetDownloader(output_dir=output_dir)

    def run_scraping(self) -> List[Dict]:
        """
        Run all enabled scrapers

        Returns:
            List of all scraped products
        """
        print("\n" + "="*60)
        print("🔍 SCRAPING PRODUCTS")
        print("="*60)
        print(f"Scraping from {len(self.scrapers)} distributor(s)")
        print("="*60 + "\n")

        all_products = []

        for key, scraper in self.scrapers.items():
            try:
                products = scraper.run()
                all_products.extend(products)
                print(f"  ✅ {scraper.distributor_name}: {len(products)} products")
            except Exception as e:
                print(f"  ❌ Error scraping {scraper.distributor_name}: {e}")

        print(f"\n{'='*60}")
        print(f"✅ Total products scraped: {len(all_products)}")
        print("="*60 + "\n")

        return all_products

    def add_avl_matching(self, products_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add AVL matching columns to products

        Args:
            products_df: Products dataframe

        Returns:
            DataFrame with AVL columns added
        """
        if self.avl_handler is None:
            print("⚠️  AVL handler not initialized, skipping AVL matching")
            return products_df

        print("\n" + "="*60)
        print("📋 AVL MATCHING")
        print("="*60)

        products_df = self.avl_handler.add_avl_columns(products_df)

        print("="*60 + "\n")

        return products_df

    def download_spec_sheets(self, products: List[Dict]):
        """
        Download specification sheets for products

        Args:
            products: List of product dictionaries
        """
        if self.spec_downloader is None:
            return

        print("\n" + "="*60)
        print("📥 DOWNLOADING SPEC SHEETS")
        print("="*60)

        spec_config = self.config.get('spec_sheets', {})
        max_pdfs = spec_config.get('max_pdfs_per_product', 3)
        delay = spec_config.get('delay_between_downloads', 1.0)

        self.spec_downloader.download_for_products_batch(
            products,
            max_pdfs_per_product=max_pdfs,
            delay=delay
        )

        print("="*60 + "\n")

    def export_to_excel(self, products_df: pd.DataFrame):
        """
        Export products to Excel

        Args:
            products_df: Products dataframe
        """
        excel_config = self.config.get('output', {}).get('excel', {})

        if not excel_config.get('enabled', True):
            print("⚠️  Excel export disabled in config")
            return

        print("\n" + "="*60)
        print("📊 EXPORTING TO EXCEL")
        print("="*60)

        # Create output directory
        output_dir = excel_config.get('directory', './output')
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename
        filename_pattern = excel_config.get(
            'filename_pattern',
            'solar_equipment_database_{timestamp}.xlsx'
        )
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = filename_pattern.replace('{timestamp}', timestamp)
        output_path = os.path.join(output_dir, filename)

        # Export
        exporter = ExcelExporter(output_path)
        exporter.export_by_category(
            products_df,
            include_summary=excel_config.get('include_summary_sheet', True),
            include_domestic_only=excel_config.get('include_domestic_only_sheet', True)
        )

        print("="*60 + "\n")

        return output_path

    def print_summary(self, products_df: pd.DataFrame):
        """
        Print execution summary

        Args:
            products_df: Products dataframe
        """
        print("\n" + "="*60)
        print("✨ EXECUTION SUMMARY")
        print("="*60)

        print(f"\n📦 Total Products: {len(products_df)}")

        # Category breakdown
        if 'category' in products_df.columns:
            print(f"\n📊 By Category:")
            category_counts = products_df['category'].value_counts()
            for category, count in category_counts.items():
                print(f"  • {category}: {count} products")

        # Stock status breakdown
        if 'stock_status' in products_df.columns:
            print(f"\n📦 By Stock Status:")
            in_stock = len(products_df[products_df['stock_status'] == 'In Stock'])
            print(f"  • In Stock: {in_stock} products")
            print(f"  • Other: {len(products_df) - in_stock} products")

        # AVL breakdown
        if 'on_any_avl' in products_df.columns:
            print(f"\n📋 AVL Approval:")
            print(f"  • On any AVL: {products_df['on_any_avl'].sum()} products")
            print(f"  • On all AVLs: {products_df['on_all_avls'].sum()} products")

            if 'thrive_approved' in products_df.columns:
                print(f"  • THRIVE approved: {products_df['thrive_approved'].sum()} products")

            if 'goodleap_approved' in products_df.columns:
                print(f"  • GOODLEAP approved: {products_df['goodleap_approved'].sum()} products")

        # Domestic content
        if 'domestic_content_qualified' in products_df.columns:
            domestic_count = products_df['domestic_content_qualified'].sum()
            print(f"\n🇺🇸 Domestic Content: {domestic_count} products")

        # Price statistics
        if 'price_per_unit' in products_df.columns:
            prices = products_df['price_per_unit']
            prices = prices[prices > 0]
            if not prices.empty:
                print(f"\n💰 Price Statistics:")
                print(f"  • Average: ${prices.mean():.2f}")
                print(f"  • Minimum: ${prices.min():.2f}")
                print(f"  • Maximum: ${prices.max():.2f}")

        print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

    def run(self) -> pd.DataFrame:
        """
        Main execution method

        Returns:
            DataFrame with all scraped and processed products
        """
        start_time = datetime.now()

        # Step 1: Scrape all distributors
        all_products = self.run_scraping()

        if not all_products:
            print("❌ No products scraped. Exiting.")
            return pd.DataFrame()

        # Step 2: Convert to DataFrame
        products_df = pd.DataFrame(all_products)

        # Step 3: Add AVL matching
        products_df = self.add_avl_matching(products_df)

        # Step 4: Download spec sheets (if enabled)
        if self.spec_downloader:
            self.download_spec_sheets(all_products)

        # Step 5: Export to Excel
        output_file = self.export_to_excel(products_df)

        # Step 6: Print summary
        self.print_summary(products_df)

        # Print execution time
        elapsed = datetime.now() - start_time
        print(f"⏱️  Total execution time: {elapsed}")

        return products_df


def main():
    """Entry point"""
    try:
        scraper = SolarEquipmentScraper('scraper_config.yaml')
        results = scraper.run()

        if not results.empty:
            print("\n✅ Scraping completed successfully!")
        else:
            print("\n⚠️  No results to export")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
