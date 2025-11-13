# 🌞 Solar Inventory Automation System

**Multi-Distributor Solar Panel Inventory Scraper with Price Tracking & Email Alerts**

---

## What's New? 🎉

This system has been completely rebuilt with enterprise features:

✅ **4 Distributors** instead of 1
- Solar Cellz USA
- Solar Electric Supply
- Wholesale Solar
- altE Store

✅ **Multi-Tab Google Sheets** with:
- Separate tab per distributor
- Master comparison tab (best prices)
- Summary statistics dashboard

✅ **Price History Tracking**
- Tracks prices over time
- Detects trends
- Stores last 30 data points per product

✅ **Email Alerts** for:
- Price drops > 10%
- New products added
- Stock status changes
- Weekly summary reports

✅ **Professional Architecture**
- Modular, extensible code
- Base scraper class for easy expansion
- Centralized configuration
- Error handling & retries

---

## Quick Start 🚀

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Setup Google Sheets
1. Get Google service account credentials
2. Save as `credentials.json`
3. Create Google Sheet and share with service account

### 3. Run
```bash
# Test your setup
python test_setup.py

# Run once
python main.py

# Run every 6 hours
python scheduled_runner.py
```

**Full setup guide:** [QUICK_START.md](QUICK_START.md)

---

## Features Overview

### 📊 Google Sheets Output

**Individual Distributor Tabs:**
- Product details (ID, SKU, title, brand)
- Pricing (current, compare, discount %)
- Technical specs (wattage, efficiency)
- Stock status & quantity
- Direct product links

**🏆 Best Prices Tab:**
- Ranked by price (best deals first)
- Price range across distributors
- Number of competitors

**📈 Summary Tab:**
- Total products by distributor
- In stock / out of stock counts
- Average, min, max prices

### 🚨 Smart Alerts

**Price Drop Alert:**
```
Subject: 🚨 5 Solar Panel Price Drop(s) Detected!

400W Monocrystalline Panel
Solar Cellz USA
$350.00 → $299.00
Save $51.00 (14.6% off!)
```

**Stock Alert:**
```
Subject: 📦 3 Product(s) Back in Stock!

[Product details with direct links]
```

**Weekly Summary:**
- Market price trends
- Best deals of the week
- Inventory statistics

### ⚙️ Easy Configuration

All settings via environment variables:

```bash
GOOGLE_SHEET_NAME="Solar Inventory"
SCRAPE_INTERVAL_HOURS="6"
PRICE_DROP_THRESHOLD="10.0"
SMTP_USERNAME="your-email@gmail.com"
ALERT_TO_EMAIL="recipient@example.com"
```

Copy `.env.example` to `.env` and customize!

---

## Project Structure

```
product_scrapping/
├── main.py                      # Main system orchestrator
├── scheduled_runner.py          # Scheduled execution
├── config.py                    # Configuration
├── base_scraper.py             # Base scraper class
├── sheets_manager.py           # Google Sheets handler
├── price_tracker.py            # Price history tracking
├── alerting.py                 # Email alerts
├── test_setup.py               # Setup verification
│
├── scrapers/                   # Distributor scrapers
│   ├── solar_cellz_scraper.py
│   ├── solar_electric_supply_scraper.py
│   ├── wholesale_solar_scraper.py
│   └── alte_scraper.py
│
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
│
└── docs/
    ├── QUICK_START.md          # 5-minute setup guide
    ├── COMPLETE_GUIDE.md       # Full documentation
    └── GOOGLE_SETUP_GUIDE.md   # Google Sheets setup
```

---

## Documentation

📚 **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes

📚 **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - Full documentation including:
- Detailed configuration options
- Deployment strategies (Replit, AWS, Heroku, GitHub Actions)
- Troubleshooting guide
- Advanced customization
- FAQ

📚 **[GOOGLE_SETUP_GUIDE.md](GOOGLE_SETUP_GUIDE.md)** - Google Sheets API setup

---

## Example Output

### Google Sheets
![Multiple tabs for each distributor + master comparison]

### Email Alert
```
🚨 Price Drop Alert!
Great news! We found 5 products with significant price drops.

Product: Canadian Solar 400W Panel
Distributor: Wholesale Solar
$350.00 → $299.00
Save $51.00 (14.6% off!)
[View Product →]
```

---

## Requirements

- Python 3.7+
- Google Cloud account (free)
- Google Sheet
- Gmail account (for email alerts, optional)

---

## Deployment Options

### Free Options
- ✅ GitHub Actions (free, recommended)
- ✅ Google Cloud Free Tier
- ✅ Replit (limited)

### Paid Options
- ✅ Replit Always-On ($7/month)
- ✅ AWS EC2 (~$5/month)
- ✅ Heroku (~$7/month)
- ✅ DigitalOcean (~$5/month)

**See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for deployment instructions**

---

## Customization

### Add More Distributors

1. Create new scraper in `scrapers/` (inherit from `BaseScraper`)
2. Register in `main.py`
3. Add to `DISTRIBUTORS_TO_SCRAPE` config

### Custom Alert Rules

Edit `alerting.py` to add custom conditions:
- High-efficiency panels (>22%)
- Specific brands
- Price ranges
- Custom thresholds

### Change Schedule

```bash
# Scrape every 4 hours instead of 6
export SCRAPE_INTERVAL_HOURS="4"
```

---

## Troubleshooting

**"Permission denied" on Google Sheets**
→ Share sheet with service account email

**"No products scraped"**
→ Run `python test_setup.py` to diagnose

**"Email not sending"**
→ Use Gmail App Password, not regular password

**More help:** [COMPLETE_GUIDE.md - Troubleshooting](COMPLETE_GUIDE.md#troubleshooting-)

---

## Testing Your Setup

Run the setup test script:

```bash
python test_setup.py
```

This checks:
- ✅ Required packages
- ✅ Google credentials
- ✅ Google Sheets connection
- ✅ Scraper functionality
- ✅ Email configuration

---

## License

Free to use and modify for your business needs!

---

## Support

📖 Read the docs: [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
🧪 Test your setup: `python test_setup.py`
💬 Issues? Check troubleshooting section in complete guide

---

Built with ❤️ for solar professionals who want to automate their inventory tracking and never miss a great deal.
