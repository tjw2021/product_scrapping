"""
Spec Sheet Downloader - Downloads specification PDFs from product pages
Supports multiple methods to find and download PDFs
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Dict
import time
import re


class SpecSheetDownloader:
    """Downloads specification sheets from product pages"""

    def __init__(self, output_dir: str = 'spec_sheets', timeout: int = 30):
        """
        Initialize spec sheet downloader

        Args:
            output_dir: Directory to save downloaded PDFs
            timeout: Timeout for HTTP requests in seconds
        """
        self.output_dir = output_dir
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Track download statistics
        self.downloaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def find_spec_sheet_links(self, product_url: str, html_content: Optional[str] = None) -> List[str]:
        """
        Find PDF links on a product page

        Args:
            product_url: URL of the product page
            html_content: Optional pre-fetched HTML content

        Returns:
            List of PDF URLs found on the page
        """
        pdf_links = []

        try:
            # Fetch page if content not provided
            if html_content is None:
                response = requests.get(product_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                html_content = response.content

            soup = BeautifulSoup(html_content, 'html.parser')

            # Method 1: Find direct PDF links (href ends with .pdf)
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    full_url = urljoin(product_url, href)
                    if full_url not in pdf_links:
                        pdf_links.append(full_url)

            # Method 2: Find links with spec/datasheet/manual keywords
            spec_keywords = [
                'spec', 'specification', 'datasheet', 'data sheet',
                'manual', 'technical', 'documentation', 'pdf', 'download'
            ]

            for link in soup.find_all('a', href=True):
                # Check link text
                link_text = link.get_text().lower()
                if any(keyword in link_text for keyword in spec_keywords):
                    href = link['href']
                    # If it's a PDF link
                    if '.pdf' in href.lower():
                        full_url = urljoin(product_url, href)
                        if full_url not in pdf_links:
                            pdf_links.append(full_url)

                # Check title attribute
                title = link.get('title', '').lower()
                if title and any(keyword in title for keyword in spec_keywords):
                    href = link['href']
                    if '.pdf' in href.lower():
                        full_url = urljoin(product_url, href)
                        if full_url not in pdf_links:
                            pdf_links.append(full_url)

            # Method 3: Find embedded PDF viewers or iframes
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '')
                if '.pdf' in src.lower():
                    full_url = urljoin(product_url, src)
                    if full_url not in pdf_links:
                        pdf_links.append(full_url)

            # Method 4: Look for download buttons/links
            for element in soup.find_all(['button', 'a'], class_=re.compile(r'download|spec|pdf', re.I)):
                # Check if there's an associated data attribute or link
                href = element.get('href') or element.get('data-url') or element.get('data-href')
                if href and '.pdf' in href.lower():
                    full_url = urljoin(product_url, href)
                    if full_url not in pdf_links:
                        pdf_links.append(full_url)

        except Exception as e:
            print(f"    ⚠️  Error finding PDFs on {product_url}: {e}")

        return pdf_links

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to remove invalid characters

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for filesystem
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200 - len(ext)] + ext

        return filename

    def download_pdf(self, url: str, filename: str, overwrite: bool = False) -> Optional[str]:
        """
        Download a PDF file

        Args:
            url: URL of the PDF
            filename: Desired filename (will be sanitized)
            overwrite: Whether to overwrite existing files

        Returns:
            Full path to downloaded file, or None if failed
        """
        try:
            # Sanitize filename
            safe_filename = self.sanitize_filename(filename)
            if not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'

            filepath = os.path.join(self.output_dir, safe_filename)

            # Check if file already exists
            if os.path.exists(filepath) and not overwrite:
                self.skipped_count += 1
                return filepath  # Already exists, skip download

            # Download PDF
            response = requests.get(url, headers=self.headers, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Verify it's actually a PDF
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                print(f"    ⚠️  URL does not appear to be a PDF: {url}")
                self.failed_count += 1
                return None

            # Save to file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            self.downloaded_count += 1
            return filepath

        except Exception as e:
            print(f"    ⚠️  Error downloading {url}: {e}")
            self.failed_count += 1
            return None

    def download_for_product(
        self,
        product: Dict,
        max_pdfs: int = 3,
        delay: float = 1.0
    ) -> List[str]:
        """
        Download spec sheets for a product

        Args:
            product: Product dictionary with 'product_url', 'sku', 'title' keys
            max_pdfs: Maximum number of PDFs to download per product
            delay: Delay between downloads in seconds

        Returns:
            List of downloaded file paths
        """
        product_url = product.get('product_url')
        sku = product.get('sku', 'unknown')
        title = product.get('title', 'product')

        if not product_url or product_url == 'N/A':
            return []

        downloaded_files = []

        try:
            # Find PDF links on product page
            pdf_links = self.find_spec_sheet_links(product_url)

            if not pdf_links:
                return []

            # Download PDFs (up to max_pdfs)
            for idx, pdf_url in enumerate(pdf_links[:max_pdfs], 1):
                # Create filename from SKU and index
                filename = f"{sku}_spec_{idx}.pdf"

                # Download
                filepath = self.download_pdf(pdf_url, filename)

                if filepath:
                    downloaded_files.append(filepath)

                # Delay between downloads
                if idx < len(pdf_links) and delay > 0:
                    time.sleep(delay)

        except Exception as e:
            print(f"    ⚠️  Error downloading specs for {sku}: {e}")

        return downloaded_files

    def download_for_products_batch(
        self,
        products: List[Dict],
        max_pdfs_per_product: int = 3,
        delay: float = 1.0,
        verbose: bool = True
    ) -> Dict[str, List[str]]:
        """
        Download spec sheets for multiple products

        Args:
            products: List of product dictionaries
            max_pdfs_per_product: Maximum PDFs to download per product
            delay: Delay between products in seconds
            verbose: Whether to print progress

        Returns:
            Dictionary mapping SKU to list of downloaded file paths
        """
        results = {}
        total = len(products)

        if verbose:
            print(f"\n📥 Downloading spec sheets for {total} products...")

        for idx, product in enumerate(products, 1):
            sku = product.get('sku', f'product_{idx}')

            if verbose and (idx % 10 == 0 or idx == 1):
                print(f"  Progress: {idx}/{total} ({(idx/total*100):.1f}%)")

            downloaded = self.download_for_product(product, max_pdfs_per_product, delay)
            if downloaded:
                results[sku] = downloaded

            # Delay between products
            if idx < total and delay > 0:
                time.sleep(delay)

        if verbose:
            print(f"\n  ✅ Download complete!")
            print(f"    • Downloaded: {self.downloaded_count} files")
            print(f"    • Skipped: {self.skipped_count} files (already exist)")
            print(f"    • Failed: {self.failed_count} files")

        return results

    def get_statistics(self) -> Dict[str, int]:
        """
        Get download statistics

        Returns:
            Dictionary with download statistics
        """
        return {
            'downloaded': self.downloaded_count,
            'skipped': self.skipped_count,
            'failed': self.failed_count,
            'total_attempts': self.downloaded_count + self.skipped_count + self.failed_count
        }


if __name__ == "__main__":
    # Test the spec sheet downloader
    print("Testing Spec Sheet Downloader...")

    downloader = SpecSheetDownloader(output_dir='test_spec_sheets')

    # Test with a sample product
    test_product = {
        'product_url': 'https://example.com/product/solar-panel',
        'sku': 'TEST-123',
        'title': 'Test Solar Panel'
    }

    print(f"\nTesting with product: {test_product['title']}")
    downloaded = downloader.download_for_product(test_product)

    if downloaded:
        print(f"✅ Downloaded {len(downloaded)} spec sheets")
        for filepath in downloaded:
            print(f"  • {filepath}")
    else:
        print("⚠️  No spec sheets found or downloaded")

    # Print statistics
    stats = downloader.get_statistics()
    print(f"\nStatistics:")
    print(f"  Downloaded: {stats['downloaded']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
