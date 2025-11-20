"""
Quick test of the complete pipeline
Tests scraping, AVL matching, and Excel export with limited data
"""

from solar_equipment_scraper import SolarEquipmentScraper

def main():
    print("\n" + "="*60)
    print("🧪 TESTING SOLAR EQUIPMENT SCRAPER PIPELINE")
    print("="*60 + "\n")

    # Run with test config (limited scrapers)
    scraper = SolarEquipmentScraper('test_config.yaml')

    # Run the system
    results = scraper.run()

    if not results.empty:
        print("\n" + "="*60)
        print("✅ TEST SUCCESSFUL!")
        print("="*60)
        print(f"\nResults:")
        print(f"  • Total products: {len(results)}")
        print(f"  • Categories: {results['category'].nunique() if 'category' in results.columns else 'N/A'}")
        print(f"  • On any AVL: {results['on_any_avl'].sum() if 'on_any_avl' in results.columns else 'N/A'}")
        print(f"  • Domestic content: {results['domestic_content_qualified'].sum() if 'domestic_content_qualified' in results.columns else 'N/A'}")
        print("="*60 + "\n")
    else:
        print("\n⚠️  No results returned")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
