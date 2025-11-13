# Solar Cellz USA Inventory Scraper 🌞

Automatically scrapes solar panel inventory from Solar Cellz USA and updates a Google Sheet in real-time.

## Features ✨

- **Automated Scraping**: Uses Shopify's JSON API for fast, reliable data extraction
- **Google Sheets Integration**: Automatically updates your inventory spreadsheet
- **Real-time Updates**: Track prices, availability, and inventory levels
- **Clean Data**: Formatted, ready-to-use data with all product details
- **Error Handling**: Robust retry logic and error reporting

## Setup Instructions 🚀

### 1. Set Up Google Sheets API

#### A. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Name it something like "Solar Inventory Scraper"

#### B. Enable Google Sheets API
1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click "Enable"
4. Also enable "Google Drive API" (needed for file access)

#### C. Create Service Account Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Name it "solar-scraper-bot" (or any name)
4. Click "Create and Continue"
5. Skip optional steps, click "Done"

#### D. Generate JSON Key
1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Download the JSON file (this is your credentials file)

### 2. Set Up Your Google Sheet

1. Create a new Google Sheet
2. Name it "Solar Cellz USA Inventory" (or your preferred name)
3. **IMPORTANT**: Share the sheet with your service account email
   - The email looks like: `solar-scraper-bot@your-project.iam.gserviceaccount.com`
   - You can find this in the JSON credentials file under `client_email`
   - Give it "Editor" permissions

### 3. Deploy on Replit

#### A. Create New Repl
1. Go to [Replit](https://replit.com/)
2. Click "Create Repl"
3. Choose "Python" as the language
4. Name it "solar-cellz-scraper"

#### B. Upload Files
1. Upload `solar_scraper_app.py` (main script)
2. Upload `requirements.txt`
3. Upload your Google credentials JSON file as `credentials.json`

#### C. Set Environment Variables (Secrets)
In Replit, go to the "Secrets" tab (lock icon) and add:

```
GOOGLE_SHEET_NAME = Solar Cellz USA Inventory
```

Optional (if you want to use secrets instead of uploading file):
```
GOOGLE_CREDENTIALS = [paste entire contents of your JSON credentials file]
```

#### D. Run the Script
Click the "Run" button or use:
```bash
python solar_scraper_app.py
```

### 4. Schedule Automatic Updates (Optional)

To run the scraper automatically every few hours:

#### Option 1: Replit Deployments (Paid)
1. Deploy your Repl
2. Set up a cron job in the deployment settings

#### Option 2: Always-On Repl (Paid)
1. Modify the script to run in a loop:
```python
import schedule

schedule.every(4).hours.do(scraper.run)

while True:
    schedule.run_pending()
    time.sleep(60)
```

#### Option 3: External Cron Service (Free)
1. Deploy your Repl
2. Use a service like [cron-job.org](https://cron-job.org/)
3. Set it to ping your Repl URL every 4-6 hours

#### Option 4: GitHub Actions (Free)
1. Push code to GitHub
2. Create a workflow file to run on schedule
3. Store credentials as GitHub Secrets

## What Data Gets Scraped 📊

The scraper extracts and organizes:

- **Product ID** - Unique Shopify product identifier
- **Variant ID** - Unique variant identifier
- **Product Title** - Full product name
- **Vendor** - Manufacturer/brand
- **Type** - Product category
- **Variant** - Size/model variations
- **SKU** - Stock keeping unit
- **Price** - Current price
- **Compare Price** - Original/MSRP price
- **Discount %** - Calculated savings
- **Status** - In Stock / Out of Stock
- **Inventory Qty** - Available quantity
- **Weight** - Product weight
- **Weight Unit** - lbs/kg
- **Product URL** - Direct link to product page
- **Image URL** - Product image
- **Last Updated** - Timestamp of scrape

## Google Sheet Output 📈

Your Google Sheet will have columns for all the data above, formatted and ready to use. Headers are bold and have a gray background for easy reading.

## Troubleshooting 🔧

### "Permission Denied" Error
- Make sure you shared your Google Sheet with the service account email
- Check that both Google Sheets API and Google Drive API are enabled

### "No products scraped"
- Check your internet connection
- The website might be temporarily down
- Rate limiting might be in effect (wait and try again)

### "Can't find credentials"
- Make sure `credentials.json` is in the same directory as the script
- Or set the `GOOGLE_CREDENTIALS` environment variable with the JSON content

## Customization 💡

### Change Update Frequency
Modify the `time.sleep(1)` value in the scraping loop (in seconds)

### Add More Data Fields
Edit the `product_info` dictionary in the `scrape_solar_panels()` method

### Filter Products
Add filtering logic before adding to `all_products` list

### Multiple Sheets
Create multiple scraper instances with different sheet names:
```python
scraper1 = SolarCellzScraper("Solar Panels Inventory")
scraper2 = SolarCellzScraper("Solar Panels Archive")
```

## Next Steps 🎯

1. **Add More Distributors**: Create similar scrapers for other solar equipment sites
2. **Price Comparison**: Compare prices across multiple suppliers automatically
3. **Automated Alerts**: Get notified when prices drop or new inventory arrives
4. **CRM Integration**: Connect to your CRM system for automated supplier outreach
5. **Historical Tracking**: Store price history in a separate sheet for trend analysis

## Support 💬

If you run into issues:
1. Check the error messages in the Replit console
2. Verify your Google Sheet sharing settings
3. Test with a simple spreadsheet first
4. Make sure all API access is enabled in Google Cloud Console

## License

Free to use and modify for your business needs!
