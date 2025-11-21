"""
Document Generator Tool
Generates professional Purchase Orders, Quotes, and Invoices in PDF format

Usage:
    python document_generator.py --type po
    python document_generator.py --type quote
    python document_generator.py --type invoice
"""

import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import argparse


class DocumentGenerator:
    """Base class for document generation"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Company info style
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_LEFT
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

    def get_user_input(self, prompt, default=""):
        """Get user input with optional default value"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()

    def get_items(self):
        """Get line items from user"""
        items = []
        print("\n--- Enter Line Items (press Enter on empty description to finish) ---")

        while True:
            description = input(f"\nItem #{len(items) + 1} Description (or press Enter to finish): ").strip()
            if not description:
                break

            quantity = input("  Quantity: ").strip()
            unit = input("  Unit (e.g., pcs, units, each): ").strip() or "units"
            unit_price = input("  Unit Price ($): ").strip()

            try:
                qty = float(quantity)
                price = float(unit_price)
                total = qty * price

                items.append({
                    'description': description,
                    'quantity': qty,
                    'unit': unit,
                    'unit_price': price,
                    'total': total
                })
                print(f"  ✓ Added: {description} - Total: ${total:.2f}")
            except ValueError:
                print("  ✗ Invalid quantity or price. Item not added.")

        return items

    def create_header(self, story, title, doc_number, date):
        """Create document header"""
        # Title
        title_text = Paragraph(title, self.styles['CustomTitle'])
        story.append(title_text)
        story.append(Spacer(1, 0.2*inch))

        # Document number and date
        info_data = [
            ['Document #:', doc_number],
            ['Date:', date]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.3*inch))

    def create_party_info(self, story, from_info, to_info, from_label="From", to_label="To"):
        """Create from/to party information section"""
        # Create two-column layout for from/to
        party_data = [
            [Paragraph(f"<b>{from_label}:</b>", self.styles['CompanyInfo']),
             Paragraph(f"<b>{to_label}:</b>", self.styles['CompanyInfo'])],
            [Paragraph(from_info.replace('\n', '<br/>'), self.styles['CompanyInfo']),
             Paragraph(to_info.replace('\n', '<br/>'), self.styles['CompanyInfo'])]
        ]

        party_table = Table(party_data, colWidths=[3.5*inch, 3.5*inch])
        party_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        story.append(party_table)
        story.append(Spacer(1, 0.3*inch))

    def create_items_table(self, story, items):
        """Create items table"""
        # Table header
        table_data = [
            ['Description', 'Quantity', 'Unit', 'Unit Price', 'Total']
        ]

        # Add items
        subtotal = 0
        for item in items:
            table_data.append([
                item['description'],
                str(item['quantity']),
                item['unit'],
                f"${item['unit_price']:.2f}",
                f"${item['total']:.2f}"
            ])
            subtotal += item['total']

        # Create table
        items_table = Table(table_data, colWidths=[3*inch, 0.8*inch, 0.7*inch, 1*inch, 1*inch])

        # Style the table
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Alternating row colors
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9'))
              for i in range(2, len(table_data), 2)]
        ]))

        story.append(items_table)
        story.append(Spacer(1, 0.2*inch))

        return subtotal

    def create_totals_section(self, story, subtotal, tax_rate=0, discount=0, shipping=0):
        """Create totals section"""
        tax = subtotal * (tax_rate / 100) if tax_rate > 0 else 0
        total_after_discount = subtotal - discount
        grand_total = total_after_discount + tax + shipping

        totals_data = []

        # Subtotal
        totals_data.append(['Subtotal:', f"${subtotal:.2f}"])

        # Discount if applicable
        if discount > 0:
            totals_data.append(['Discount:', f"-${discount:.2f}"])

        # Tax if applicable
        if tax > 0:
            totals_data.append([f'Tax ({tax_rate}%):', f"${tax:.2f}"])

        # Shipping if applicable
        if shipping > 0:
            totals_data.append(['Shipping:', f"${shipping:.2f}"])

        # Grand total
        totals_data.append(['<b>TOTAL:</b>', f"<b>${grand_total:.2f}</b>"])

        # Create table aligned to the right
        totals_table = Table(totals_data, colWidths=[1.5*inch, 1.5*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2c3e50')),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
        ]))

        # Align table to the right
        totals_wrapper = Table([[totals_table]], colWidths=[7*inch])
        totals_wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))

        story.append(totals_wrapper)
        story.append(Spacer(1, 0.3*inch))

        return grand_total


