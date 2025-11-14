# Solar Inventory Automation System - Complete Guide 🌞

## Overview

A comprehensive automation system that scrapes solar panel inventory from multiple distributors, tracks price changes, sends email alerts, and maintains organized Google Sheets with price comparisons.

## Features ✨

### 🔍 Multi-Distributor Scraping
- **Solar Cellz USA** - shop.solarcellzusa.com
- **Solar Electric Supply** - solarelectricsupply.com
- **Wholesale Solar** - wholesalesolar.com
- **altE Store** - altestore.com

### 📊 Google Sheets Integration
- **Separate tabs for each distributor** with full product details
- **Master comparison tab** showing best prices across all distributors
- **Summary statistics tab** with market overview
- **Price history tracking** (last 30 data points per product)

### 🚨 Email Alerts
- **Price drops** > 10% (configurable threshold)
- **New products** added to inventory
- **Stock changes** (items back in stock)
- **Weekly summary** reports with market trends

### 📈 Smart Features
- Automatic wattage and efficiency extraction from titles
- Price trend analysis
- Best deal recommendations
- Configurable via environment variables
- Scheduled execution (every 6 hours by default)

---

## Quick Start 🚀

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Sheets

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Create service account credentials
5. Download the JSON credentials file as `credentials.json`
6. Create a Google Sheet and share it with your service account email

### 3. Configure Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required
GOOGLE_SHEET_NAME="Solar Inventory Tracker"

# Optional - Email Alerts
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
ALERT_TO_EMAIL="recipient@example.com"

# Optional - Customization
SCRAPE_INTERVAL_HOURS="6"
PRICE_DROP_THRESHOLD="10.0"
DISTRIBUTORS_TO_SCRAPE="solar_cellz,solar_electric,wholesale_solar,alte"
```

### 4. Run the System

**One-time run:**
```bash
python main.py
```

**Scheduled execution (every 6 hours):**
```bash
python scheduled_runner.py
```

---

## Configuration Options ⚙️

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_SHEET_NAME` | Solar Inventory Tracker | Name of your Google Sheet |
| `SCRAPE_INTERVAL_HOURS` | 6 | Hours between scraping runs |
| `DISTRIBUTORS_TO_SCRAPE` | all | Comma-separated list of distributors |

### Alert Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PRICE_DROP_THRESHOLD` | 10.0 | Minimum % price drop to trigger alert |
| `SEND_NEW_PRODUCT_ALERTS` | true | Alert when new products appear |
| `SEND_STOCK_ALERTS` | true | Alert when items back in stock |
| `SEND_WEEKLY_SUMMARY` | true | Send weekly summary report |

### Email Configuration

| Variable | Description |
|----------|-------------|
| `SMTP_SERVER` | SMTP server address (e.g., smtp.gmail.com) |
| `SMTP_PORT` | SMTP port (usually 587) |
| `SMTP_USERNAME` | Your email address |
| `SMTP_PASSWORD` | App password (not regular password!) |
| `ALERT_TO_EMAIL` | Recipient email address |

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use the app password for `SMTP_PASSWORD`

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_PRICE_TRACKING` | true | Track price history |
| `ENABLE_EMAIL_ALERTS` | true | Send email notifications |
| `CREATE_COMPARISON_TAB` | true | Create best prices tab |
| `CREATE_SUMMARY_TAB` | true | Create statistics tab |

---

## File Structure 📁

```
product_scrapping/
├── main.py                    # Main orchestrator
├── scheduled_runner.py        # Scheduled execution
├── config.py                  # Configuration settings
├── base_scraper.py           # Base scraper class
├── sheets_manager.py         # Google Sheets manager
├── price_tracker.py          # Price history tracking
├── alerting.py               # Email alert system
├── requirements.txt          # Python dependencies
├── credentials.json          # Google API credentials (you provide)
├── price_history.json        # Price history database (auto-generated)
│
├── scrapers/                 # Distributor scrapers
│   ├── __init__.py
│   ├── solar_cellz_scraper.py
│   ├── solar_electric_supply_scraper.py
│   ├── wholesale_solar_scraper.py
│   └── alte_scraper.py
│
└── docs/                     # Documentation
    ├── COMPLETE_GUIDE.md     # This file
    ├── README.md             # Original readme
    └── GOOGLE_SETUP_GUIDE.md # Google Sheets setup
