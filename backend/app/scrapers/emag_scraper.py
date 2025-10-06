"""eMAG scraper - Romania's largest online retailer"""

from typing import List, Optional
from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseScraper
from app.schemas.price import PriceCreate
import re
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class EmagScraper(BaseScraper):
    """
    Scraper for eMAG.ro - Romania's #1 online marketplace
    
    Base URL: https://www.emag.ro
    """
    
    BASE_URL = "https://www.emag.ro"
    SEARCH_URL = "https://www.emag.ro/search"
    
    def __init__(self):
        super().__init__("eMAG")
    
    async def search_product(self, product_name: str, category: Optional[str] = None) -> List[PriceCreate]:
        """
        Search eMAG for products
        
        Example: https://www.emag.ro/search/cafea
        """
        prices = []
        
        # Build search URL
        search_query = quote_plus(product_name)
        search_url = f"{self.SEARCH_URL}/{search_query}"
        
        html = await self._make_request(search_url)
        if not html:
            logger.warning(f"Failed to fetch eMAG search results for '{product_name}'")
            return prices
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find product cards
        # eMAG uses card-v2 or card-item classes
        products = soup.find_all('div', class_=re.compile(r'card-item|card-v2'))
        
        logger.info(f"Found {len(products)} products on eMAG for '{product_name}'")
        
        for product in products[:15]:  # Limit to first 15 results
            try:
                price_data = self._extract_product_data(product)
                if price_data:
                    prices.append(price_data)
            except Exception as e:
                logger.error(f"Error extracting eMAG product data: {e}")
                continue
                
        return prices
    
    async def get_product_price(self, product_url: str) -> Optional[PriceCreate]:
        """Get current price for specific eMAG product"""
        html = await self._make_request(product_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'lxml')
        return self._extract_product_detail_data(soup, product_url)
    
    def _extract_product_data(self, element) -> Optional[PriceCreate]:
        """Extract product data from search result card"""
        try:
            # Product name
            name_elem = element.find('a', class_=re.compile(r'card-v2-title|product-title'))
            if not name_elem:
                return None
            
            name = self._clean_text(name_elem.get_text())
            
            # Product URL
            product_url = name_elem.get('href', '')
            if product_url and not product_url.startswith('http'):
                product_url = f"{self.BASE_URL}{product_url}"
            
            # Price extraction
            price_elem = element.find('p', class_=re.compile(r'product-new-price'))
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            price = self._parse_price(price_text)
            
            if not price:
                return None
            
            # Check for promotional pricing
            original_price_elem = element.find('p', class_=re.compile(r'product-old-price'))
            original_price = None
            is_promotional = False
            promotion_text = None
            
            if original_price_elem:
                original_price_text = original_price_elem.get_text().strip()
                original_price = self._parse_price(original_price_text)
                if original_price and price < original_price:
                    is_promotional = True
                    discount = ((original_price - price) / original_price) * 100
                    promotion_text = f"Reducere {discount:.0f}%"
            
            # Check availability
            stock_elem = element.find('p', class_=re.compile(r'stock|availability'))
            availability = True
            stock_status = "In stoc"
            
            if stock_elem:
                stock_text = stock_elem.get_text().lower()
                if 'indisponibil' in stock_text or 'stoc limitat' in stock_text:
                    availability = False
                    stock_status = "Stoc limitat"
            
            # Delivery info
            delivery_elem = element.find('span', class_=re.compile(r'delivery|shipping'))
            delivery_info = None
            if delivery_elem:
                delivery_info = self._clean_text(delivery_elem.get_text())
            
            return PriceCreate(
                product_id=0,  # Will be set by service
                retailer="eMAG",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=availability,
                stock_status=stock_status,
                url=product_url,
                is_promotional=is_promotional,
                promotion_text=promotion_text,
                delivery_info=delivery_info
            )
            
        except Exception as e:
            logger.error(f"Error extracting eMAG product data: {e}")
            return None
    
    def _extract_product_detail_data(self, soup: BeautifulSoup, url: str) -> Optional[PriceCreate]:
        """Extract product data from detail page"""
        try:
            # Price on detail page
            price_elem = soup.find('p', class_=re.compile(r'product-new-price'))
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            price = self._parse_price(price_text)
            
            if not price:
                return None
            
            # Original price
            original_price_elem = soup.find('p', class_=re.compile(r'product-old-price'))
            original_price = None
            is_promotional = False
            
            if original_price_elem:
                original_price = self._parse_price(original_price_elem.get_text())
                is_promotional = self._is_promotional(original_price, price)
            
            # Stock status
            stock_elem = soup.find('div', class_=re.compile(r'stock-availability'))
            stock_status = "In stoc"
            availability = True
            
            if stock_elem:
                stock_text = stock_elem.get_text().lower()
                if 'indisponibil' in stock_text:
                    availability = False
                    stock_status = "Indisponibil"
            
            return PriceCreate(
                product_id=0,
                retailer="eMAG",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=availability,
                stock_status=stock_status,
                url=url,
                is_promotional=is_promotional,
                promotion_text=None,
                delivery_info=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting eMAG detail data: {e}")
            return None

