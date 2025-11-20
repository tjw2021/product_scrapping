"""
Quick test with minimal data
Tests the core functionality without scraping all products
"""

import pandas as pd
from datetime import datetime
from avl_handler import AVLHandler
from excel_exporter import ExcelExporter

def main():
    print("\n" + "="*60)
    print("🧪 QUICK PIPELINE TEST")
    print("="*60 + "\n")

    # Step 1: Create sample product data
    print("1. Creating sample product data...")
    sample_products = [
        {
            'distributor': 'Soligent',
            'category': 'Solar Panel',
            'brand': 'Canadian Solar',
            'sku': 'CS3W-400MS',
            'title': 'Canadian Solar 400W Mono Perc Panel',
            'wattage': '400W',
            'price': 150.00,
            'price_per_unit': 150.00,
            'quantity': 1,
            'stock_status': 'In Stock',
            'inventory_qty': '500',
            'product_url': 'https://connect.soligent.net/product1',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'specs': {'domestic_content': 'No'}
        },
        {
            'distributor': 'Soligent',
            'category': 'Solar Panel',
            'brand': 'Silfab',
            'sku': 'SIL-380-BX',
            'title': 'Silfab 380W Solar Panel - Domestic Content',
            'wattage': '380W',
            'price': 175.00,
            'price_per_unit': 175.00,
            'quantity': 1,
            'stock_status': 'In Stock',
            'inventory_qty': '200',
            'product_url': 'https://connect.soligent.net/product2',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'specs': {'domestic_content': 'Yes'}
        },
        {
            'distributor': 'Soligent',
            'category': 'Inverter',
            'brand': 'SolarEdge',
            'sku': 'SE7600H-US',
            'title': 'SolarEdge 7.6kW Inverter with HD-Wave',
            'wattage': 'N/A',
            'price': 1250.00,
            'price_per_unit': 1250.00,
            'quantity': 1,
            'stock_status': 'In Stock',
            'inventory_qty': '50',
            'product_url': 'https://connect.soligent.net/product3',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'specs': {'domestic_content': 'Yes'}
        },
        {
            'distributor': 'Soligent',
            'category': 'Inverter',
            'brand': 'Enphase',
            'sku': 'IQ8PLUS-72-2-US',
            'title': 'Enphase IQ8+ Microinverter',
            'wattage': 'N/A',
            'price': 180.00,
            'price_per_unit': 180.00,
            'quantity': 1,
            'stock_status': 'In Stock',
            'inventory_qty': '1000',
            'product_url': 'https://connect.soligent.net/product4',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'specs': {'domestic_content': 'Yes'}
        },
        {
            'distributor': 'Soligent',
            'category': 'Battery/Storage',
            'brand': 'Tesla',
            'sku': 'POWERWALL3',
            'title': 'Tesla Powerwall 3',
            'wattage': 'N/A',
            'price': 8500.00,
            'price_per_unit': 8500.00,
            'quantity': 1,
            'stock_status': 'Dropship',
            'inventory_qty': '0',
            'product_url': 'https://connect.soligent.net/product5',
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'specs': {'domestic_content': 'Yes'}
        }
    ]

    df = pd.DataFrame(sample_products)
    print(f"   ✅ Created {len(df)} sample products")

    # Step 2: Test AVL matching
    print("\n2. Testing AVL matching...")
    avl_handler = AVLHandler('THRIVE_AVL.xlsx', 'GOODLEAP_AVL.xlsx')
    df = avl_handler.add_avl_columns(df)
    print("   ✅ AVL matching complete")

    # Step 3: Test Excel export
    print("\n3. Testing Excel export...")
    output_file = 'output/quick_test_output.xlsx'
    exporter = ExcelExporter(output_file)
    exporter.export_by_category(df, include_summary=True, include_domestic_only=True)
    print("   ✅ Excel export complete")

    # Step 4: Print results
    print("\n" + "="*60)
    print("✅ TEST RESULTS")
    print("="*60)
    print(f"\nTotal Products: {len(df)}")
    print(f"Categories: {df['category'].nunique()}")
    print(f"On THRIVE AVL: {df['thrive_approved'].sum()}")
    print(f"On GOODLEAP AVL: {df['goodleap_approved'].sum()}")
    print(f"On Any AVL: {df['on_any_avl'].sum()}")
    print(f"Domestic Content: {df['domestic_content_qualified'].sum()}")
    print(f"\nOutput saved to: {output_file}")

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
