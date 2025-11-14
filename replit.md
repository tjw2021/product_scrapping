# Solar Inventory Automation System

## Overview
This is a Python-based solar inventory scraper that automatically extracts product data from multiple solar panel distributors and updates a Google Sheet with real-time inventory information.

## Project Type
Backend / CLI automation system (no web interface)

## Key Features
- Scrapes 5 solar distributors: Solar Cellz USA, Solar Electric Supply, Wholesale Solar, altE Store, and RES Supply
- Updates Google Sheets with product data (prices, availability, specs)
- Tracks price changes and sends email alerts
- Can run on-demand or on a schedule (every 6 hours by default)

## Main Entry Points
- `main.py` - Run the scraper once manually
- `scheduled_runner.py` - Run the scraper on a schedule (configured via workflow)
- `test_api.py` - Test API connectivity
- `test_setup.py` - Test Google Sheets setup

## Architecture
- **Scrapers**: Individual scrapers for each distributor in `scrapers/` directory
- **Sheets Manager**: Handles Google Sheets integration (`sheets_manager.py`)
- **Price Tracker**: Tracks price changes over time (`price_tracker.py`)
- **Alerting**: Email notification system (`alerting.py`)
- **Config**: Centralized configuration from environment variables (`config.py`)

## Configuration
All settings are controlled via environment variables:

### Required Secrets
- `GOOGLE_CREDENTIALS` or upload `credentials.json` file - Google service account credentials
- `GOOGLE_SHEET_NAME` - Name of the Google Sheet to update (default: "Solar Inventory Tracker")

### Optional Settings
- `SCRAPE_INTERVAL_HOURS` - How often to run (default: 6)
- `DISTRIBUTORS_TO_SCRAPE` - Comma-separated list (default: all 4)
- `PRICE_DROP_THRESHOLD` - Alert threshold percentage (default: 10.0)
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - Email alert settings
- `ALERT_FROM_EMAIL`, `ALERT_TO_EMAIL` - Email addresses for alerts

### Feature Flags
- `ENABLE_PRICE_TRACKING` - Track price changes (default: true)
- `ENABLE_EMAIL_ALERTS` - Send email alerts (default: true)
- `CREATE_COMPARISON_TAB` - Create comparison sheet (default: true)
- `CREATE_SUMMARY_TAB` - Create summary sheet (default: true)

## Setup Requirements
1. **Python 3.11** - Already installed
2. **Dependencies** - Already installed from requirements.txt
3. **Google Sheets API**:
   - Create a Google Cloud project
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download credentials.json
   - Share your Google Sheet with the service account email
4. **Credentials**: Upload credentials.json or set GOOGLE_CREDENTIALS secret

## How It Works
1. **Scraping**: Uses Shopify JSON APIs to extract product data from distributor websites
2. **Processing**: Normalizes data across all distributors
3. **Storage**: Updates Google Sheets with tabs for each distributor
4. **Tracking**: Stores price history in `price_history.json`
5. **Alerting**: Sends email notifications for price drops, new products, and stock changes

## Current Status
- ✅ Python 3.11 installed
- ✅ All dependencies installed  
- ✅ Google Sheets integration fully configured and working
- ✅ Code tested and working (scraped 179 products successfully)
- ✅ Data successfully transfers to Google Sheets
- ✅ Scheduled workflow configured (runs every 6 hours)
- ✅ 3 out of 5 scrapers working perfectly:
  - Solar Cellz USA: 141 products (Shopify API) ✅
  - altE Store: 38 products (Shopify API) ✅
  - RES Supply: 14 products (HTML scraping) ✅
- ⚠️ 2 scrapers need updates (website platform changed):
  - Solar Electric Supply: Uses Magento (not Shopify API)
  - Wholesale Solar: Domain redirects to unboundsolar.com
- ⚠️ Email alerts not configured (optional)

## Working Features
1. **Scraping**: Successfully scrapes 193 products from 3 distributors
   - Solar Cellz USA: 141 products via Shopify API
   - altE Store: 38 products via Shopify API
   - RES Supply: 14 products via HTML scraping
2. **Google Sheets**: Automatically creates and updates Google Sheets with tabs:
   - Individual distributor tabs (Solar Cellz USA, altE Store, RES Supply)
   - Best Prices comparison tab
   - Summary statistics tab
3. **Scheduling**: Runs every 6 hours automatically
4. **Price Tracking**: Tracks price history in price_history.json
5. **Google Sheets URL**: https://docs.google.com/spreadsheets/d/{auto-generated-id}

## Known Issues & Solutions
### Solar Electric Supply Scraper (Currently Disabled)
- **Issue**: Website uses Magento, not Shopify - Shopify API endpoints return 404
- **Solution**: Need to implement Magento scraper or HTML scraping
- **Temporary Fix**: Disabled in default configuration

### Wholesale Solar Scraper (Currently Disabled)
- **Issue**: Domain now redirects to unboundsolar.com
- **Solution**: Update scraper to use unboundsolar.com or remove
- **Temporary Fix**: Disabled in default configuration

## User Preferences
None set yet - first time setup

## Recent Changes
- 2025-11-14: Added RES Supply scraper
  - Created new HTML-based scraper for ressupply.com (uses OpenCart platform)
  - Scrapes 14 solar panel products from 2 categories (solar-panels, solar-panel-pallets)
  - Extracts product details including specs, pricing, wattage, brand, and minimum quantities
  - Added to default configuration alongside Solar Cellz USA and altE Store
  - Total products now: 193 across 3 distributors
- 2025-11-14: Initial setup in Replit environment
  - Installed Python 3.11 and dependencies
  - Configured scheduled workflow to run every 6 hours
  - Tested scraping functionality (working correctly)
  - Successfully integrated Google Sheets via Replit connector
