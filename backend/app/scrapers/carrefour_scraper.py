"""Carrefour scraper - Supermarket chain"""

from typing import List, Optional
from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseScraper
from app.schemas.price import PriceCreate
import re
import logging
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class CarrefourScraper(BaseScraper):
    """
    Scraper for Carrefour.ro - Supermarket and general goods
    
    Base URL: https://www.carrefour.ro
    """
    
    BASE_URL = "https://www.carrefour.ro"
    SEARCH_URL = "https://www.carrefour.ro/cautare"
    
    def __init__(self):
        super().__init__("Carrefour")
    
    async def search_product(self, product_name: str, category: Optional[str] = None) -> List[PriceCreate]:
        """Search Carrefour for products"""
        prices = []
        
        search_query = quote_plus(product_name)
        search_url = f"{self.SEARCH_URL}?q={search_query}"
        
        html = await self._make_request(search_url)
        if not html:
            logger.warning(f"Failed to fetch Carrefour search results for '{product_name}'")
            return prices
            
        soup = BeautifulSoup(html, 'lxml')
        
        # Find product cards
        products = soup.find_all('div', class_=re.compile(r'product-tile|productCard'))
        
        logger.info(f"Found {len(products)} products on Carrefour for '{product_name}'")
        
        for product in products[:15]:
            try:
                price_data = self._extract_product_data(product)
                if price_data:
                    prices.append(price_data)
            except Exception as e:
                logger.error(f"Error extracting Carrefour product data: {e}")
                continue
                
        return prices
    
    async def get_product_price(self, product_url: str) -> Optional[PriceCreate]:
        """Get current price for specific Carrefour product"""
        html = await self._make_request(product_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'lxml')
        return self._extract_product_detail_data(soup, product_url)
    
    def _extract_product_data(self, element) -> Optional[PriceCreate]:
        """Extract product data from search result"""
        try:
            # Product name and link
            name_elem = element.find('a', class_=re.compile(r'product-name|title'))
            if not name_elem:
                name_elem = element.find('h3')
            
            if not name_elem:
                return None
            
            name = self._clean_text(name_elem.get_text())
            product_url = name_elem.get('href', '')
            if product_url and not product_url.startswith('http'):
                product_url = f"{self.BASE_URL}{product_url}"
            
            # Price
            price_elem = element.find('span', class_=re.compile(r'product-price|price-sales'))
            if not price_elem:
                price_elem = element.find('span', attrs={'data-price': True})
            
            if not price_elem:
                return None
            
            price_text = price_elem.get_text().strip()
            if not price_text and price_elem.get('data-price'):
                price_text = price_elem.get('data-price')
            
            price = self._parse_price(price_text)
            if not price:
                return None
            
            # Promotional price
            old_price_elem = element.find('span', class_=re.compile(r'price-standard|old-price'))
            original_price = None
            is_promotional = False
            promotion_text = None
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                if original_price and price < original_price:
                    is_promotional = True
                    discount = ((original_price - price) / original_price) * 100
                    promotion_text = f"Discount {discount:.0f}%"
            
            # Check for promotion labels
            promo_elem = element.find('span', class_=re.compile(r'promotion|badge'))
            if promo_elem and not promotion_text:
                promotion_text = self._clean_text(promo_elem.get_text())
                is_promotional = True
            
            return PriceCreate(
                product_id=0,
                retailer="Carrefour",
                price=price,
                original_price=original_price,
                currency="RON",
                availability=True,
                stock_status="In stoc",
                url=product_url,
                is_promotional=is_promotional,
                promotion_text=promotion_text,
                delivery_info="Livrare disponibila"
            )
            
        except Exception as e:
            logger.error(f"Error extracting Carrefour product data: {e}")
            return None
    
    def _extract_product_detail_data(self, soup: BeautifulSoup, url: str) -> Optional[PriceCreate]:
        """Extract product data from detail page"""
        try:
            price_elem = soup.find('span', class_=re.compile(r'product-price|price-sales'))
            if not price_elem:
                return None
            
            price = self._parse_price(price_elem.get_text())
            if not price:
                return None
            
            old_price_elem = soup.find('span', class_=re.compile(r'price-standard'))
            original_price = None
            is_promotional = False
            
            if old_price_elem:
                original_price = self._parse_price(old_price_elem.get_text())
                is_promotional = self._is_promotional(original_price, price)
            
            return PriceCreate(
                product_id=0,
                retailer="Carrefour",
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
            logger.error(f"Error extracting Carrefour detail data: {e}")
            return None

