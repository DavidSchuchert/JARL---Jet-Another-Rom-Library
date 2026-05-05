"""Scraper module for fetching ROM metadata from external sources."""
from app.scraper.screenscraper import ScreenScraperScraper
from app.scraper.igdb import IGDBScraper
from app.scraper.batch import BatchScraper

__all__ = ["ScreenScraperScraper", "IGDBScraper", "BatchScraper"]