class PurchaseOrderGenerator(DocumentGenerator):
    """Generate Purchase Orders"""

    def generate(self, output_file=None):
        """Generate a purchase order"""
        print("\n" + "="*60)
        print("PURCHASE ORDER GENERATOR")
        print("="*60)

        # Get document info
        po_number = self.get_user_input("PO Number", f"PO-{datetime.now().strftime('%Y%m%d')}-001")
        po_date = self.get_user_input("PO Date", datetime.now().strftime('%Y-%m-%d'))

        # Get buyer info
        print("\n--- Buyer Information ---")
        buyer_name = self.get_user_input("Buyer Company Name")
        buyer_contact = self.get_user_input("Buyer Contact Person")
        buyer_email = self.get_user_input("Buyer Email")
        buyer_phone = self.get_user_input("Buyer Phone")
        buyer_address = self.get_user_input("Buyer Address")

        buyer_info = f"{buyer_name}\n{buyer_contact}\n{buyer_email}\n{buyer_phone}\n{buyer_address}"

        # Get vendor info
        print("\n--- Vendor Information ---")
        vendor_name = self.get_user_input("Vendor Company Name")
        vendor_contact = self.get_user_input("Vendor Contact Person")
        vendor_email = self.get_user_input("Vendor Email")
        vendor_phone = self.get_user_input("Vendor Phone")
        vendor_address = self.get_user_input("Vendor Address")

        vendor_info = f"{vendor_name}\n{vendor_contact}\n{vendor_email}\n{vendor_phone}\n{vendor_address}"

        # Get items
        items = self.get_items()

        if not items:
            print("No items added. Cancelling...")
            return

        # Get additional details
        print("\n--- Additional Details ---")
        delivery_date = self.get_user_input("Expected Delivery Date")
        payment_terms = self.get_user_input("Payment Terms", "Net 30")
        shipping_method = self.get_user_input("Shipping Method", "Standard")

        # Get optional charges
        tax_rate = float(self.get_user_input("Tax Rate (%)", "0") or "0")
        shipping_cost = float(self.get_user_input("Shipping Cost ($)", "0") or "0")

        # Special instructions
        special_instructions = self.get_user_input("Special Instructions (optional)", "")

        # Generate filename
        if not output_file:
            output_file = f"PO_{po_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.75*inch, rightMargin=0.75*inch)

        story = []

        # Header
        self.create_header(story, "PURCHASE ORDER", po_number, po_date)

        # Party info
        self.create_party_info(story, buyer_info, vendor_info, "Buyer", "Vendor")

        # Delivery and payment info
        delivery_data = [
            ['Expected Delivery:', delivery_date],
            ['Payment Terms:', payment_terms],
            ['Shipping Method:', shipping_method]
        ]

        delivery_table = Table(delivery_data, colWidths=[2*inch, 4*inch])
        delivery_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))

        story.append(delivery_table)
        story.append(Spacer(1, 0.3*inch))

        # Items section
        story.append(Paragraph("Items Ordered", self.styles['SectionHeader']))
        subtotal = self.create_items_table(story, items)

        # Totals
        self.create_totals_section(story, subtotal, tax_rate=tax_rate, shipping=shipping_cost)

        # Special instructions
        if special_instructions:
            story.append(Paragraph("Special Instructions", self.styles['SectionHeader']))
            story.append(Paragraph(special_instructions, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        # Terms and conditions
        story.append(Spacer(1, 0.2*inch))
        terms = """
        <b>Terms and Conditions:</b><br/>
        1. Please confirm receipt of this purchase order within 48 hours.<br/>
        2. All items must be delivered by the specified delivery date.<br/>
        3. Payment will be made according to the agreed payment terms.<br/>
        4. Any changes to this order must be approved in writing.<br/>
        5. Goods must match the specifications outlined in this purchase order.
        """
        story.append(Paragraph(terms, self.styles['Normal']))

        # Signature section
        story.append(Spacer(1, 0.5*inch))
        sig_data = [
            ['Authorized Signature:', '_'*30, 'Date:', '_'*20]
        ]
        sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 0.7*inch, 1.8*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))
        story.append(sig_table)

        # Build PDF
        doc.build(story)

        print(f"\n✓ Purchase Order generated successfully: {output_file}")
        return output_file


