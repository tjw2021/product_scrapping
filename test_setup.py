"""
Setup Test Script
Run this to verify your configuration before running the full system
"""

import os
import sys


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_imports():
    """Test if all required packages are installed"""
    print_header("Testing Package Imports")

    packages = {
        'requests': 'requests',
        'gspread': 'gspread',
        'oauth2client': 'oauth2client',
        'schedule': 'schedule',
    }

    all_good = True

    for name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - Run: pip install {name}")
            all_good = False

    return all_good


def test_google_credentials():
    """Test Google credentials"""
    print_header("Testing Google Credentials")

    # Check for credentials file
    if os.path.exists('credentials.json'):
        print(f"  ✅ credentials.json found")

        try:
            import json
            with open('credentials.json', 'r') as f:
                creds = json.load(f)

            required_fields = ['type', 'project_id', 'client_email']
            missing = [f for f in required_fields if f not in creds]

            if missing:
                print(f"  ⚠️  Missing fields in credentials.json: {', '.join(missing)}")
                return False

            print(f"  ✅ Service account email: {creds['client_email']}")
            print(f"  ℹ️  Share your Google Sheet with this email!")
            return True

        except Exception as e:
            print(f"  ❌ Error reading credentials.json: {e}")
            return False

    elif os.environ.get('GOOGLE_CREDENTIALS'):
        print(f"  ✅ GOOGLE_CREDENTIALS environment variable set")
        return True
    else:
        print(f"  ❌ No credentials found!")
        print(f"     Create credentials.json or set GOOGLE_CREDENTIALS env var")
        return False


def test_google_sheet_connection():
    """Test connection to Google Sheets"""
    print_header("Testing Google Sheets Connection")

    try:
        from sheets_manager import SheetsManager
        from config import Config

        sheet_name = Config.GOOGLE_SHEET_NAME

        print(f"  📊 Attempting to connect to: {sheet_name}")
        sheets = SheetsManager(sheet_name)

        print(f"  ✅ Successfully connected to Google Sheets!")
        return True

    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        print(f"\n  Troubleshooting:")
        print(f"    1. Make sure the sheet '{Config.GOOGLE_SHEET_NAME}' exists")
        print(f"    2. Share it with your service account email")
        print(f"    3. Grant 'Editor' permissions")
        return False


def test_scraper():
    """Test a single scraper"""
    print_header("Testing Scraper (Solar Cellz USA)")

    try:
        from scrapers import SolarCellzScraper

        print(f"  🔍 Running quick scraper test (first page only)...")

        scraper = SolarCellzScraper()
        url = f"{scraper.base_url}/collections/solar-panels/products.json?limit=5"

        response = scraper.make_request(url)

        if response:
            data = response.json()
            products = data.get('products', [])

            if products:
                print(f"  ✅ Successfully scraped {len(products)} sample products")
                print(f"  ℹ️  Example: {products[0]['title']}")
                return True
            else:
                print(f"  ⚠️  No products returned")
                return False
        else:
            print(f"  ❌ Failed to fetch data")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_email_config():
    """Test email configuration"""
    print_header("Testing Email Configuration")

    from config import Config

    if not Config.SMTP_USERNAME:
        print(f"  ⚠️  Email alerts not configured (optional)")
        print(f"     Set SMTP_USERNAME to enable email alerts")
        return None

    print(f"  📧 SMTP Server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")
    print(f"  📧 From: {Config.ALERT_FROM_EMAIL or Config.SMTP_USERNAME}")
    print(f"  📧 To: {Config.ALERT_TO_EMAIL}")

    if not Config.SMTP_PASSWORD:
        print(f"  ❌ SMTP_PASSWORD not set")
        return False

    # Ask user if they want to send test email
    response = input("\n  Send test email? (y/n): ").lower().strip()

    if response == 'y':
        try:
            from alerting import AlertingSystem

            alerting = AlertingSystem(Config.get_smtp_config())
            success = alerting.send_email(
                "🧪 Test Alert",
                "<h1>Success!</h1><p>Your email alerts are working correctly.</p>"
            )

            if success:
                print(f"  ✅ Test email sent successfully!")
                return True
            else:
                print(f"  ❌ Failed to send test email")
                return False

        except Exception as e:
            print(f"  ❌ Error sending email: {e}")
            return False
    else:
        print(f"  ⏭️  Skipped email test")
        return None


def test_config():
    """Test configuration"""
    print_header("Configuration Summary")

    from config import Config

    Config.print_config()

    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  🧪 SOLAR INVENTORY SYSTEM - SETUP TEST")
    print("="*60)

    results = {
        'Packages': test_imports(),
        'Google Credentials': test_google_credentials(),
        'Google Sheets': test_google_sheet_connection(),
        'Scraper': test_scraper(),
        'Email': test_email_config(),
        'Configuration': test_config(),
    }

    # Summary
    print_header("Test Summary")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for test_name, result in results.items():
        if result is True:
            print(f"  ✅ {test_name}")
        elif result is False:
            print(f"  ❌ {test_name}")
        else:
            print(f"  ⏭️  {test_name} (skipped)")

    print(f"\n  Results: {passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        print(f"\n  🎉 All tests passed! You're ready to run the system.")
        print(f"\n  Next steps:")
        print(f"    • Run once: python main.py")
        print(f"    • Run scheduled: python scheduled_runner.py")
    else:
        print(f"\n  ⚠️  Some tests failed. Please fix the issues above.")
        print(f"     Check COMPLETE_GUIDE.md for troubleshooting help.")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        sys.exit(1)
