"""
Scrapers Package
Contains all distributor-specific scrapers
"""

from .solar_cellz_scraper import SolarCellzScraper
from .solar_electric_supply_scraper import SolarElectricSupplyScraper
from .wholesale_solar_scraper import WholesaleSolarScraper
from .alte_scraper import AltEScraper
from .ressupply_scraper import RessupplyScraper

__all__ = [
    'SolarCellzScraper',
    'SolarElectricSupplyScraper',
    'WholesaleSolarScraper',
    'AltEScraper',
    'RessupplyScraper'
]
