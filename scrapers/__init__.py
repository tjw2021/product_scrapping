"""
Scrapers Package
Contains all distributor-specific scrapers
"""

from .solar_cellz_scraper import SolarCellzScraper
from .solar_electric_supply_scraper import SolarElectricSupplyScraper
from .alte_scraper import AltEScraper
from .ressupply_scraper import RessupplyScraper
from .us_solar_supplier_scraper import USSolarSupplierScraper
from .solar_store_scraper import SolarStoreScraper

__all__ = [
    'SolarCellzScraper',
    'SolarElectricSupplyScraper',
    'AltEScraper',
    'RessupplyScraper',
    'USSolarSupplierScraper',
    'SolarStoreScraper'
]
