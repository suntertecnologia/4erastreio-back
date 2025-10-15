"""
Base scraper class with common functionality for all scrapers.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional
from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)
from ..configs.logger_config import logger
from ..configs.config import (
    BROWSER_CONFIG,
    SCREENSHOT_DIR,
    SCREENSHOT_ENABLED,
)
from .scrapper_data_model import ScraperResponse, ErrorInfo


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Provides common functionality for browser management, error handling, and logging.
    """

    def __init__(self, name: str):
        """
        Initialize the base scraper.

        Args:
            name: Name of the scraper (e.g., "accert", "jamef")
        """
        self.name = name
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._teardown_browser()

    async def _setup_browser(self):
        """Initialize browser and page."""
        self._playwright = await async_playwright().start()

        # Launch browser with configuration
        self.browser = await self._playwright.chromium.launch(
            headless=BROWSER_CONFIG["headless"]
        )

        # Create context with user agent and viewport
        context = await self.browser.new_context(
            user_agent=BROWSER_CONFIG["user_agent"], viewport=BROWSER_CONFIG["viewport"]
        )

        self.page = await context.new_page()

    async def _teardown_browser(self):
        """Close browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
            logger.info(f"[{self.name.upper()}] Browser closed.")
        if self._playwright:
            await self._playwright.stop()

    async def create_page(self) -> Page:
        """
        Get the current page instance.

        Returns:
            The Playwright Page object.
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Use async context manager.")
        return self.page

    def _get_log_prefix(self, **kwargs) -> str:
        """
        Generate a log prefix with tracking information.

        Args:
            **kwargs: Key-value pairs to include in the prefix.

        Returns:
            Formatted log prefix string.
        """
        parts = [f"{k.upper()}: {v}" for k, v in kwargs.items()]
        return f"[{self.name.upper()}] [{', '.join(parts)}]"

    async def _take_screenshot(self, error_type: str = "error"):
        """
        Take a screenshot for debugging purposes.

        Args:
            error_type: Type of error (used in filename).
        """
        if not SCREENSHOT_ENABLED or not self.page:
            return

        try:
            # Create screenshots directory if it doesn't exist
            screenshot_dir = Path(SCREENSHOT_DIR)
            screenshot_dir.mkdir(exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{error_type}_{timestamp}.png"
            filepath = screenshot_dir / filename

            await self.page.screenshot(path=str(filepath))
            logger.info(f"[{self.name.upper()}] Screenshot saved: {filepath}")
        except Exception as e:
            logger.error(f"[{self.name.upper()}] Failed to take screenshot: {e}")

    def _create_error_info(self, error_type: str, message: str) -> ErrorInfo:
        """
        Create standardized error information.

        Args:
            error_type: Type of error ("timeout", "exception", "not_found").
            message: Error message.

        Returns:
            ErrorInfo dictionary.
        """
        return {
            "tipo": error_type,
            "mensagem": message,
            "timestamp": datetime.now().isoformat(),
        }

    def success_response(self, dados: dict) -> ScraperResponse:
        """
        Create a successful response.

        Args:
            dados: Extracted data.

        Returns:
            ScraperResponse with success status.
        """
        return {"status": "sucesso", "dados": dados, "erro": None}

    def error_response(self, error_type: str, message: str) -> ScraperResponse:
        """
        Create an error response.

        Args:
            error_type: Type of error.
            message: Error message.

        Returns:
            ScraperResponse with failure status.
        """
        return {
            "status": "falha",
            "dados": None,
            "erro": self._create_error_info(error_type, message),
        }

    async def execute(self, *args, **kwargs) -> ScraperResponse:
        """
        Execute the scraper with error handling.

        Args:
            *args: Positional arguments for the scraper.
            **kwargs: Keyword arguments for the scraper.

        Returns:
            ScraperResponse with results or error information.
        """
        log_prefix = self._get_log_prefix(
            **{
                k: v
                for k, v in kwargs.items()
                if k in ["cnpj", "nota_fiscal", "n_rastreio"]
            }
        )

        try:
            logger.info(f"{log_prefix} Starting scraper execution")

            async with self:
                result = await self.scrape(*args, **kwargs)

            logger.info(f"{log_prefix} Scraper execution completed successfully")
            return result

        except PlaywrightTimeoutError as e:
            logger.error(f"{log_prefix} Timeout error: {e}")
            await self._take_screenshot("timeout")
            return self.error_response(
                "timeout",
                "O tempo para encontrar um elemento expirou. Verifique os seletores ou a velocidade da sua conexão.",
            )

        except Exception as e:
            logger.exception(f"{log_prefix} Unexpected error: {e}")
            await self._take_screenshot("exception")
            return self.error_response("exception", f"Erro inesperado: {str(e)}")

    @abstractmethod
    async def scrape(self, *args, **kwargs) -> ScraperResponse:
        """
        Abstract method to be implemented by each scraper.
        Contains the scraper-specific logic.

        Args:
            *args: Scraper-specific positional arguments.
            **kwargs: Scraper-specific keyword arguments.

        Returns:
            ScraperResponse with extracted data.
        """
        pass
