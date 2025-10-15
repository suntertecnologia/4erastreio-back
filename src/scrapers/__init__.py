"""
Scrapers package for logistics tracking.

This package provides web scrapers for various Brazilian logistics companies.
All scrapers inherit from BaseScraper and follow a consistent interface.
"""

from .base_scraper import BaseScraper
from ..configs.config import BROWSER_CONFIG, TIMEOUTS, SCRAPER_URLS
from .scrapper_data_model import ScraperResponse, ErrorInfo

# Import scraper classes
from .accert_scraper import AccertScraper, rastrear_accert
from .jamef_scraper import JamefScraper, rastrear_jamef
from .braspress_scraper import BrasspressScraper, rastrear_braspress
from .viaverde_scraper import ViaVerdeScraper, rastrear_viaverde

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
    # Legacy functions for backward compatibility
    "rastrear_accert",
    "rastrear_jamef",
    "rastrear_braspress",
    "rastrear_viaverde",
]
