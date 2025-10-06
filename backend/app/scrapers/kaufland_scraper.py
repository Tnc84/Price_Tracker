"""Kaufland scraper - Supermarket chain"""

from typing import List, Optional
from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseScraper
from app.schemas.price import PriceCreate
import re
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class KauflandScraper(BaseScraper):
    """
    Scraper for Kaufland.ro - Supermarket products
    
    Base URL: https://www.kaufland.ro
    """
    
    BASE_URL = "https://www.kaufland.ro"
    SEARCH_URL = "https://www.kaufland.ro/oferte/search.html"
    
    def __init__(self):
        super().__init__("Kaufland")
    
    async def search_product(self, product_name: str, category: Optional[str] = None) -> List[PriceCreate]:
        """Search Kaufland for products"""
        prices = []
        
        search_query = quote_plus(product_name)
        search_url = f"{self.SEARCH_URL}?q={search_query}"
        
        html = await self._make_request(search_url)
        if not html:
            logger.warning(f"Failed to fetch Kaufland search results for '{product_name}'")
            return prices
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find product cards
        products = soup.find_all('article', class_=re.compile(r'product|offer-tile'))
        
        logger.info(f"Found {len(products)} products on Kaufland for '{product_name}'")
        
        for product in products[:15]:
            try:
                price_data = self._extract_product_data(product)
                if price_data:
                    prices.append(price_data)
            except Exception as e:
                logger.error(f"Error extracting Kaufland product data: {e}")
                continue
                
        return prices
    
    async def get_product_price(self, product_url: str) -> Optional[PriceCreate]:
        """Get current price for specific Kaufland product"""
        html = await self._make_request(product_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'lxml')
        return self._extract_product_detail_data(soup, product_url)
    
    def _extract_product_data(self, element) -> Optional[PriceCreate]:
        """Extract product data from search result"""
        try:
            # Product name
            name_elem = element.find('h3', class_=re.compile(r'product-title|offer-title'))
            if not name_elem:
                name_elem = element.find('a', class_=re.compile(r'title'))
            
            if not name_elem:
                return None
            
            name = self._clean_text(name_elem.get_text())
            
            # Product URL
            link_elem = element.find('a', href=True)
            product_url = ""
            if link_elem:
                product_url = link_elem.get('href', '')
                if product_url and not product_url.startswith('http'):
                    product_url = f"{self.BASE_URL}{product_url}"
            
            # Price
            price_elem = element.find('span', class_=re.compile(r'price__integer|offer-price'))
            if not price_elem:
                price_elem = element.find('div', class_=re.compile(r'price'))
            
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            
            # Check for decimal
            decimal_elem = element.find('span', class_=re.compile(r'price__decimal'))
            if decimal_elem:
                price_text += "," + decimal_elem.get_text().strip()
            
            price = self._parse_price(price_text)
            if not price:
                return None
            
            # Check for old price (promotions)
            old_price_elem = element.find('span', class_=re.compile(r'price__old|original-price'))
            original_price = None
            is_promotional = False
            promotion_text = None
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                if original_price and price < original_price:
                    is_promotional = True
                    savings = original_price - price
                    promotion_text = f"Reducere {savings:.0f} lei"
            
            # Check for promotion badge
            badge_elem = element.find('span', class_=re.compile(r'badge|promotion'))
            if badge_elem:
                is_promotional = True
                if not promotion_text:
                    promotion_text = self._clean_text(badge_elem.get_text())
            
            return PriceCreate(
                product_id=0,
                retailer="Kaufland",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=True,
                stock_status="Disponibil",
                url=product_url,
                is_promotional=is_promotional,
                promotion_text=promotion_text,
                delivery_info=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting Kaufland product data: {e}")
            return None
    
    def _extract_product_detail_data(self, soup: BeautifulSoup, url: str) -> Optional[PriceCreate]:
        """Extract product data from detail page"""
        try:
            price_elem = soup.find('span', class_=re.compile(r'price__integer'))
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            
            decimal_elem = soup.find('span', class_=re.compile(r'price__decimal'))
            if decimal_elem:
                price_text += "," + decimal_elem.get_text().strip()
            
            price = self._parse_price(price_text)
            if not price:
                return None
            
            old_price_elem = soup.find('span', class_=re.compile(r'price__old'))
            original_price = None
            is_promotional = False
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                is_promotional = self._is_promotional(original_price, price)
            
            return PriceCreate(
                product_id=0,
                retailer="Kaufland",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=True,
                stock_status="Disponibil",
                url=url,
                is_promotional=is_promotional,
                promotion_text=None,
                delivery_info=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting Kaufland detail data: {e}")
            return None

