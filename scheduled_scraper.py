"""
Scheduled Scraper - Runs automatically at specified intervals
Use this for continuous monitoring
"""

import schedule
import time
from solar_scraper_app import SolarCellzScraper
import os
from datetime import datetime

def job():
    """Job to run on schedule"""
    print(f"\n{'='*60}")
    print(f"⏰ Scheduled run started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        sheet_name = os.environ.get('GOOGLE_SHEET_NAME', 'Solar Cellz USA Inventory')
        scraper = SolarCellzScraper(sheet_name)
        scraper.run()
    except Exception as e:
        print(f"❌ Scheduled job failed: {e}")
    
    print(f"\n{'='*60}")
    print(f"⏰ Next run scheduled in 4 hours")
    print(f"{'='*60}\n")

# Schedule the job every 4 hours
schedule.every(4).hours.do(job)

# Also run immediately on startup
print("🚀 Starting scheduled scraper...")
print("📅 Schedule: Every 4 hours")
print("🛑 Press Ctrl+C to stop\n")

# Run immediately on startup
job()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
