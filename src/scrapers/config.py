"""
Configuration constants for scrapers.
"""

# Browser Configuration
BROWSER_CONFIG = {
    "headless": True,  # Set to False for debugging
    "timeout": 60000,  # Default page load timeout in ms
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "viewport": {"width": 1920, "height": 1080}
}

# Timeout Configuration (in milliseconds)
TIMEOUTS = {
    "page_load": 60000,
    "selector_wait": 15000,
    "element_wait": 10000,
    "network_idle": 30000
}

# Scraper URLs
SCRAPER_URLS = {
    "accert": "https://cliente.accertlogistica.com.br/rastreamento",
    "jamef": "https://www.jamef.com.br/",
    "braspress": "https://www.braspress.com/",
    "viaverde": "http://viaverde.supplytrack.com.br/login?ReturnUrl=%2f"
}

# Screenshot Configuration
SCREENSHOT_DIR = "screenshots"
SCREENSHOT_ENABLED = True
