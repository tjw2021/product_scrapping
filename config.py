"""
Configuration Settings
Centralized configuration for the solar inventory scraper
"""

import os


class Config:
    """Configuration settings"""

    # Google Sheets
    GOOGLE_SHEET_NAME = os.environ.get('GOOGLE_SHEET_NAME', 'Solar Inventory Tracker')

    # Scraping Settings
    SCRAPE_INTERVAL_HOURS = int(os.environ.get('SCRAPE_INTERVAL_HOURS', '6'))
    # Enable all working scrapers by default
    # wholesale_solar redirects to unboundsolar.com (still disabled)
    DISTRIBUTORS_TO_SCRAPE = os.environ.get(
        'DISTRIBUTORS_TO_SCRAPE',
        'solar_cellz,solar_electric,alte,ressupply'
    ).split(',')

    # Alert Settings
    PRICE_DROP_THRESHOLD = float(os.environ.get('PRICE_DROP_THRESHOLD', '10.0'))  # Percent
    SEND_NEW_PRODUCT_ALERTS = os.environ.get('SEND_NEW_PRODUCT_ALERTS', 'true').lower() == 'true'
    SEND_STOCK_ALERTS = os.environ.get('SEND_STOCK_ALERTS', 'true').lower() == 'true'
    SEND_WEEKLY_SUMMARY = os.environ.get('SEND_WEEKLY_SUMMARY', 'true').lower() == 'true'

    # Email Settings (SMTP)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')  # App password for Gmail
    ALERT_FROM_EMAIL = os.environ.get('ALERT_FROM_EMAIL', '')
    ALERT_TO_EMAIL = os.environ.get('ALERT_TO_EMAIL', '')

    # Price History
    PRICE_HISTORY_FILE = os.environ.get('PRICE_HISTORY_FILE', 'price_history.json')
    KEEP_HISTORY_DAYS = int(os.environ.get('KEEP_HISTORY_DAYS', '90'))

    # Feature Flags
    ENABLE_PRICE_TRACKING = os.environ.get('ENABLE_PRICE_TRACKING', 'true').lower() == 'true'
    ENABLE_EMAIL_ALERTS = os.environ.get('ENABLE_EMAIL_ALERTS', 'true').lower() == 'true'
    CREATE_COMPARISON_TAB = os.environ.get('CREATE_COMPARISON_TAB', 'true').lower() == 'true'
    CREATE_SUMMARY_TAB = os.environ.get('CREATE_SUMMARY_TAB', 'true').lower() == 'true'

    @classmethod
    def get_smtp_config(cls):
        """Get SMTP configuration as dict"""
        return {
            'server': cls.SMTP_SERVER,
            'port': cls.SMTP_PORT,
            'username': cls.SMTP_USERNAME,
            'password': cls.SMTP_PASSWORD,
            'from_email': cls.ALERT_FROM_EMAIL,
            'to_email': cls.ALERT_TO_EMAIL
        }

    @classmethod
    def print_config(cls):
        """Print current configuration (masking sensitive data)"""
        print("\n" + "="*60)
        print("⚙️  CURRENT CONFIGURATION")
        print("="*60)
        print(f"Google Sheet: {cls.GOOGLE_SHEET_NAME}")
        print(f"Scrape Interval: Every {cls.SCRAPE_INTERVAL_HOURS} hours")
        print(f"Distributors: {', '.join(cls.DISTRIBUTORS_TO_SCRAPE)}")
        print(f"\nAlerts:")
        print(f"  • Price Drop Threshold: {cls.PRICE_DROP_THRESHOLD}%")
        print(f"  • New Product Alerts: {'✅' if cls.SEND_NEW_PRODUCT_ALERTS else '❌'}")
        print(f"  • Stock Alerts: {'✅' if cls.SEND_STOCK_ALERTS else '❌'}")
        print(f"  • Weekly Summary: {'✅' if cls.SEND_WEEKLY_SUMMARY else '❌'}")
        print(f"\nEmail Configuration:")
        print(f"  • SMTP Server: {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
        print(f"  • From: {cls.ALERT_FROM_EMAIL or cls.SMTP_USERNAME or 'Not configured'}")
        print(f"  • To: {cls.ALERT_TO_EMAIL or 'Not configured'}")
        print(f"  • Enabled: {'✅' if cls.ENABLE_EMAIL_ALERTS and cls.SMTP_USERNAME else '❌'}")
        print(f"\nFeatures:")
        print(f"  • Price Tracking: {'✅' if cls.ENABLE_PRICE_TRACKING else '❌'}")
        print(f"  • Comparison Tab: {'✅' if cls.CREATE_COMPARISON_TAB else '❌'}")
        print(f"  • Summary Tab: {'✅' if cls.CREATE_SUMMARY_TAB else '❌'}")
        print("="*60 + "\n")
