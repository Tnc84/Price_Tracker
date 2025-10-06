"""Selgros scraper - Cash & Carry retailer"""

from typing import List, Optional
from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseScraper
from app.schemas.price import PriceCreate
import re
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class SelgrosScraper(BaseScraper):
    """
    Scraper for Selgros.ro - Cash & Carry products
    
    Base URL: https://www.selgros.ro
    """
    
    BASE_URL = "https://www.selgros.ro"
    SEARCH_URL = "https://www.selgros.ro/search"
    
    def __init__(self):
        super().__init__("Selgros")
    
    async def search_product(self, product_name: str, category: Optional[str] = None) -> List[PriceCreate]:
        """Search Selgros for products"""
        prices = []
        
        search_query = quote_plus(product_name)
        search_url = f"{self.SEARCH_URL}?q={search_query}"
        
        html = await self._make_request(search_url)
        if not html:
            logger.warning(f"Failed to fetch Selgros search results for '{product_name}'")
            return prices
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find product cards
        products = soup.find_all('div', class_=re.compile(r'product-item|productCard'))
        
        logger.info(f"Found {len(products)} products on Selgros for '{product_name}'")
        
        for product in products[:15]:
            try:
                price_data = self._extract_product_data(product)
                if price_data:
                    prices.append(price_data)
            except Exception as e:
                logger.error(f"Error extracting Selgros product data: {e}")
                continue
                
        return prices
    
    async def get_product_price(self, product_url: str) -> Optional[PriceCreate]:
        """Get current price for specific Selgros product"""
        html = await self._make_request(product_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'lxml')
        return self._extract_product_detail_data(soup, product_url)
    
    def _extract_product_data(self, element) -> Optional[PriceCreate]:
        """Extract product data from search result"""
        try:
            # Product name
            name_elem = element.find('a', class_=re.compile(r'product-title|product-name'))
            if not name_elem:
                name_elem = element.find('h3')
            
            if not name_elem:
                return None
            
            name = self._clean_text(name_elem.get_text())
            
            # Product URL
            product_url = name_elem.get('href', '')
            if product_url and not product_url.startswith('http'):
                product_url = f"{self.BASE_URL}{product_url}"
            
            # Price
            price_elem = element.find('span', class_=re.compile(r'price-value|product-price'))
            if not price_elem:
                price_elem = element.find('div', class_=re.compile(r'price'))
            
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            price = self._parse_price(price_text)
            
            if not price:
                return None
            
            # Check for promotional pricing
            old_price_elem = element.find('span', class_=re.compile(r'old-price|price-was'))
            original_price = None
            is_promotional = False
            promotion_text = None
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                if original_price and price < original_price:
                    is_promotional = True
                    discount = ((original_price - price) / original_price) * 100
                    promotion_text = f"Discount {discount:.0f}%"
            
            # Check for promotion badge
            promo_elem = element.find('div', class_=re.compile(r'promo|discount-badge'))
            if promo_elem:
                is_promotional = True
                badge_text = self._clean_text(promo_elem.get_text())
                if badge_text and not promotion_text:
                    promotion_text = badge_text
            
            # Availability
            stock_elem = element.find('span', class_=re.compile(r'stock|availability'))
            availability = True
            stock_status = "In stoc"
            
            if stock_elem:
                stock_text = stock_elem.get_text().lower()
                if 'indisponibil' in stock_text or 'stoc epuizat' in stock_text:
                    availability = False
                    stock_status = "Indisponibil"
            
            return PriceCreate(
                product_id=0,
                retailer="Selgros",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=availability,
                stock_status=stock_status,
                url=product_url,
                is_promotional=is_promotional,
                promotion_text=promotion_text,
                delivery_info=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting Selgros product data: {e}")
            return None
    
    def _extract_product_detail_data(self, soup: BeautifulSoup, url: str) -> Optional[PriceCreate]:
        """Extract product data from detail page"""
        try:
            price_elem = soup.find('span', class_=re.compile(r'price-value'))
            if not price_elem:
                return None
            
            price = self._parse_price(price_elem.get_text())
            if not price:
                return None
            
            old_price_elem = soup.find('span', class_=re.compile(r'old-price'))
            original_price = None
            is_promotional = False
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                is_promotional = self._is_promotional(original_price, price)
            
            return PriceCreate(
                product_id=0,
                retailer="Selgros",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=True,
                stock_status="In stoc",
                url=url,
                is_promotional=is_promotional,
                promotion_text=None,
                delivery_info=None
            )
            
        except Exception as e:
            logger.error(f"Error extracting Selgros detail data: {e}")
            return None