class QuoteGenerator(DocumentGenerator):
    """Generate Sales Quotes"""

    def generate(self, output_file=None):
        """Generate a quote"""
        print("\n" + "="*60)
        print("QUOTE GENERATOR")
        print("="*60)

        # Get document info
        quote_number = self.get_user_input("Quote Number", f"QT-{datetime.now().strftime('%Y%m%d')}-001")
        quote_date = self.get_user_input("Quote Date", datetime.now().strftime('%Y-%m-%d'))
        valid_until = self.get_user_input("Valid Until Date")

        # Get company (seller) info
        print("\n--- Your Company Information ---")
        company_name = self.get_user_input("Your Company Name")
        company_contact = self.get_user_input("Contact Person")
        company_email = self.get_user_input("Email")
        company_phone = self.get_user_input("Phone")
        company_address = self.get_user_input("Address")

        company_info = f"{company_name}\n{company_contact}\n{company_email}\n{company_phone}\n{company_address}"

        # Get customer info
        print("\n--- Customer Information ---")
        customer_name = self.get_user_input("Customer Company Name")
        customer_contact = self.get_user_input("Customer Contact Person")
        customer_email = self.get_user_input("Customer Email")
        customer_phone = self.get_user_input("Customer Phone")
        customer_address = self.get_user_input("Customer Address")

        customer_info = f"{customer_name}\n{customer_contact}\n{customer_email}\n{customer_phone}\n{customer_address}"

        # Get items
        items = self.get_items()

        if not items:
            print("No items added. Cancelling...")
            return

        # Get additional details
        print("\n--- Additional Details ---")
        payment_terms = self.get_user_input("Payment Terms", "Due upon receipt")
        delivery_time = self.get_user_input("Estimated Delivery Time", "2-3 weeks")

        # Get optional charges
        discount = float(self.get_user_input("Discount Amount ($)", "0") or "0")
        tax_rate = float(self.get_user_input("Tax Rate (%)", "0") or "0")
        shipping_cost = float(self.get_user_input("Shipping Cost ($)", "0") or "0")

        # Notes
        notes = self.get_user_input("Additional Notes (optional)", "")

        # Generate filename
        if not output_file:
            output_file = f"Quote_{quote_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.75*inch, rightMargin=0.75*inch)

        story = []

        # Header
        self.create_header(story, "QUOTATION", quote_number, quote_date)

        # Valid until
        valid_text = Paragraph(f"<b>Valid Until:</b> {valid_until}", self.styles['Normal'])
        story.append(valid_text)
        story.append(Spacer(1, 0.2*inch))

        # Party info
        self.create_party_info(story, company_info, customer_info, "From", "To")

        # Items section
        story.append(Paragraph("Quoted Items", self.styles['SectionHeader']))
        subtotal = self.create_items_table(story, items)

        # Totals
        grand_total = self.create_totals_section(story, subtotal, tax_rate=tax_rate,
                                                 discount=discount, shipping=shipping_cost)

        # Quote details
        story.append(Spacer(1, 0.2*inch))
        details_data = [
            ['Payment Terms:', payment_terms],
            ['Estimated Delivery:', delivery_time]
        ]

        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))

        story.append(details_table)
        story.append(Spacer(1, 0.3*inch))

        # Additional notes
        if notes:
            story.append(Paragraph("Additional Notes", self.styles['SectionHeader']))
            story.append(Paragraph(notes, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        # Terms
        story.append(Spacer(1, 0.2*inch))
        terms = """
        <b>Terms and Conditions:</b><br/>
        1. This quote is valid until the date specified above.<br/>
        2. Prices are subject to change after the expiration date.<br/>
        3. Payment terms as specified must be met.<br/>
        4. Delivery times are estimates and may vary based on availability.<br/>
        5. Please contact us to accept this quote and proceed with the order.
        """
        story.append(Paragraph(terms, self.styles['Normal']))

        # Build PDF
        doc.build(story)

        print(f"\n✓ Quote generated successfully: {output_file}")
        return output_file


class InvoiceGenerator(DocumentGenerator):
    """Generate Invoices"""

    def generate(self, output_file=None):
        """Generate an invoice"""
        print("\n" + "="*60)
        print("INVOICE GENERATOR")
        print("="*60)

        # Get document info
        invoice_number = self.get_user_input("Invoice Number", f"INV-{datetime.now().strftime('%Y%m%d')}-001")
        invoice_date = self.get_user_input("Invoice Date", datetime.now().strftime('%Y-%m-%d'))
        due_date = self.get_user_input("Due Date")

        # Get company (seller) info
        print("\n--- Your Company Information ---")
        company_name = self.get_user_input("Your Company Name")
        company_contact = self.get_user_input("Contact Person")
        company_email = self.get_user_input("Email")
        company_phone = self.get_user_input("Phone")
        company_address = self.get_user_input("Address")

        company_info = f"{company_name}\n{company_contact}\n{company_email}\n{company_phone}\n{company_address}"

        # Get customer info
        print("\n--- Bill To Information ---")
        customer_name = self.get_user_input("Customer Company Name")
        customer_contact = self.get_user_input("Customer Contact Person")
        customer_email = self.get_user_input("Customer Email")
        customer_phone = self.get_user_input("Customer Phone")
        customer_address = self.get_user_input("Customer Address")

        customer_info = f"{customer_name}\n{customer_contact}\n{customer_email}\n{customer_phone}\n{customer_address}"

        # Get items
        items = self.get_items()

        if not items:
            print("No items added. Cancelling...")
            return

        # Get additional details
        print("\n--- Additional Details ---")
        payment_terms = self.get_user_input("Payment Terms", "Net 30")
        po_number = self.get_user_input("Customer PO Number (optional)", "")

        # Get optional charges
        discount = float(self.get_user_input("Discount Amount ($)", "0") or "0")
        tax_rate = float(self.get_user_input("Tax Rate (%)", "0") or "0")
        shipping_cost = float(self.get_user_input("Shipping Cost ($)", "0") or "0")

        # Payment instructions
        print("\n--- Payment Information ---")
        bank_name = self.get_user_input("Bank Name (optional)", "")
        account_number = self.get_user_input("Account Number (optional)", "")
        routing_number = self.get_user_input("Routing Number (optional)", "")

        # Notes
        notes = self.get_user_input("Additional Notes (optional)", "")

        # Generate filename
        if not output_file:
            output_file = f"Invoice_{invoice_number.replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.75*inch, rightMargin=0.75*inch)

        story = []

        # Header
        self.create_header(story, "INVOICE", invoice_number, invoice_date)

        # Due date
        due_text = Paragraph(f"<b style='color: #d9534f;'>Due Date: {due_date}</b>", self.styles['Normal'])
        story.append(due_text)
        story.append(Spacer(1, 0.2*inch))

        # Party info
        self.create_party_info(story, company_info, customer_info, "From", "Bill To")

        # PO Number if provided
        if po_number:
            po_text = Paragraph(f"<b>Customer PO#:</b> {po_number}", self.styles['Normal'])
            story.append(po_text)
            story.append(Spacer(1, 0.2*inch))

        # Items section
        story.append(Paragraph("Invoice Items", self.styles['SectionHeader']))
        subtotal = self.create_items_table(story, items)

        # Totals
        grand_total = self.create_totals_section(story, subtotal, tax_rate=tax_rate,
                                                 discount=discount, shipping=shipping_cost)

        # Payment terms
        story.append(Spacer(1, 0.2*inch))
        terms_text = Paragraph(f"<b>Payment Terms:</b> {payment_terms}", self.styles['Normal'])
        story.append(terms_text)
        story.append(Spacer(1, 0.2*inch))

        # Payment information
        if bank_name or account_number:
            story.append(Paragraph("Payment Information", self.styles['SectionHeader']))
            payment_info = []
            if bank_name:
                payment_info.append(f"Bank: {bank_name}")
            if account_number:
                payment_info.append(f"Account: {account_number}")
            if routing_number:
                payment_info.append(f"Routing: {routing_number}")

            payment_text = Paragraph("<br/>".join(payment_info), self.styles['Normal'])
            story.append(payment_text)
            story.append(Spacer(1, 0.2*inch))

        # Additional notes
        if notes:
            story.append(Paragraph("Notes", self.styles['SectionHeader']))
            story.append(Paragraph(notes, self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))

        # Footer message
        story.append(Spacer(1, 0.3*inch))
        footer = Paragraph(
            "<i>Thank you for your business!</i>",
            self.styles['Normal']
        )
        story.append(footer)

        # Build PDF
        doc.build(story)

        print(f"\n✓ Invoice generated successfully: {output_file}")
        return output_file


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Generate professional Purchase Orders, Quotes, and Invoices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python document_generator.py --type po
  python document_generator.py --type quote
  python document_generator.py --type invoice
  python document_generator.py --type po --output my_purchase_order.pdf
        """
    )

    parser.add_argument(
        '--type',
        choices=['po', 'quote', 'invoice'],
        required=True,
        help='Type of document to generate (po=Purchase Order, quote=Quote, invoice=Invoice)'
    )

    parser.add_argument(
        '--output',
        help='Output PDF filename (optional, will auto-generate if not provided)'
    )

    args = parser.parse_args()

    # Generate document based on type
    if args.type == 'po':
        generator = PurchaseOrderGenerator()
    elif args.type == 'quote':
        generator = QuoteGenerator()
    else:  # invoice
        generator = InvoiceGenerator()

    try:
        generator.generate(args.output)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error generating document: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
