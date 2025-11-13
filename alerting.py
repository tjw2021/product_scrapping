"""
Email Alerting System
Sends email notifications for price drops, stock changes, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os
from datetime import datetime


class AlertingSystem:
    """Send email alerts for important changes"""

    def __init__(self, smtp_config: Dict = None):
        """
        Initialize alerting system
        smtp_config should contain: server, port, username, password, from_email, to_email
        """
        self.smtp_config = smtp_config or self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get SMTP config from environment variables"""
        return {
            'server': os.environ.get('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.environ.get('SMTP_PORT', '587')),
            'username': os.environ.get('SMTP_USERNAME', ''),
            'password': os.environ.get('SMTP_PASSWORD', ''),
            'from_email': os.environ.get('ALERT_FROM_EMAIL', ''),
            'to_email': os.environ.get('ALERT_TO_EMAIL', '')
        }

    def send_email(self, subject: str, body_html: str):
        """Send email alert"""
        if not self.smtp_config.get('username') or not self.smtp_config.get('to_email'):
            print("⚠️ Email alerts not configured. Set SMTP environment variables.")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['from_email'] or self.smtp_config['username']
            msg['To'] = self.smtp_config['to_email']

            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)

            print(f"✅ Email alert sent: {subject}")
            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def send_price_drop_alert(self, price_drops: List[Dict]):
        """Send alert for significant price drops"""
        if not price_drops:
            return

        subject = f"🚨 {len(price_drops)} Solar Panel Price Drop(s) Detected!"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #2ecc71; color: white; padding: 20px; }}
                .product {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
                .savings {{ color: #27ae60; font-weight: bold; font-size: 18px; }}
                .price {{ font-size: 16px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💰 Price Drop Alert!</h1>
                <p>Great news! We found {len(price_drops)} products with significant price drops.</p>
            </div>
        """

        for drop in price_drops[:10]:  # Top 10 drops
            product = drop['product']
            html += f"""
            <div class="product">
                <h3>{product['title']}</h3>
                <p><strong>Distributor:</strong> {product['distributor']}</p>
                <p class="price">
                    <strike>${drop['old_price']:.2f}</strike> →
                    <strong>${drop['new_price']:.2f}</strong>
                </p>
                <p class="savings">
                    Save ${drop['savings']:.2f} ({drop['percentage']:.1f}% off!)
                </p>
                <p><a href="{product['product_url']}">View Product →</a></p>
            </div>
            """

        html += """
        </body>
        </html>
        """

        self.send_email(subject, html)

    def send_new_products_alert(self, new_products: List[Dict]):
        """Send alert for new products"""
        if not new_products:
            return

        subject = f"🆕 {len(new_products)} New Solar Product(s) Available!"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #3498db; color: white; padding: 20px; }}
                .product {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🆕 New Products Alert!</h1>
                <p>We found {len(new_products)} new products in the inventory.</p>
            </div>
        """

        for product in new_products[:10]:  # Top 10 new products
            html += f"""
            <div class="product">
                <h3>{product['title']}</h3>
                <p><strong>Distributor:</strong> {product['distributor']}</p>
                <p><strong>Price:</strong> ${product['price']:.2f}</p>
                <p><strong>Status:</strong> {product['stock_status']}</p>
                <p><a href="{product['product_url']}">View Product →</a></p>
            </div>
            """

        html += """
        </body>
        </html>
        """

        self.send_email(subject, html)

    def send_stock_change_alert(self, stock_changes: List[Dict]):
        """Send alert for stock status changes"""
        if not stock_changes:
            return

        # Only alert for items coming back in stock
        back_in_stock = [
            change for change in stock_changes
            if change['new_stock'] == 'In Stock' and change['old_stock'] != 'In Stock'
        ]

        if not back_in_stock:
            return

        subject = f"📦 {len(back_in_stock)} Product(s) Back in Stock!"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #e74c3c; color: white; padding: 20px; }}
                .product {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📦 Stock Alert!</h1>
                <p>{len(back_in_stock)} products are now back in stock!</p>
            </div>
        """

        for change in back_in_stock[:10]:
            product = change['product']
            html += f"""
            <div class="product">
                <h3>{product['title']}</h3>
                <p><strong>Distributor:</strong> {product['distributor']}</p>
                <p><strong>Price:</strong> ${product['price']:.2f}</p>
                <p><strong>Status:</strong> {change['old_stock']} → {change['new_stock']}</p>
                <p><a href="{product['product_url']}">Order Now →</a></p>
            </div>
            """

        html += """
        </body>
        </html>
        """

        self.send_email(subject, html)

    def send_weekly_summary(self, summary_data: Dict):
        """Send weekly summary report"""
        subject = f"📊 Weekly Solar Inventory Report - {datetime.now().strftime('%Y-%m-%d')}"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #34495e; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #3498db; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Weekly Solar Inventory Summary</h1>
                <p>Week of {summary_data.get('week_start', '')} to {summary_data.get('week_end', '')}</p>
            </div>

            <div class="section">
                <h2>📈 Market Overview</h2>
                <table>
                    <tr>
                        <th>Distributor</th>
                        <th>Total Products</th>
                        <th>Avg Price</th>
                        <th>Price Trend</th>
                    </tr>
        """

        for dist_name, stats in summary_data.get('distributors', {}).items():
            trend_icon = "📉" if stats.get('price_trend', 0) < 0 else "📈" if stats.get('price_trend', 0) > 0 else "➡️"
            html += f"""
                    <tr>
                        <td>{dist_name}</td>
                        <td>{stats.get('total_products', 0)}</td>
                        <td>${stats.get('avg_price', 0):.2f}</td>
                        <td>{trend_icon} {abs(stats.get('price_trend', 0)):.1f}%</td>
                    </tr>
            """

        html += """
                </table>
            </div>

            <div class="section">
                <h2>💰 Best Deals This Week</h2>
                <ul>
        """

        for deal in summary_data.get('best_deals', [])[:5]:
            html += f"""
                    <li>
                        <strong>{deal['title']}</strong><br>
                        ${deal['price']:.2f} at {deal['distributor']}
                    </li>
            """

        html += """
                </ul>
            </div>
        </body>
        </html>
        """

        self.send_email(subject, html)
