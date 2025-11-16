"""Base scraper class for all retailer scrapers"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from app.schemas.price import PriceCreate
from app.core.config import settings
from app.core.exceptions import ScraperException, RetailerUnavailableException
import random
import logging
import re

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Base scraper following SOLID principles:
    - Single Responsibility: Handle HTTP requests and parsing
    - Open/Closed: Extend for specific retailers without modifying base
    - Liskov Substitution: All scrapers can be used interchangeably
    - Interface Segregation: Only implement methods needed
    - Dependency Inversion: Depend on abstractions not concretions
    """
    
    def __init__(self, retailer_name: str):
        self.retailer_name = retailer_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_agents = settings.user_agents
        
    async def __aenter__(self):
        """Async context manager entry"""
        # Increased timeout for slow retailers (some take 60+ seconds)
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        self.session = aiohttp.ClientSession(
            headers=self._get_headers(),
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random user agent"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @abstractmethod
    async def search_product(self, product_name: str, category: Optional[str] = None) -> List[PriceCreate]:
        """
        Search for a product and return price information
        
        Args:
            product_name: Name of the product to search
            category: Optional category filter
            
        Returns:
            List of PriceCreate objects
        """
        pass
    
    @abstractmethod
    async def get_product_price(self, product_url: str) -> Optional[PriceCreate]:
        """
        Get current price for a specific product URL
        
        Args:
            product_url: Direct URL to product page
            
        Returns:
            PriceCreate object or None if not found
        """
        pass
    
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[str]:
        """
        Make HTTP request with error handling and rate limiting
        
        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for aiohttp
            
        Returns:
            Response text or None on failure
        """
        try:
            # Rate limiting
            await asyncio.sleep(settings.request_delay)
            
            logger.info(f"Requesting {url}")
            
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 404:
                    logger.warning(f"Product not found: {url}")
                    return None
                elif response.status == 429:
                    logger.warning(f"Rate limited by {self.retailer_name}")
                    await asyncio.sleep(10)  # Wait before retry
                    return None
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Request failed for {url}: {e}")
            raise RetailerUnavailableException(
                f"{self.retailer_name} is unavailable",
                details=str(e)
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Unexpected error for {url}: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full traceback:\n{error_details}")
            return None
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """
        Parse price from Romanian text format
        
        Examples:
            "123,45 lei" -> 123.45
            "1.234,56 RON" -> 1234.56
            "123 lei" -> 123.0
            
        Args:
            price_text: Price string to parse
            
        Returns:
            Float price or None if parsing fails
        """
        try:
            # Remove currency symbols and common words
            price_text = price_text.lower()
            price_text = re.sub(r'(lei|ron|eur|€)', '', price_text)
            price_text = price_text.strip()
            
            # Handle Romanian number format (1.234,56)
            # Remove thousand separators (.)
            price_text = price_text.replace('.', '')
            # Replace decimal comma with point
            price_text = price_text.replace(',', '.')
            
            # Extract number
            match = re.search(r'\d+\.?\d*', price_text)
            if match:
                return float(match.group())
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse price '{price_text}': {e}")
            return None
    
    def _is_promotional(self, original_price: Optional[float], current_price: float) -> bool:
        """Determine if current price is promotional"""
        if not original_price:
            return False
        return current_price < original_price
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.split()).strip()
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from URL (retailer-specific)"""
        return None

