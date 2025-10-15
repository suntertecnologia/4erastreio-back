"""
Scrapers package for logistics tracking.

This package provides web scrapers for various Brazilian logistics companies.
All scrapers inherit from BaseScraper and follow a consistent interface.
"""

from .base_scraper import BaseScraper
from ..configs.config import BROWSER_CONFIG, TIMEOUTS, SCRAPER_URLS
from .scrapper_data_model import ScraperResponse, ErrorInfo

# Import scraper classes
from .accert_scraper import AccertScraper
from .jamef_scraper import JamefScraper
from .braspress_scraper import BrasspressScraper
from .viaverde_scraper import ViaVerdeScraper

__all__ = [
    # Base classes and utilities
    "BaseScraper",
    "BROWSER_CONFIG",
    "TIMEOUTS",
    "SCRAPER_URLS",
    "ScraperResponse",
    "ErrorInfo",
    # Scraper classes
    "AccertScraper",
    "JamefScraper",
    "BrasspressScraper",
    "ViaVerdeScraper",
]
