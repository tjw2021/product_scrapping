# 🚀 QUICK START GUIDE - Solar Cellz USA Scraper

## 5-Minute Setup

### Step 1: Google Cloud Setup (2 minutes)
1. Go to: https://console.cloud.google.com/
2. Create project → Enable "Google Sheets API" and "Google Drive API"
3. Create Service Account → Download JSON credentials
4. Copy the email from JSON (looks like: xxx@xxx.iam.gserviceaccount.com)

### Step 2: Google Sheet Setup (1 minute)
1. Create new Google Sheet: "Solar Cellz USA Inventory"
2. Share it with the service account email (from Step 1)
3. Give "Editor" permission

### Step 3: Replit Setup (2 minutes)
1. Create Python Repl on Replit.com
2. Upload these files:
   - solar_scraper_app.py
   - requirements.txt
   - credentials.json (your downloaded file)
3. In Secrets tab, add:
   - Name: `GOOGLE_SHEET_NAME`
   - Value: `Solar Cellz USA Inventory`

### Step 4: Run! ▶️
Click "Run" button or type:
```bash
python solar_scraper_app.py
```

## Expected Results

After running, your Google Sheet will have approximately 100+ rows with:
- Product names (Renogy, Canadian Solar, Meyer Burger, etc.)
- Current prices ($88.99 - $210+ range)
- Stock status (In Stock / Out of Stock)
- Product URLs and images
- Last update timestamp

## What You'll See in Console

```
============================================================
🌞 Solar Cellz USA Inventory Scraper
============================================================
✅ Connected to Google Sheet: Solar Cellz USA Inventory
🔍 Starting to scrape Solar Cellz USA...
📄 Fetching page 1...
📄 Fetching page 2...
✅ Completed scraping. Total products: 156
📊 Updating Google Sheet with 156 products...
✅ Successfully updated Google Sheet!
📈 Total products: 156

📊 Summary Statistics:
   • Total Products: 156
   • In Stock: 143
   • Out of Stock: 13
   • Average Price: $178.42

✨ Scraping complete!
============================================================
```

## Automation Options

### Option A: Manual (Free)
Run the script whenever you want updated data

### Option B: Scheduled (Free with external service)
1. Get your Repl URL (when deployed)
2. Use cron-job.org to ping it every 4 hours

### Option C: Always-On (Replit Paid Plan)
Use `scheduled_scraper.py` for continuous updates:
```bash
python scheduled_scraper.py
```

## Troubleshooting

**Error: "Permission Denied"**
→ Did you share the Google Sheet with service account email?

**Error: "No products found"**
→ Website might be temporarily down, try again in a few minutes

**Error: "Can't find credentials"**
→ Make sure credentials.json is uploaded to Replit

## Next Steps

1. ✅ Get basic scraper working
2. 📊 Verify data in Google Sheet
3. 🔄 Set up automation (optional)
4. 🎯 Add more distributor websites
5. 💰 Build price comparison across suppliers
6. 🔔 Add email alerts for price drops

## Sample Google Sheet Structure

| Product ID | Product Title | Vendor | Price | Status | Last Updated |
|------------|--------------|---------|--------|---------|--------------|
| 123456 | Renogy 50W Panel | Renogy | $88.99 | In Stock | 2025-11-13 |
| 123457 | Canadian Solar 380W | Canadian Solar | $155.25 | In Stock | 2025-11-13 |
| 123458 | Meyer Burger 380W | Meyer Burger | $167.95 | Out of Stock | 2025-11-13 |

## Support

Need help? Check:
1. Full README.md for detailed instructions
2. Error messages in Replit console
3. Google Cloud Console for API status
