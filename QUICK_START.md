# Quick Start Guide 🚀

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Sheets Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "Google Sheets API" & "Google Drive API"
3. Create service account → Download JSON credentials
4. Save as `credentials.json` in project folder
5. Create Google Sheet → Share with service account email (found in JSON)

### 3. Basic Configuration
```bash
export GOOGLE_SHEET_NAME="Solar Inventory Tracker"
```

### 4. Run It!
```bash
# One-time run
python main.py

# Scheduled (every 6 hours)
python scheduled_runner.py
```

---

## Optional: Email Alerts

Add these to enable email notifications:

```bash
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-gmail-app-password"
export ALERT_TO_EMAIL="recipient@example.com"
```

**Gmail App Password:** https://myaccount.google.com/apppasswords

---

## What It Does

✅ Scrapes 4 solar distributors (Solar Cellz USA, Solar Electric Supply, Wholesale Solar, altE)
✅ Creates separate Google Sheet tabs for each distributor
✅ Builds master comparison tab with best prices
✅ Tracks price history over time
✅ Sends email alerts for price drops > 10%
✅ Alerts when new products appear
✅ Alerts when out-of-stock items return
✅ Generates weekly summary reports

---

## File You Need

📄 **credentials.json** - Google service account credentials (you create this)

---

## Files Auto-Generated

📄 **price_history.json** - Price tracking database (automatically created)

---

## Customize

Edit `config.py` or set environment variables:

```bash
# Scrape every 4 hours instead of 6
export SCRAPE_INTERVAL_HOURS="4"

# Only alert for price drops > 15%
export PRICE_DROP_THRESHOLD="15.0"

# Only scrape specific distributors
export DISTRIBUTORS_TO_SCRAPE="solar_cellz,wholesale_solar"
```

---

## Next Steps

📚 Read [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for:
- Full configuration options
- Deployment strategies
- Troubleshooting
- Advanced customization

---

## Need Help?

**Common Issues:**

❌ "Permission denied" → Share Google Sheet with service account email
❌ "No products scraped" → Check internet connection / website availability
❌ "Email not sending" → Use Gmail app password, not regular password

**Test Individual Components:**

```bash
# Test single scraper
python scrapers/solar_cellz_scraper.py

# Test email
python -c "from alerting import AlertingSystem; from config import Config; AlertingSystem(Config.get_smtp_config()).send_email('Test', '<h1>Works!</h1>')"
```

---

That's it! You're ready to automate your solar inventory tracking. 🌞