```

---

## Usage Examples 💡

### Basic Usage

```python
from main import SolarInventorySystem

# Create and run system
system = SolarInventorySystem()
system.run()
```

### Custom Configuration

```python
import os
os.environ['PRICE_DROP_THRESHOLD'] = '15.0'  # 15% threshold
os.environ['SCRAPE_INTERVAL_HOURS'] = '4'    # Every 4 hours

system = SolarInventorySystem()
system.run()
```

### Run Specific Distributors Only

```python
os.environ['DISTRIBUTORS_TO_SCRAPE'] = 'solar_cellz,wholesale_solar'

system = SolarInventorySystem()
system.run()
```

---

## Google Sheets Output 📊

### Individual Distributor Tabs

Each distributor gets its own tab with columns:
- Distributor
- Product ID
- SKU
- Product Title
- Brand
- Wattage
- Efficiency
- Price
- Compare Price
- Discount %
- Stock Status
- Inventory Qty
- Shipping Cost
- Product URL
- Image URL
- Last Updated

### 🏆 Best Prices Tab

Master comparison showing:
- Rank (best deals first)
- Product Title
- Brand
- Wattage
- Best Price
- Best Distributor
- Stock Status
- Price Range (across all distributors)
- Number of competitors carrying the product

### 📈 Summary Tab

Statistics dashboard showing:
- Total products per distributor
- In stock / out of stock counts
- Average, min, max prices
- Last updated timestamp

---

## Email Alerts 📧

### Price Drop Alert

Triggered when prices drop more than the threshold (default 10%).

**Example:**
```
Subject: 🚨 5 Solar Panel Price Drop(s) Detected!

💰 Price Drop Alert!
Great news! We found 5 products with significant price drops.

Product: 400W Monocrystalline Solar Panel
Distributor: Solar Cellz USA
$350.00 → $299.00
Save $51.00 (14.6% off!)
[View Product →]
```

### New Products Alert

Sent when new products are detected.

### Stock Change Alert

Notifies when out-of-stock items become available again.

### Weekly Summary

Comprehensive weekly report with:
- Market price trends
- Best deals of the week
- Price movements by distributor
- Inventory statistics

---

## Deployment Options 🚀

### Option 1: Replit (Easiest)

1. Create a new Python Repl
2. Upload all files
3. Add `credentials.json` to Replit
4. Set environment variables in Replit Secrets
5. Run `python scheduled_runner.py`
6. Keep the Repl always on (paid feature)

### Option 2: Cloud VM (AWS, Google Cloud, DigitalOcean)

1. Create a small VM instance
2. Clone your repository
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables
5. Run with systemd or supervisor for auto-restart

**Systemd service example:**
```bash
[Unit]
Description=Solar Inventory Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/product_scrapping
ExecStart=/usr/bin/python3 scheduled_runner.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 3: GitHub Actions (Free)

1. Push code to GitHub
2. Store credentials as GitHub Secrets
3. Create workflow file `.github/workflows/scraper.yml`

```yaml
name: Solar Scraper
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run scraper
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
        run: python main.py
```

### Option 4: Heroku

1. Create `Procfile`:
   ```
   worker: python scheduled_runner.py
   ```
2. Deploy to Heroku
3. Set config vars (environment variables)
4. Scale worker dyno: `heroku ps:scale worker=1`

---

## Troubleshooting 🔧

### Google Sheets Errors

**"Permission denied"**
- Make sure you shared the sheet with the service account email
- Email format: `service-name@project-id.iam.gserviceaccount.com`
- Grant "Editor" permissions

