"""Web scrapers for Romanian retailers"""

from app.scrapers.emag_scraper import EmagScraper
from app.scrapers.altex_scraper import AltexScraper
from app.scrapers.carrefour_scraper import CarrefourScraper
from app.scrapers.kaufland_scraper import KauflandScraper
from app.scrapers.selgros_scraper import SelgrosScraper

__all__ = [
    "EmagScraper",
    "AltexScraper",
    "CarrefourScraper",
    "KauflandScraper",
    "SelgrosScraper",
]

