"""Product service for business logic"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.product_repository import ProductRepository
from app.repositories.price_repository import PriceRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductWithPrices
from app.models.product import Product
from app.services.scraper_service import ScraperService
from app.core.exceptions import ProductNotFoundException
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """
    Product service handling business logic
    
    Separates business logic from API routes and database operations
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.price_repo = PriceRepository(db)
        self.scraper_service = ScraperService()
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        # Check if product with same SKU exists
        if product_data.sku:
            existing = await self.product_repo.get_by_sku(product_data.sku)
            if existing:
                raise ValueError(f"Product with SKU '{product_data.sku}' already exists")
        
        product = await self.product_repo.create(product_data)
        logger.info(f"Created product: {product.name} (ID: {product.id})")
        return product
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        return await self.product_repo.get_by_id(product_id)
    
    async def get_product_with_prices(self, product_id: int) -> Optional[ProductWithPrices]:
        """Get product with current price information"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return None
        
        # Get latest prices
        latest_prices = await self.price_repo.get_latest_by_product(product_id)
        
        if not latest_prices:
            return ProductWithPrices(
                **product.__dict__,
                current_lowest_price=None,
                current_highest_price=None,
                price_drop_percentage=None,
                best_retailer=None,
                total_retailers=0
            )
        
        # Calculate price statistics
        available_prices = [p for p in latest_prices if p.availability]
        if not available_prices:
            return ProductWithPrices(
                **product.__dict__,
                current_lowest_price=None,
                current_highest_price=None,
                price_drop_percentage=None,
                best_retailer=None,
                total_retailers=len(latest_prices)
            )
        
        prices_list = [p.price for p in available_prices]
        lowest_price = min(prices_list)
        highest_price = max(prices_list)
        
        # Find best retailer
        best_price = min(available_prices, key=lambda p: p.price)
        
        # Calculate price drop if target price is set
        price_drop = None
        if product.target_price and lowest_price < product.target_price:
            price_drop = ((product.target_price - lowest_price) / product.target_price) * 100
        
        return ProductWithPrices(
            **product.__dict__,
            current_lowest_price=lowest_price,
            current_highest_price=highest_price,
            price_drop_percentage=price_drop,
            best_retailer=best_price.retailer,
            total_retailers=len(available_prices)
        )
    
    async def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """List products with filtering"""
        return await self.product_repo.list(skip, limit, category, brand, is_active)
    
    async def search_products(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products"""
        return await self.product_repo.search(query, skip, limit)
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = await self.product_repo.update(product_id, product_data)
        if not product:
            raise ProductNotFoundException(f"Product with ID {product_id} not found")
        
        logger.info(f"Updated product ID: {product_id}")
        return product
    
    async def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        success = await self.product_repo.delete(product_id)
        if success:
            logger.info(f"Deleted product ID: {product_id}")
        return success
    
    async def scrape_product_prices(self, product_id: int, retailers: List[str] = None) -> int:
        """
        Scrape prices for a product from all retailers
        
        Returns number of prices found
        """
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ProductNotFoundException(f"Product with ID {product_id} not found")
        
        # Search all retailers
        results = await self.scraper_service.search_all_retailers(
            product.name,
            product.category,
            retailers
        )
        
        # Save prices to database
        total_saved = 0
        for retailer, prices in results.items():
            for price_data in prices:
                price_data.product_id = product_id
                await self.price_repo.create(price_data)
                total_saved += 1
        
        await self.db.commit()
        
        logger.info(f"Scraped and saved {total_saved} prices for product ID {product_id}")
        return total_saved

