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
        
        # If still no products, try finding any div with a product link inside
        if not products:
            # Look for divs containing links with /p/ in href
            all_divs = soup.find_all('div')
            products = [div for div in all_divs if div.find('a', href=re.compile(r'/p/'))]
        
        logger.info(f"Found {len(products)} product elements on eMAG for '{product_name}'")
        
        seen_urls = set()  # Track URLs to avoid duplicates
        extracted_count = 0
        
        # Process more products to ensure we get at least 3 different ones
        failed_extractions = 0
        # Increase to 50 to ensure we get at least 3 valid products
        for idx, product in enumerate(products[:50]):
            try:
                price_data = self._extract_product_data(product)
                if price_data and price_data.url:
                    # Only add if we haven't seen this URL before
                    if price_data.url not in seen_urls:
                        seen_urls.add(price_data.url)
                        prices.append(price_data)
                        extracted_count += 1
                        logger.info(f"Extracted product {extracted_count}: {price_data.url} - {price_data.price} RON")
                        
                        # Stop early if we have enough unique products
                        if extracted_count >= 5:  # Get at least 5 to ensure top 3 selection
                            logger.info(f"Reached target of {extracted_count} products, stopping early")
                            break
                    else:
                        logger.debug(f"Skipping duplicate URL: {price_data.url}")
                else:
                    failed_extractions += 1
                    if idx < 10:  # Log first 10 failures for debugging
                        logger.debug(f"Failed to extract product {idx + 1}: No valid data returned")
            except Exception as e:
                failed_extractions += 1
                if idx < 10:  # Log first 10 failures for debugging
                    logger.warning(f"Error extracting eMAG product {idx + 1}: {str(e)}")
                continue
        
        if failed_extractions > 0:
            logger.warning(f"Failed to extract {failed_extractions} out of {min(50, len(products))} products - selectors may need updating")
        
        if extracted_count < 3:
            logger.error(f"Only extracted {extracted_count} products, expected at least 3. HTML structure may have changed.")
        
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
            # eMAG uses various structures, try all common patterns
            name_elem = None
            
            # Strategy 1: Look for links with product URLs (most reliable)
            all_links = element.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                # eMAG product URLs typically contain /p/ or /product/
                if '/p/' in href or '/product/' in href or 'emag.ro' in href:
                    name_elem = link
                    break
            
            # Strategy 2: Try class-based selectors
            if not name_elem:
                name_elem = element.find('a', class_=re.compile(r'card-v2-title|product-title|title|product-name'))
            
            # Strategy 3: Try data attributes
            if not name_elem:
                name_elem = element.find('a', {'data-product-id': True})
            
            # Strategy 4: Look for any link in the element
            if not name_elem:
                name_elem = element.find('a', href=True)
            
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
            
            # Price extraction - try multiple selectors and strategies
            price_elem = None
            
            # Strategy 1: Look for price in common class names
            price_elem = element.find('p', class_=re.compile(r'product-new-price|price-new|new-price|product-price'))
            if not price_elem:
                price_elem = element.find('span', class_=re.compile(r'product-new-price|price-new|new-price|product-price'))
            if not price_elem:
                price_elem = element.find('div', class_=re.compile(r'product-new-price|price-new|new-price|product-price'))
            
            # Strategy 2: Look for price patterns in text (contains "RON" or "lei")
            if not price_elem:
                all_text_elements = element.find_all(['p', 'span', 'div'])
                for elem in all_text_elements:
                    text = elem.get_text().strip()
                    # Look for price patterns like "77,99 RON" or "77.99 lei"
                    if re.search(r'\d+[.,]\d+\s*(RON|lei|LEI)', text, re.IGNORECASE):
                        price_elem = elem
                        break
            
            # Strategy 3: Look for any element containing price-like patterns
            if not price_elem:
                price_pattern = re.compile(r'\d+[.,]\d+')
                for tag in ['p', 'span', 'div', 'strong', 'b']:
                    for elem in element.find_all(tag):
                        text = elem.get_text().strip()
                        if price_pattern.search(text) and len(text) < 50:  # Price text is usually short
                            # Check if it looks like a price (has decimal separator)
                            if ',' in text or '.' in text:
                                price_elem = elem
                                break
                    if price_elem:
                        break
            
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

