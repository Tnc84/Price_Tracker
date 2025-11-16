"""Scraper service for coordinating multiple retailer scrapers"""

from typing import List, Dict
import asyncio
from app.scrapers import (
    EmagScraper,
    # AltexScraper,
    # CarrefourScraper,
    # KauflandScraper,
    # SelgrosScraper
)
from app.schemas.price import PriceCreate
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service for coordinating web scraping across multiple Romanian retailers
    
    Follows SOLID principles:
    - Single Responsibility: Coordinates scraping only
    - Open/Closed: Easy to add new scrapers
    - Dependency Inversion: Depends on abstract scraper interface
    """
    
    def __init__(self):
        self.scrapers = {
            "emag": EmagScraper,
            # "altex": AltexScraper,
            # "carrefour": CarrefourScraper,
            # "kaufland": KauflandScraper,
            # "selgros": SelgrosScraper
        }
    
    async def search_all_retailers(
        self,
        product_name: str,
        category: str = None,
        retailers: List[str] = None
    ) -> Dict[str, List[PriceCreate]]:
        """
        Search for a product across all retailers
        
        Args:
            product_name: Product name to search
            category: Optional category filter
            retailers: Optional list of specific retailers (defaults to all)
            
        Returns:
            Dictionary mapping retailer names to list of prices
        """
        if not retailers:
            retailers = list(self.scrapers.keys())
        
        logger.info(f"Searching '{product_name}' across {len(retailers)} retailers")
        
        tasks = []
        for retailer in retailers:
            if retailer in self.scrapers:
                tasks.append(self._search_retailer(retailer, product_name, category))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results with detailed error logging
        all_results = {}
        for i, retailer in enumerate(retailers):
            if isinstance(results[i], Exception):
                error_msg = str(results[i])
                logger.error(f"Error scraping {retailer}: {error_msg}", exc_info=results[i])
                all_results[retailer] = []
            else:
                all_results[retailer] = results[i]
                if len(all_results[retailer]) == 0:
                    logger.warning(f"No results found for {retailer} - scraper returned empty list")
        
        total_prices = sum(len(prices) for prices in all_results.values())
        retailers_with_results = [r for r, prices in all_results.items() if len(prices) > 0]
        logger.info(f"Found {total_prices} total prices across all retailers. Retailers with results: {retailers_with_results}")
        
        return all_results
    
    async def _search_retailer(
        self,
        retailer: str,
        product_name: str,
        category: str = None
    ) -> List[PriceCreate]:
        """Search a specific retailer"""
        try:
            scraper_class = self.scrapers.get(retailer)
            if not scraper_class:
                logger.warning(f"Unknown retailer: {retailer}")
                return []
            
            async with scraper_class() as scraper:
                prices = await scraper.search_product(product_name, category)
                logger.info(f"Found {len(prices)} prices on {retailer}")
                return prices
                
        except Exception as e:
            logger.error(f"Error searching {retailer}: {e}")
            return []
    
    async def get_product_price(self, retailer: str, product_url: str) -> PriceCreate:
        """Get price for a specific product URL"""
        scraper_class = self.scrapers.get(retailer)
        if not scraper_class:
            raise ValueError(f"Unknown retailer: {retailer}")
        
        async with scraper_class() as scraper:
            return await scraper.get_product_price(product_url)
    
    def get_supported_retailers(self) -> List[str]:
        """Get list of supported retailers"""
        return list(self.scrapers.keys())

