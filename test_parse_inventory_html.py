#!/usr/bin/env python3
"""
Test parsing the warehouse inventory HTML structure
Using the actual HTML provided by the user
"""

from bs4 import BeautifulSoup


def test_parse_inventory():
    """Test parsing the inventory HTML"""

    # Actual HTML provided by the user
    html = '''
    <div itemprop="offers" itemscope="" itemtype="http://schema.org/Offer">
        <link itemprop="availability" href="http://schema.org/InStock">
    </div>
    <div class="inventory-display">
        <p class="inventory-display-stock-information-in-stock  inventory-display-message-text">
            <span class="inventory-display-stock-information-in-stock  icon"><i></i></span>
            <span class="inventory-display-message-in-stock "> This item is IN STOCK</span>
        </p>
        <p class="inventory-display-quantity-availablev1">
            <span><b>Current Stock:</b></span>
        </p>
        <ul>
            <li><b>Arlington, TX:</b> 273</li>
            <li><b>Fontana, CA:</b> 124</li>
            <li><b>Millstone, NJ:</b> 38</li>
            <li><b>Orlando, FL:</b> 125</li>
            <li><b>Sacramento, CA:</b> 43</li>
            <li><b>Tampa, FL:</b> 20</li>
            <p></p>
        </ul>
    </div>
    '''

    soup = BeautifulSoup(html, 'html.parser')

    print("=" * 70)
    print("TESTING WAREHOUSE INVENTORY PARSING")
    print("=" * 70)

    # Find the inventory display div
    inventory_display = soup.find('div', class_='inventory-display')

    if not inventory_display:
        print("❌ Could not find inventory-display div")
        return

    print("✅ Found inventory-display div")

    # Check for in-stock message
    in_stock_span = inventory_display.find('span', class_='inventory-display-message-in-stock')
    if in_stock_span:
        print(f"✅ Stock status: {in_stock_span.get_text().strip()}")

    # Find the warehouse list
    warehouse_list = inventory_display.find('ul')

    if not warehouse_list:
        print("❌ Could not find warehouse <ul>")
        return

    print("\n📦 PARSING WAREHOUSE INVENTORY:")
    print("=" * 70)

    warehouse_inventory = {}

    for li in warehouse_list.find_all('li'):
        text = li.get_text().strip()
        print(f"  Raw text: {repr(text)}")

        if ':' in text:
            # Split on first colon
            parts = text.split(':', 1)
            if len(parts) == 2:
                location = parts[0].strip()
                quantity_str = parts[1].strip()

                try:
                    quantity = int(quantity_str.replace(',', ''))
                    warehouse_inventory[location] = quantity
                    print(f"  ✅ Parsed: {location} -> {quantity}")
                except ValueError as e:
                    print(f"  ❌ Could not parse quantity: {quantity_str} ({e})")

    print("\n" + "=" * 70)
    print("FINAL RESULTS:")
    print("=" * 70)
    print(f"\n📦 Total warehouses: {len(warehouse_inventory)}")
    print(f"📊 Total inventory: {sum(warehouse_inventory.values())}")
    print("\nWarehouse breakdown:")
    for location, qty in warehouse_inventory.items():
        print(f"  {location}: {qty}")

    # Show the data structure for the scraper
    print("\n" + "=" * 70)
    print("DATA STRUCTURE FOR SCRAPER:")
    print("=" * 70)
    print(f"warehouse_inventory = {warehouse_inventory}")

    # Create a formatted string for Google Sheets
    warehouse_str = '; '.join([f"{loc}: {qty}" for loc, qty in warehouse_inventory.items()])
    print(f"\nGoogle Sheets format: {warehouse_str}")

    print("\n✅ PARSING TEST SUCCESSFUL!")


if __name__ == "__main__":
    test_parse_inventory()
