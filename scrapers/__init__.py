"""
Scrapers Package
Contains all distributor-specific scrapers
"""

from .solar_cellz_scraper import SolarCellzScraper
from .alte_scraper import AltEScraper
from .ressupply_scraper import RessupplyScraper
from .us_solar_supplier_scraper import USSolarSupplierScraper
from .solar_store_scraper import SolarStoreScraper
from .giga_energy_scraper import GigaEnergyScraper
from .essential_parts_scraper import EssentialPartsScraper
from .soligent_scraper import SoligentScraper

__all__ = [
    'SolarCellzScraper',
    'AltEScraper',
    'RessupplyScraper',
    'USSolarSupplierScraper',
    'SolarStoreScraper',
    'GigaEnergyScraper',
    'EssentialPartsScraper',
    'SoligentScraper'
]
