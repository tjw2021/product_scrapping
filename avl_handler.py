"""
AVL Handler - Matches products against THRIVE and GOODLEAP Approved Vendor Lists
Handles manufacturer/model matching and domestic content identification
"""

import pandas as pd
from typing import Dict, Optional
import os


class AVLHandler:
    """Handles matching against multiple AVL files"""

    def __init__(self, thrive_file: Optional[str] = None, goodleap_file: Optional[str] = None):
        """
        Initialize AVL handler with AVL file paths

        Args:
            thrive_file: Path to THRIVE AVL Excel file
            goodleap_file: Path to GOODLEAP AVL Excel file
        """
        self.thrive_df = None
        self.goodleap_df = None

        # Load THRIVE AVL
        if thrive_file and os.path.exists(thrive_file):
            try:
                self.thrive_df = pd.read_excel(thrive_file)
                # Normalize manufacturer names for matching
                if 'Manufacturer' in self.thrive_df.columns:
                    self.thrive_df['manufacturer_normalized'] = (
                        self.thrive_df['Manufacturer'].str.upper().str.strip()
                    )
                    # Handle Model column - might be missing
                    if 'Model' in self.thrive_df.columns:
                        self.thrive_df['model_normalized'] = (
                            self.thrive_df['Model'].astype(str).str.upper().str.strip()
                        )
                    print(f"✅ Loaded THRIVE AVL: {len(self.thrive_df)} entries")
                else:
                    print(f"⚠️  THRIVE AVL file missing 'Manufacturer' column")
                    self.thrive_df = None
            except Exception as e:
                print(f"⚠️  Error loading THRIVE AVL: {e}")
                self.thrive_df = None
        else:
            print("⚠️  THRIVE AVL file not found")

        # Load GOODLEAP AVL
        if goodleap_file and os.path.exists(goodleap_file):
            try:
                self.goodleap_df = pd.read_excel(goodleap_file)
                # Normalize manufacturer names for matching
                if 'Manufacturer' in self.goodleap_df.columns:
                    self.goodleap_df['manufacturer_normalized'] = (
                        self.goodleap_df['Manufacturer'].str.upper().str.strip()
                    )
                    print(f"✅ Loaded GOODLEAP AVL: {len(self.goodleap_df)} entries")
                else:
                    print(f"⚠️  GOODLEAP AVL file missing 'Manufacturer' column")
                    self.goodleap_df = None
            except Exception as e:
                print(f"⚠️  Error loading GOODLEAP AVL: {e}")
                self.goodleap_df = None
        else:
            print("⚠️  GOODLEAP AVL file not found")

    def check_thrive_approval(self, manufacturer: str, model: str = '') -> Dict:
        """
        Check if product is on THRIVE AVL

        Args:
            manufacturer: Product manufacturer/brand
            model: Product model number (optional)

        Returns:
            Dictionary with approval status and domestic content flag
            {
                'approved': bool,
                'domestic': bool,
                'match_type': str  # 'exact', 'manufacturer_only', or 'not_found'
            }
        """
        if self.thrive_df is None or self.thrive_df.empty:
            return {'approved': False, 'domestic': False, 'match_type': 'no_avl'}

        manufacturer_norm = manufacturer.upper().strip()
        model_norm = model.upper().strip() if model else ''

        # Find matching manufacturer
        manufacturer_matches = self.thrive_df[
            self.thrive_df['manufacturer_normalized'] == manufacturer_norm
        ]

        if manufacturer_matches.empty:
            return {'approved': False, 'domestic': False, 'match_type': 'not_found'}

        # Check for model-specific match if model is provided and column exists
        if model_norm and 'model_normalized' in self.thrive_df.columns:
            model_matches = manufacturer_matches[
                manufacturer_matches['model_normalized'] == model_norm
            ]

            if not model_matches.empty:
                # Exact model match found
                row = model_matches.iloc[0]
                domestic = False
                if 'Domestic Content' in row:
                    domestic = str(row['Domestic Content']).upper() in ['YES', 'Y', 'TRUE', '1']

                return {
                    'approved': True,
                    'domestic': domestic,
                    'match_type': 'exact'
                }

        # Manufacturer match only (no model or no model match)
        # Consider as approved but not necessarily domestic
        return {
            'approved': True,
            'domestic': False,
            'match_type': 'manufacturer_only'
        }

    def check_goodleap_approval(self, manufacturer: str) -> Dict:
        """
        Check if manufacturer is on GOODLEAP AVL

        Args:
            manufacturer: Product manufacturer/brand

        Returns:
            Dictionary with approval status, program type, and domestic content
            {
                'approved': bool,
                'program': str,  # e.g., 'Loans/Leases/PPAs' or 'Loans Only'
                'domestic': bool
            }
        """
        if self.goodleap_df is None or self.goodleap_df.empty:
            return {'approved': False, 'program': None, 'domestic': False}

        manufacturer_norm = manufacturer.upper().strip()

        matches = self.goodleap_df[
            self.goodleap_df['manufacturer_normalized'] == manufacturer_norm
        ]

        if matches.empty:
            return {'approved': False, 'program': None, 'domestic': False}

        # Get first match (there should typically only be one per manufacturer)
        row = matches.iloc[0]

        # Get program type
        program = row.get('Program Type', 'Unknown')

        # Get domestic content
        domestic = False
        if 'Domestic Content' in row:
            domestic_val = str(row['Domestic Content']).upper()
            domestic = domestic_val in ['YES', 'Y', 'TRUE', '1']

        return {
            'approved': True,
            'program': program,
            'domestic': domestic
        }

    def add_avl_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add AVL check columns to product dataframe

        Args:
            df: Product dataframe with 'brand' and 'sku' columns

        Returns:
            DataFrame with additional AVL columns
        """
        print("\n📋 Adding AVL approval columns...")

        # Ensure required columns exist
        if 'brand' not in df.columns:
            print("⚠️  'brand' column not found in dataframe")
            return df

        # Use 'sku' as model if available, otherwise empty string
        model_col = 'sku' if 'sku' in df.columns else None

        # THRIVE columns
        if self.thrive_df is not None:
            print("  Checking THRIVE AVL...")
            thrive_results = df.apply(
                lambda row: self.check_thrive_approval(
                    row['brand'],
                    row.get(model_col, '') if model_col else ''
                ),
                axis=1
            )

            df['thrive_approved'] = thrive_results.apply(lambda x: x['approved'])
            df['thrive_domestic'] = thrive_results.apply(lambda x: x['domestic'])
            df['thrive_match_type'] = thrive_results.apply(lambda x: x['match_type'])

            print(f"    ✅ {df['thrive_approved'].sum()} products approved on THRIVE AVL")
            print(f"    ✅ {df['thrive_domestic'].sum()} products with THRIVE domestic content")
        else:
            df['thrive_approved'] = False
            df['thrive_domestic'] = False
            df['thrive_match_type'] = 'no_avl'

        # GOODLEAP columns
        if self.goodleap_df is not None:
            print("  Checking GOODLEAP AVL...")
            goodleap_results = df.apply(
                lambda row: self.check_goodleap_approval(row['brand']),
                axis=1
            )

            df['goodleap_approved'] = goodleap_results.apply(lambda x: x['approved'])
            df['goodleap_program'] = goodleap_results.apply(lambda x: x['program'])
            df['goodleap_domestic'] = goodleap_results.apply(lambda x: x['domestic'])

            print(f"    ✅ {df['goodleap_approved'].sum()} products approved on GOODLEAP AVL")
            print(f"    ✅ {df['goodleap_domestic'].sum()} products with GOODLEAP domestic content")
        else:
            df['goodleap_approved'] = False
            df['goodleap_program'] = None
            df['goodleap_domestic'] = False

        # Combined columns
        df['on_any_avl'] = df['thrive_approved'] | df['goodleap_approved']
        df['on_all_avls'] = df['thrive_approved'] & df['goodleap_approved']

        # Domestic content from either AVL or product specs
        df['domestic_content_qualified'] = (
            df['thrive_domestic'] |
            df['goodleap_domestic'] |
            df.get('specs', pd.Series()).apply(
                lambda x: isinstance(x, dict) and x.get('domestic_content', 'No').upper() == 'YES'
            )
        )

        print(f"\n  📊 Summary:")
        print(f"    • On any AVL: {df['on_any_avl'].sum()} products")
        print(f"    • On all AVLs: {df['on_all_avls'].sum()} products")
        print(f"    • Domestic content qualified: {df['domestic_content_qualified'].sum()} products")

        return df

    def identify_domestic_content(self, product: Dict) -> bool:
        """
        Determine if product qualifies for domestic content incentives

        Args:
            product: Product dictionary with 'title', 'brand', 'sku', 'specs' keys

        Returns:
            True if product qualifies for domestic content, False otherwise
        """
        # Check 1: Title contains "Domestic Content"
        if 'domestic content' in product.get('title', '').lower():
            return True

        # Check 2: AVL approval
        manufacturer = product.get('brand', '')
        model = product.get('sku', '')

        if manufacturer:
            thrive_check = self.check_thrive_approval(manufacturer, model)
            if thrive_check['domestic']:
                return True

            goodleap_check = self.check_goodleap_approval(manufacturer)
            if goodleap_check['domestic']:
                return True

        # Check 3: Product specs field
        specs = product.get('specs', {})
        if isinstance(specs, dict):
            domestic_field = specs.get('domestic_content', 'No')
            if str(domestic_field).upper() in ['YES', 'Y', 'TRUE', '1']:
                return True

        return False


if __name__ == "__main__":
    # Test the AVL handler
    print("Testing AVL Handler...")

    # Create handler with example files
    avl = AVLHandler('THRIVE_AVL.xlsx', 'GOODLEAP_AVL.xlsx')

    # Test some manufacturers
    test_manufacturers = [
        ('Canadian Solar', 'CS3W-400MS'),
        ('Silfab', 'SIL-380-BX'),
        ('Unknown Brand', 'MODEL123')
    ]

    for manufacturer, model in test_manufacturers:
        print(f"\n Testing: {manufacturer} {model}")
        thrive_result = avl.check_thrive_approval(manufacturer, model)
        goodleap_result = avl.check_goodleap_approval(manufacturer)
        print(f"  THRIVE: {thrive_result}")
        print(f"  GOODLEAP: {goodleap_result}")
