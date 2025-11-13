"""
Test Script - Verify API Access
Run this first to make sure the scraping will work
"""

import requests
import json

def test_shopify_api():
    """Test if we can access Solar Cellz USA's Shopify API"""
    print("🧪 Testing Solar Cellz USA API Access...\n")
    
    base_url = "https://shop.solarcellzusa.com"
    test_url = f"{base_url}/collections/solar-panels/products.json?limit=5"
    
    try:
        print(f"📡 Attempting to fetch: {test_url}")
        response = requests.get(test_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        products = data.get('products', [])
        
        if products:
            print(f"✅ SUCCESS! API is accessible")
            print(f"📦 Retrieved {len(products)} sample products\n")
            
            print("Sample Product Details:")
            print("=" * 60)
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. {product['title']}")
                print(f"   Vendor: {product.get('vendor', 'N/A')}")
                print(f"   Product ID: {product['id']}")
                print(f"   Variants: {len(product.get('variants', []))}")
                print(f"   URL: {base_url}/products/{product['handle']}")
                
                if product.get('variants'):
                    variant = product['variants'][0]
                    print(f"   Price: ${variant.get('price', 0)}")
                    print(f"   Available: {'Yes' if variant.get('available') else 'No'}")
            
            print("\n" + "=" * 60)
            print("✅ API test successful! You're ready to run the full scraper.")
            return True
            
        else:
            print("⚠️ API returned no products")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing API: {e}")
        print("\nPossible causes:")
        print("  • No internet connection")
        print("  • Website is down")
        print("  • Your IP might be rate-limited")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_pagination():
    """Test pagination to see how many pages exist"""
    print("\n🔍 Testing pagination...\n")
    
    base_url = "https://shop.solarcellzusa.com"
    page = 1
    total_products = 0
    
    while page <= 3:  # Only test first 3 pages
        try:
            url = f"{base_url}/collections/solar-panels/products.json?limit=250&page={page}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            products = data.get('products', [])
            
            if not products:
                print(f"📄 Page {page}: No more products (end of catalog)")
                break
            
            total_products += len(products)
            print(f"📄 Page {page}: Found {len(products)} products")
            
            page += 1
            
        except Exception as e:
            print(f"⚠️ Error on page {page}: {e}")
            break
    
    print(f"\n✅ Estimated total products: ~{total_products}+")
    print("(Full scraper will get all pages)\n")

if __name__ == "__main__":
    print("=" * 60)
    print("🌞 Solar Cellz USA API Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    api_works = test_shopify_api()
    
    if api_works:
        test_pagination()
        print("\n✨ All tests passed! Ready to scrape. ✨")
        print("\nNext step: Run 'python solar_scraper_app.py'")
    else:
        print("\n❌ Tests failed. Please check your connection and try again.")
    
    print("=" * 60)