**"Spreadsheet not found"**
- Check `GOOGLE_SHEET_NAME` matches exactly
- Verify credentials are correct

### Scraping Issues

**"No products scraped"**
- Some distributors may use different collection URLs
- Check if the website structure changed
- Try running individual scrapers to debug

**Rate limiting**
- Scrapers include 1-second delays between requests
- If still blocked, increase delay in individual scraper files

### Email Alerts Not Working

**No emails sent**
- Verify SMTP credentials are correct
- For Gmail, use an "App Password" not your regular password
- Check spam folder
- Enable "Less secure app access" (if not using app password)

**Test email configuration:**
```python
from alerting import AlertingSystem
from config import Config

alerting = AlertingSystem(Config.get_smtp_config())
alerting.send_email("Test Alert", "<h1>Test successful!</h1>")
```

---

## Advanced Customization 🛠️

### Adding a New Distributor

1. Create new scraper file in `scrapers/` directory:

```python
from base_scraper import BaseScraper

class NewDistributorScraper(BaseScraper):
    def __init__(self):
        super().__init__("New Distributor")
        self.base_url = "https://example.com"

    def scrape_products(self):
        # Implement scraping logic
        products = []
        # ... scraping code ...
        return products
```

2. Register in `scrapers/__init__.py`
3. Add to `main.py` in `initialize_scrapers()`

### Custom Alert Conditions

Edit `alerting.py` to add custom alert logic:

```python
def send_custom_alert(self, products):
    # Filter for specific conditions
    high_efficiency = [p for p in products if p.get('efficiency') > 22]

    if high_efficiency:
        # Send custom email
        pass
```

### Price History Export

```python
from price_tracker import PriceTracker

tracker = PriceTracker()
trends = tracker.get_price_trends()

# Export to CSV, database, etc.
```

---

## Best Practices 📝

### For Reliable Scraping

1. **Respect rate limits** - Keep delays between requests
2. **Handle errors gracefully** - Don't crash on single failures
3. **Log everything** - Track what's happening
4. **Monitor regularly** - Check if scrapers still work

### For Cost Optimization

1. **Adjust scraping frequency** - 6 hours is usually sufficient
2. **Disable unused distributors** - Only scrape what you need
3. **Use free tiers** - GitHub Actions, Google Cloud free tier
4. **Optimize sheet updates** - Batch operations when possible

### For Better Alerts

1. **Set appropriate thresholds** - Too low = spam, too high = missed deals
2. **Filter by relevance** - Only alert for products you care about
3. **Customize email templates** - Match your business needs
4. **Track alert effectiveness** - Are you acting on them?

---

## FAQ ❓

**Q: How much does it cost to run?**
A: Can be completely free using GitHub Actions + Google Sheets. Email via Gmail is also free.

**Q: How many products can it track?**
A: Google Sheets limit is 5 million cells. With ~15 columns, that's ~300,000 products.

**Q: Can I scrape other product types?**
A: Yes! Modify the collection URLs in each scraper to target different product categories.

**Q: Is this legal?**
A: Scraping public data is generally legal. However, review each site's Terms of Service and robots.txt. Use responsibly.

**Q: What if a website blocks me?**
A: Increase delays between requests, use rotating proxies, or contact the distributor for API access.

**Q: Can I integrate with my CRM?**
A: Yes! Export data from Google Sheets or modify the code to write directly to your CRM.

---

## Support & Contributions 🤝

### Getting Help

1. Check this documentation
2. Review error messages carefully
3. Test individual components (scrapers, sheets, alerts)
4. Check configuration settings

### Contributing

Feel free to:
- Add more distributors
- Improve scraping logic
- Enhance alert templates
- Add new features

---

## License

Free to use and modify for your business needs!

---

## Credits

Built with ❤️ for solar professionals who want to automate their inventory tracking and find the best deals.
