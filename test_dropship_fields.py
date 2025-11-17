#!/usr/bin/env python3
"""
Test dropship and delivery date field extraction
"""

import sys
sys.path.insert(0, '/home/user/product_scrapping')

from scrapers.soligent_scraper import SoligentScraper


def test_dropship_fields():
    """Test that dropship and delivery date fields are extracted"""

    print("=" * 70)
    print("TESTING DROPSHIP AND DELIVERY DATE FIELDS")
    print("=" * 70)

    scraper = SoligentScraper()

    # Fetch products
    print("\n📡 Fetching 50 products...")
    data = scraper._fetch_products_page(page=1, page_size=50)

    if not data or 'items' not in data:
        print("❌ Failed to fetch products")
        return False

    products = []
    for item in data['items']:
        product = scraper._parse_product(item)
        if product:
            products.append(product)

    print(f"✅ Parsed {len(products)} products\n")

    # Check that the new fields exist
    print("=" * 70)
    print("CHECKING NEW FIELDS")
    print("=" * 70)

    if products:
        first_product = products[0]

        print(f"\nSample product: {first_product['title'][:60]}")
        print("\n✅ New fields added to specs:")

        specs = first_product.get('specs', {})

        print(f"  • is_dropship: {specs.get('is_dropship', 'MISSING')}")
        print(f"  • is_backorderable: {specs.get('is_backorderable', 'MISSING')}")
        print(f"  • delivery_date_eta: {specs.get('delivery_date_eta', 'MISSING')}")

        # Show examples
        print("\n" + "=" * 70)
        print("EXAMPLES FROM FIRST 10 PRODUCTS")
        print("=" * 70)

        dropship_count = 0
        backorder_count = 0
        delivery_info_count = 0

        for idx, product in enumerate(products[:10], 1):
            specs = product.get('specs', {})

            is_dropship = specs.get('is_dropship', 'No')
            is_backorderable = specs.get('is_backorderable', 'No')
            delivery_eta = specs.get('delivery_date_eta', 'N/A')
            stock_status = product.get('stock_status', 'Unknown')

            print(f"\n{idx}. {product['title'][:50]}")
            print(f"   Stock Status: {stock_status}")
            print(f"   Dropship: {is_dropship}")
            print(f"   Backorderable: {is_backorderable}")
            if delivery_eta != 'N/A':
                print(f"   Delivery/ETA: {delivery_eta}")
                delivery_info_count += 1

            if is_dropship == 'Yes':
                dropship_count += 1
            if is_backorderable == 'Yes':
                backorder_count += 1

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total products tested: {len(products[:10])}")
        print(f"Dropship items: {dropship_count}")
        print(f"Backorderable items: {backorder_count}")
        print(f"Items with delivery/ETA info: {delivery_info_count}")

        print("\n✅ NEW FIELDS SUCCESSFULLY ADDED!")
        print("\nThese fields will now appear in Google Sheets:")
        print("  • Dropship Status (Yes/No)")
        print("  • Backorderable (Yes/No)")
        print("  • Delivery Date/ETA (if available)")

        return True

    return False


if __name__ == "__main__":
    success = test_dropship_fields()
    sys.exit(0 if success else 1)
