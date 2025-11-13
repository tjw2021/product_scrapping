"""
Price History Tracker
Tracks price changes over time and detects significant changes
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple


class PriceTracker:
    """Track price history and detect changes"""

    def __init__(self, history_file: str = 'price_history.json'):
        self.history_file = history_file
        self.history = self.load_history()

    def load_history(self) -> Dict:
        """Load price history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading price history: {e}")
                return {}
        return {}

    def save_history(self):
        """Save price history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving price history: {e}")

    def get_product_key(self, product: Dict) -> str:
        """Generate unique key for product"""
        return f"{product['distributor']}_{product['sku']}_{product['product_id']}"

    def track_products(self, products: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Track new products and detect changes
        Returns dict with: price_drops, price_increases, new_products, stock_changes
        """
        changes = {
            'price_drops': [],
            'price_increases': [],
            'new_products': [],
            'stock_changes': []
        }

        for product in products:
            key = self.get_product_key(product)
            current_price = product.get('price', 0)
            current_stock = product.get('stock_status', 'Unknown')

            if key in self.history:
                # Existing product - check for changes
                old_data = self.history[key]
                old_price = old_data.get('price', 0)
                old_stock = old_data.get('stock_status', 'Unknown')

                # Check price changes
                if old_price > 0 and current_price > 0:
                    price_diff = old_price - current_price
                    price_change_pct = (price_diff / old_price) * 100

                    if price_change_pct > 10:  # Price dropped more than 10%
                        changes['price_drops'].append({
                            'product': product,
                            'old_price': old_price,
                            'new_price': current_price,
                            'savings': price_diff,
                            'percentage': price_change_pct
                        })
                    elif price_change_pct < -10:  # Price increased more than 10%
                        changes['price_increases'].append({
                            'product': product,
                            'old_price': old_price,
                            'new_price': current_price,
                            'increase': abs(price_diff),
                            'percentage': abs(price_change_pct)
                        })

                # Check stock changes
                if old_stock != current_stock:
                    changes['stock_changes'].append({
                        'product': product,
                        'old_stock': old_stock,
                        'new_stock': current_stock
                    })

                # Update history
                self.history[key] = {
                    'price': current_price,
                    'stock_status': current_stock,
                    'title': product.get('title'),
                    'distributor': product.get('distributor'),
                    'last_updated': product.get('last_updated'),
                    'price_history': old_data.get('price_history', []) + [{
                        'date': product.get('last_updated'),
                        'price': current_price
                    }][-30:]  # Keep last 30 price points
                }

            else:
                # New product
                changes['new_products'].append(product)

                self.history[key] = {
                    'price': current_price,
                    'stock_status': current_stock,
                    'title': product.get('title'),
                    'distributor': product.get('distributor'),
                    'last_updated': product.get('last_updated'),
                    'price_history': [{
                        'date': product.get('last_updated'),
                        'price': current_price
                    }]
                }

        # Save updated history
        self.save_history()

        return changes

    def get_price_trends(self) -> List[Dict]:
        """Analyze price trends across all tracked products"""
        trends = []

        for key, data in self.history.items():
            price_history = data.get('price_history', [])

            if len(price_history) >= 2:
                first_price = price_history[0]['price']
                last_price = price_history[-1]['price']

                if first_price > 0:
                    change_pct = ((last_price - first_price) / first_price) * 100

                    trends.append({
                        'title': data.get('title'),
                        'distributor': data.get('distributor'),
                        'first_price': first_price,
                        'current_price': last_price,
                        'change_pct': change_pct,
                        'trend': 'down' if change_pct < 0 else 'up' if change_pct > 0 else 'stable',
                        'data_points': len(price_history)
                    })

        return sorted(trends, key=lambda x: x['change_pct'])
