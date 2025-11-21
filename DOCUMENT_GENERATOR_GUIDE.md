# Document Generator Tool

A professional tool for generating Purchase Orders, Quotes, and Invoices in PDF format.

## Features

- **Purchase Order Generator** - Create professional POs with buyer/vendor information, line items, terms, and signatures
- **Quote Generator** - Generate sales quotes with pricing, validity dates, and terms
- **Invoice Generator** - Create invoices with payment terms, due dates, and banking information
- **Professional PDF Output** - Clean, well-formatted documents with tables and branding
- **Interactive CLI** - Easy-to-use command-line interface with prompts
- **Customizable** - Add line items, tax, shipping, discounts, and special instructions

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

This will install `reportlab` for PDF generation.

## Usage

### Quick Start

Generate a Purchase Order:
```bash
python document_generator.py --type po
```

Generate a Quote:
```bash
python document_generator.py --type quote
```

Generate an Invoice:
```bash
python document_generator.py --type invoice
```

### Command-Line Options

- `--type` (required): Type of document to generate
  - `po` - Purchase Order
  - `quote` - Sales Quote
  - `invoice` - Invoice

- `--output` (optional): Specify output filename
  ```bash
  python document_generator.py --type po --output my_custom_po.pdf
  ```

If no output filename is provided, the tool will auto-generate one based on the document type and number.

## Interactive Prompts

The tool will guide you through entering all necessary information:

