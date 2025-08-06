"""
Scrapers Package
Modular scraper system for Casablanca Insights
"""

__version__ = "1.0.0"
__author__ = "Casablanca Insights Team"

# Import main components
from .orchestrator import MasterOrchestrator
from .base.scraper_interface import BaseScraper

__all__ = [
    'MasterOrchestrator',
    'BaseScraper'
] 