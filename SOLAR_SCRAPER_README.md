# Solar Equipment Scraper System

A comprehensive Python-based system for scraping solar equipment data from multiple distributor websites, matching products against Approved Vendor Lists (AVLs), and exporting organized data to Excel.

## 🌟 Features

- **Multi-Distributor Support**: Scrape from 8+ solar equipment distributors
- **AVL Matching**: Automatic matching against THRIVE and GOODLEAP AVLs
- **Domestic Content Identification**: Identifies products qualifying for domestic content incentives
- **Organized Excel Export**: Separate sheets by equipment category with formatting
- **Spec Sheet Downloads**: Optional PDF specification sheet downloads
- **Product Categorization**: Automatic categorization into Solar Panels, Inverters, Batteries, etc.
- **Price Per Unit Calculation**: Handles bulk quantities and calculates per-unit pricing
- **Warehouse Inventory**: Track inventory across multiple warehouse locations (Soligent)
- **Dropship & Backorder Tracking**: Identifies dropship items and delivery dates

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [AVL Files](#avl-files)
- [Output Format](#output-format)
- [Supported Distributors](#supported-distributors)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- `pandas` - Data processing
- `openpyxl` - Excel export
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `pyyaml` - Configuration files
- `tqdm` - Progress bars

## ⚡ Quick Start

### 1. Create AVL Files

First, generate example AVL files:

```bash
python create_example_avl_files.py
```

This creates:
- `THRIVE_AVL.xlsx` - THRIVE approved vendor list
- `GOODLEAP_AVL.xlsx` - GOODLEAP approved vendor list

**Replace these with your actual AVL files before production use!**

### 2. Configure Settings

Edit `scraper_config.yaml` to enable/disable distributors and features:

```yaml
distributors:
  solar_cellz:
    enabled: true
  soligent:
    enabled: true
  # ... etc

avl:
  enabled: true
  thrive_file: "THRIVE_AVL.xlsx"
  goodleap_file: "GOODLEAP_AVL.xlsx"

spec_sheets:
  enabled: false  # Set to true to download PDFs
```

### 3. Run the Scraper

```bash
python solar_equipment_scraper.py
```

### 4. Check Output

Results are saved to `output/solar_equipment_database_YYYYMMDD_HHMMSS.xlsx`

## ⚙️ Configuration

### Configuration File: `scraper_config.yaml`

#### Distributor Selection

Enable or disable specific distributors:

```yaml
distributors:
  solar_cellz:
    enabled: true
    name: "Solar Cellz USA"
    type: "shopify"

  soligent:
    enabled: true
    requires_auth: true  # Set SOLIGENT_USERNAME and SOLIGENT_PASSWORD env vars
```

#### AVL Settings

```yaml
avl:
  enabled: true
  thrive_file: "THRIVE_AVL.xlsx"
  goodleap_file: "GOODLEAP_AVL.xlsx"
```

#### Spec Sheet Downloads

```yaml
spec_sheets:
  enabled: false  # Set to true to enable
  output_directory: "spec_sheets"
  max_pdfs_per_product: 3
  delay_between_downloads: 1.0
```

#### Excel Export Settings

```yaml
output:
  excel:
    enabled: true
    directory: "./output"
    filename_pattern: "solar_equipment_database_{timestamp}.xlsx"
    include_summary_sheet: true
    include_domestic_only_sheet: true
```

## 📊 AVL Files

### THRIVE AVL Structure

Required columns:
- `Manufacturer` - Manufacturer name (e.g., "Canadian Solar")
- `Model` - Model number (e.g., "CS3W-400MS")
- `Domestic Content` - "Yes" or "No"

**Matching Logic:**
- Exact manufacturer + model match → Approved + Domestic flag
- Manufacturer only match → Approved (no domestic flag)
- No match → Not approved

### GOODLEAP AVL Structure

Required columns:
- `Manufacturer` - Manufacturer name
- `Program Type` - "Loans/Leases/PPAs" or "Loans Only"
- `Domestic Content` - "Yes" or "No"

**Matching Logic:**
- Manufacturer-level matching (no model required)
- Returns program type and domestic content flag

### Example AVL Entry

**THRIVE_AVL.xlsx:**
```
Manufacturer    | Model           | Domestic Content
Canadian Solar  | CS3W-400MS      | No
Silfab         | SIL-380-BX      | Yes
```

**GOODLEAP_AVL.xlsx:**
```
Manufacturer    | Program Type         | Domestic Content
Canadian Solar  | Loans/Leases/PPAs    | No
Silfab         | Loans/Leases/PPAs    | Yes
```

## 📁 Output Format

### Excel Workbook Structure

The output Excel file contains multiple sheets:

1. **Solar Panel** - All solar panels/modules
2. **Inverter** - String inverters, microinverters, etc.
3. **Battery/Storage** - Battery systems
4. **Charge Controller** - MPPT and PWM controllers
5. **Transformer** - Pad-mount transformers with KVA ratings
6. **Switch** - Disconnects and switches
7. **Racking/Mounting** - Mounting hardware
8. **BOS/Electrical** - Balance of system components
9. **Other** - Uncategorized products
10. **Domestic Content** - All domestic content products
11. **All Products** - Complete dataset
12. **Summary** - Statistics by category

### Column Structure

| Column | Description |
|--------|-------------|
| Distributor | Source distributor name |
| Category | Equipment category |
| Manufacturer | Brand/manufacturer |
| Model/SKU | Model number or SKU |
| Product Title | Full product name |
| Wattage | Power rating (for applicable products) |
| Price Per Unit | Price per individual unit |
| Total Price | Total price (for bulk items) |
| Quantity | Number of units (for bulk sales) |
| Stock Status | In Stock, Dropship, Backorder, etc. |
| Inventory Qty | Available quantity |
| Product URL | Link to product page |
| THRIVE Approved | Yes/No |
| THRIVE Domestic | Yes/No |
| GOODLEAP Approved | Yes/No |
| GOODLEAP Domestic | Yes/No |
| GOODLEAP Program | Loans/Leases/PPAs or Loans Only |
| On Any AVL | Yes if on either AVL |
| Domestic Content | Yes if qualifies for domestic content |
| Last Updated | Timestamp of scrape |

### Formatting Features

- **Color-coded headers** - Blue headers with white text
- **Auto-sized columns** - Readable width for all data
- **Frozen header row** - Headers stay visible while scrolling
- **Summary totals** - Highlighted in yellow
- **Formatted prices** - Currency formatting ($XX.XX)
- **Boolean fields** - Yes/No instead of True/False

## 🏪 Supported Distributors

| Distributor | Type | Status | Notes |
|-------------|------|--------|-------|
| Solar Cellz USA | Shopify | ✅ Active | Full API access |
| Soligent | NetSuite API | ✅ Active | Requires auth for warehouse inventory |
| Giga Energy | HTML | ✅ Active | Transformers specialty |
| altE Store | Shopify | ✅ Active | |
| Ressupply | Shopify | ✅ Active | |
| US Solar Supplier | Shopify | ✅ Active | |
| The Solar Store | Shopify | ✅ Active | |
| Essential Parts | HTML | ⚠️ Limited | Requires Cloudflare bypass |
| Rexel | HTML | 🔧 Development | |

## 🔧 Advanced Usage

### Authentication for Soligent

Soligent requires authentication for warehouse inventory data:

```bash
export SOLIGENT_USERNAME="your_username"
export SOLIGENT_PASSWORD="your_password"
```

Or create a `.env` file:

```
SOLIGENT_USERNAME=your_username
SOLIGENT_PASSWORD=your_password
```

### Programmatic Usage

```python
from solar_equipment_scraper import SolarEquipmentScraper

# Initialize with config
scraper = SolarEquipmentScraper('scraper_config.yaml')

# Run scraping
results_df = scraper.run()

# Access results
print(f"Total products: {len(results_df)}")
print(f"Domestic content: {results_df['domestic_content_qualified'].sum()}")

# Filter for specific category
solar_panels = results_df[results_df['category'] == 'Solar Panel']
```

### Custom AVL Matching

```python
from avl_handler import AVLHandler

# Initialize
avl = AVLHandler('THRIVE_AVL.xlsx', 'GOODLEAP_AVL.xlsx')

# Check individual product
result = avl.check_thrive_approval('Canadian Solar', 'CS3W-400MS')
print(f"Approved: {result['approved']}")
print(f"Domestic: {result['domestic']}")

# Check manufacturer only
result = avl.check_goodleap_approval('Enphase')
print(f"Program: {result['program']}")
```

### Spec Sheet Downloads

```python
from spec_sheet_downloader import SpecSheetDownloader

# Initialize
downloader = SpecSheetDownloader(output_dir='spec_sheets')

# Download for single product
product = {
    'product_url': 'https://example.com/product',
    'sku': 'CS3W-400MS',
    'title': 'Solar Panel'
}

downloaded_files = downloader.download_for_product(product)
print(f"Downloaded {len(downloaded_files)} PDFs")
```

### Excel Export Only

```python
from excel_exporter import ExcelExporter
import pandas as pd

# Load existing data
df = pd.read_csv('products.csv')

# Export to Excel
exporter = ExcelExporter('output.xlsx')
exporter.export_by_category(df)
```

## 🐛 Troubleshooting

### No Products Scraped

**Issue:** Scraper returns 0 products

**Solutions:**
1. Check internet connection
2. Verify distributor websites are accessible
3. Check if website structure has changed
4. Enable debug logging in config

### AVL Matching Not Working

**Issue:** All products show "No" for AVL approval

**Solutions:**
1. Verify AVL files exist in correct location
2. Check AVL file column names match exactly:
   - `Manufacturer`, `Model`, `Domestic Content`
3. Ensure manufacturer names match between products and AVL
4. Check for extra spaces or special characters

### Spec Sheets Not Downloading

**Issue:** PDF downloads fail

**Solutions:**
1. Verify spec sheets are enabled in config
2. Check product pages actually have PDF links
3. Verify write permissions for spec_sheets directory
4. Some distributors may block automated downloads

### Soligent Authentication Issues

**Issue:** Warehouse inventory not loading

**Solutions:**
1. Verify credentials are set correctly
2. Check if account has API access
3. Try logging into website manually first
4. Contact Soligent support for API access

### Excel File Won't Open

**Issue:** Excel file is corrupted or won't open

**Solutions:**
1. Ensure openpyxl is installed correctly
2. Check disk space availability
3. Verify output directory has write permissions
4. Try exporting to different location

## 📝 File Structure

```
product_scrapping/
├── solar_equipment_scraper.py    # Main system
├── avl_handler.py                # AVL matching logic
├── spec_sheet_downloader.py      # PDF downloader
├── excel_exporter.py             # Excel export
├── base_scraper.py               # Base scraper class
├── scraper_config.yaml           # Configuration
├── requirements.txt              # Dependencies
├── create_example_avl_files.py   # AVL file generator
├── THRIVE_AVL.xlsx              # THRIVE AVL (generated)
├── GOODLEAP_AVL.xlsx            # GOODLEAP AVL (generated)
├── scrapers/                    # Individual scrapers
│   ├── __init__.py
│   ├── solar_cellz_scraper.py
│   ├── soligent_scraper.py
│   ├── giga_energy_scraper.py
│   └── ...
├── output/                      # Excel output files
└── spec_sheets/                 # Downloaded PDFs
```

## 🎯 Best Practices

1. **Start Small**: Enable 1-2 distributors first to test
2. **Update AVL Files**: Keep AVL files current for accurate matching
3. **Rate Limiting**: Be respectful with request frequency
4. **Verify Output**: Check first few rows of output for accuracy
5. **Regular Updates**: Run scraper on schedule for price tracking
6. **Backup Data**: Keep historical exports for price trends
7. **Monitor Changes**: Distributor websites may change structure

## 📞 Support

For issues or questions:
1. Check this README
2. Review configuration settings
3. Enable debug logging
4. Check individual scraper logs

## 🔄 Updates

### Adding New Distributors

1. Create new scraper class inheriting from `BaseScraper`
2. Implement `scrape_products()` method
3. Add to `scrapers/__init__.py`
4. Add to `solar_equipment_scraper.py` scraper map
5. Add to config file

### Updating AVL Files

Simply replace `THRIVE_AVL.xlsx` or `GOODLEAP_AVL.xlsx` with updated versions. Ensure column names match the required structure.

## 📄 License

This project is for internal use. Respect distributor terms of service and robots.txt files.

## 🙏 Acknowledgments

Built for solar industry professionals to streamline equipment sourcing and pricing.

---

**Last Updated:** November 2025
**Version:** 2.0
