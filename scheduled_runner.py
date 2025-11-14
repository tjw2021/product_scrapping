"""
Scheduled Runner
Runs the scraper at specified intervals (default: every 6 hours)
"""

import schedule
import time
from main import SolarInventorySystem
from config import Config
from datetime import datetime


def scheduled_job():
    """Job to run on schedule"""
    print(f"\n{'='*60}")
    print(f"⏰ SCHEDULED RUN STARTED")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        system = SolarInventorySystem()
        system.run()
    except Exception as e:
        print(f"❌ Scheduled job failed: {e}")

    interval_hours = Config.SCRAPE_INTERVAL_HOURS
    print(f"\n{'='*60}")
    print(f"⏰ Next run scheduled in {interval_hours} hours")
    print(f"{'='*60}\n")


def main():
    """Main scheduler loop"""
    interval_hours = Config.SCRAPE_INTERVAL_HOURS

    print("="*60)
    print("🚀 SOLAR INVENTORY SCHEDULER")
    print("="*60)
    print(f"Schedule: Every {interval_hours} hours")
    print(f"Next run: Immediately")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")

    # Schedule the job
    schedule.every(interval_hours).hours.do(scheduled_job)

    # Run immediately on startup
    scheduled_job()

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⚠️ Scheduler stopped by user")


if __name__ == "__main__":
    main()
