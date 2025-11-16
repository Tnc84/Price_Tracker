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
        
        # Find product cards - try multiple selectors for eMAG
        # eMAG uses various class names: card-item, card-v2, card-body, etc.
        products = soup.find_all('div', class_=re.compile(r'card-item|card-v2|card-body|product-item'))
        
        # If no products found with those selectors, try alternative approach
        if not products:
            # Try finding by data attributes or other patterns
            products = soup.find_all('div', {'data-product-id': True})
        
        logger.info(f"Found {len(products)} product elements on eMAG for '{product_name}'")
        
        seen_urls = set()  # Track URLs to avoid duplicates
        extracted_count = 0
        
        for product in products[:20]:  # Increased limit to 20 to get more variety
            try:
                price_data = self._extract_product_data(product)
                if price_data and price_data.url:
                    # Only add if we haven't seen this URL before
                    if price_data.url not in seen_urls:
                        seen_urls.add(price_data.url)
                        prices.append(price_data)
                        extracted_count += 1
                        logger.debug(f"Extracted product {extracted_count}: {price_data.url} - {price_data.price} RON")
                    else:
                        logger.debug(f"Skipping duplicate URL: {price_data.url}")
            except Exception as e:
                logger.debug(f"Error extracting eMAG product data: {e}")
                continue
        
        logger.info(f"Successfully extracted {extracted_count} unique products from {len(products)} product elements")
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
            # Product name and URL - try multiple selectors
            name_elem = element.find('a', class_=re.compile(r'card-v2-title|product-title|title'))
            if not name_elem:
                # Try alternative: look for any link with href containing /p/
                name_elem = element.find('a', href=re.compile(r'/p/'))
            
            if not name_elem:
                # Try finding by data attributes
                name_elem = element.find('a', {'data-product-id': True})
            
            if not name_elem:
                return None
            
            name = self._clean_text(name_elem.get_text())
            
            # Product URL
            product_url = name_elem.get('href', '')
            if not product_url:
                # Try data-href or other attributes
                product_url = name_elem.get('data-href', '')
            
            if product_url and not product_url.startswith('http'):
                product_url = f"{self.BASE_URL}{product_url}"
            
            if not product_url:
                return None
            
            # Price extraction - try multiple selectors
            price_elem = element.find('p', class_=re.compile(r'product-new-price|price-new|new-price'))
            if not price_elem:
                price_elem = element.find('span', class_=re.compile(r'product-new-price|price-new'))
            if not price_elem:
                price_elem = element.find('div', class_=re.compile(r'product-new-price|price-new'))
            
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