### Purchase Order Fields
1. **Document Information**
   - PO Number (auto-generated default)
   - PO Date (today's date default)

2. **Buyer Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

3. **Vendor Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

4. **Line Items** (can add multiple)
   - Description
   - Quantity
   - Unit (pcs, units, each, etc.)
   - Unit Price
   - (Total calculated automatically)

5. **Additional Details**
   - Expected Delivery Date
   - Payment Terms (default: Net 30)
   - Shipping Method (default: Standard)
   - Tax Rate (%)
   - Shipping Cost ($)
   - Special Instructions (optional)

### Quote Fields
1. **Document Information**
   - Quote Number (auto-generated default)
   - Quote Date (today's date default)
   - Valid Until Date

2. **Your Company Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

3. **Customer Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

4. **Line Items** (same as PO)

5. **Additional Details**
   - Payment Terms (default: Due upon receipt)
   - Estimated Delivery Time (default: 2-3 weeks)
   - Discount Amount ($)
   - Tax Rate (%)
   - Shipping Cost ($)
   - Additional Notes (optional)

### Invoice Fields
1. **Document Information**
   - Invoice Number (auto-generated default)
   - Invoice Date (today's date default)
   - Due Date

2. **Your Company Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

3. **Bill To Information**
   - Company Name
   - Contact Person
   - Email
   - Phone
   - Address

4. **Line Items** (same as PO)

5. **Additional Details**
   - Payment Terms (default: Net 30)
   - Customer PO Number (optional)
   - Discount Amount ($)
   - Tax Rate (%)
   - Shipping Cost ($)

6. **Payment Information** (optional)
   - Bank Name
   - Account Number
   - Routing Number
   - Additional Notes

## Example Workflow

### Creating a Purchase Order

```bash
$ python document_generator.py --type po

============================================================
PURCHASE ORDER GENERATOR
============================================================

PO Number [PO-20251121-001]: PO-2025-001
PO Date [2025-11-21]:

--- Buyer Information ---
Buyer Company Name: Solar Solutions Inc.
Buyer Contact Person: John Smith
Buyer Email: john@solarsolutions.com
Buyer Phone: (555) 123-4567
Buyer Address: 123 Solar Street, Phoenix, AZ 85001

--- Vendor Information ---
Vendor Company Name: Panel Distributors LLC
Vendor Contact Person: Jane Doe
Vendor Email: jane@paneldist.com
Vendor Phone: (555) 987-6543
Vendor Address: 456 Supply Ave, Los Angeles, CA 90001

--- Enter Line Items (press Enter on empty description to finish) ---

Item #1 Description (or press Enter to finish): Solar Panel - 400W Monocrystalline
  Quantity: 100
  Unit (e.g., pcs, units, each): pcs
  Unit Price ($): 125.50
  ✓ Added: Solar Panel - 400W Monocrystalline - Total: $12550.00

Item #2 Description (or press Enter to finish): Inverter - 10kW String
  Quantity: 10
  Unit (e.g., pcs, units, each): units
  Unit Price ($): 1850.00
  ✓ Added: Inverter - 10kW String - Total: $18500.00

Item #3 Description (or press Enter to finish):

--- Additional Details ---
Expected Delivery Date: 2025-12-15
Payment Terms [Net 30]: Net 30
Shipping Method [Standard]: Freight
Tax Rate (%) [0]: 8.5
Shipping Cost ($) [0]: 500
Special Instructions (optional): Please deliver to warehouse dock. Contact 24hrs before delivery.

✓ Purchase Order generated successfully: PO_PO-2025-001_20251121.pdf
```

## Output

The tool generates professional PDF documents with:

- **Clean, modern design** with professional typography
- **Well-organized tables** for line items with alternating row colors
- **Automatic calculations** for subtotals, taxes, discounts, and totals
- **Clear sections** for all parties' information
- **Terms and conditions** appropriate for each document type
- **Signature blocks** (for Purchase Orders)
- **Professional formatting** suitable for business use

## Sample Generated Documents

### Purchase Order includes:
- PO number and date
- Buyer and vendor information
- Itemized list with quantities and pricing
- Delivery details and shipping method
- Payment terms
- Tax and shipping calculations
- Total amount
- Special instructions
- Terms and conditions
- Signature block

### Quote includes:
- Quote number and date
- Valid until date
- Company and customer information
- Itemized pricing
- Discount, tax, and shipping
- Total quoted amount
- Payment terms and delivery estimates
- Terms and conditions

### Invoice includes:
- Invoice number and date
- Due date (highlighted)
- Company and customer information
- Reference to customer PO (if applicable)
- Itemized charges
- Discount, tax, and shipping
- Total amount due
- Payment terms
- Banking information for payment
- Thank you message

## Tips

1. **Auto-generated Numbers**: The tool suggests document numbers based on today's date (e.g., PO-20251121-001). You can use this or enter your own numbering scheme.

2. **Default Values**: Many fields have sensible defaults shown in brackets [like this]. Just press Enter to accept the default.

3. **Line Items**: Add as many line items as needed. Press Enter without typing a description when you're done adding items.

4. **Optional Fields**: Fields marked as (optional) can be left blank by pressing Enter.

5. **Cancellation**: Press Ctrl+C at any time to cancel document generation.

6. **File Naming**: If you don't specify an output filename, the tool automatically generates one based on the document type and number.

## Customization

The tool uses professional styling with:
- Dark blue header backgrounds (#2c3e50)
- Clean typography (Helvetica)
- Alternating row colors for readability
- Proper spacing and margins
- Professional color scheme

You can customize the appearance by editing the `setup_custom_styles()` method in `document_generator.py`.

## Programmatic Usage

You can also use the generators programmatically in your own Python scripts:

```python
from document_generator import PurchaseOrderGenerator, QuoteGenerator, InvoiceGenerator

# Generate a PO programmatically
generator = PurchaseOrderGenerator()
generator.generate(output_file="custom_po.pdf")

# Or for quotes
quote_gen = QuoteGenerator()
quote_gen.generate()

# Or for invoices
invoice_gen = InvoiceGenerator()
invoice_gen.generate(output_file="invoice_2025.pdf")
```

## Troubleshooting

### "reportlab module not found"
Install dependencies:
```bash
pip install reportlab
```

### "Permission denied" error
Make sure you have write permissions in the current directory, or specify a different output path:
```bash
python document_generator.py --type po --output /path/to/output/file.pdf
```

### PDF won't open
Ensure the document generation completed successfully. Check for any error messages during generation.

## Support

For issues or questions:
1. Check this guide
2. Review the examples above
3. Ensure all dependencies are installed
4. Verify you have write permissions in the output directory

## Future Enhancements

Potential features for future versions:
- Logo upload and placement
- Custom color schemes
- Template selection
- Batch generation from CSV/Excel
- Email integration
- Digital signatures
- Multi-currency support
- Custom fields and branding

---

**Version**: 1.0
**Last Updated**: 2025-11-21
**Author**: Solar Inventory Team
