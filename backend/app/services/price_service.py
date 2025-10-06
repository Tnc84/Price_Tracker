"""Price service for business logic"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.price_repository import PriceRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.price import PriceCreate, PriceComparison, PriceHistory
from app.models.price import Price
import logging

logger = logging.getLogger(__name__)


class PriceService:
    """Service for price-related business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.price_repo = PriceRepository(db)
        self.product_repo = ProductRepository(db)
    
    async def get_price_comparison(self, product_id: int) -> Optional[PriceComparison]:
        """Get comprehensive price comparison for a product"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return None
        
        latest_prices = await self.price_repo.get_latest_by_product(product_id)
        if not latest_prices:
            return None
        
        # Filter available prices
        available_prices = [p for p in latest_prices if p.availability]
        if not available_prices:
            return None
        
        # Calculate statistics
        price_values = [p.price for p in available_prices]
        lowest_price = min(price_values)
        highest_price = max(price_values)
        average_price = sum(price_values) / len(price_values)
        price_range = highest_price - lowest_price
        
        # Calculate savings
        savings_percentage = ((highest_price - lowest_price) / highest_price) * 100 if highest_price > 0 else 0
        
        # Find best deal
        best_deal = min(available_prices, key=lambda p: p.price)
        
        return PriceComparison(
            product_id=product_id,
            product_name=product.name,
            lowest_price=lowest_price,
            highest_price=highest_price,
            average_price=round(average_price, 2),
            price_range=round(price_range, 2),
            savings_percentage=round(savings_percentage, 2),
            retailers_count=len(available_prices),
            best_deal=best_deal,
            all_prices=available_prices
        )
    
    async def get_price_history(
        self,
        product_id: int,
        retailer: str,
        days: int = 30
    ) -> Optional[PriceHistory]:
        """Get price history for a product at a retailer"""
        prices = await self.price_repo.get_price_history(product_id, retailer, days)
        if not prices:
            return None
        
        price_values = [p.price for p in prices]
        avg_price = sum(price_values) / len(price_values)
        min_price = min(price_values)
        max_price = max(price_values)
        
        # Determine trend
        if len(prices) >= 2:
            recent_avg = sum(p.price for p in prices[:len(prices)//2]) / (len(prices)//2)
            older_avg = sum(p.price for p in prices[len(prices)//2:]) / (len(prices) - len(prices)//2)
            
            if recent_avg > older_avg * 1.05:
                trend = "increasing"
            elif recent_avg < older_avg * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return PriceHistory(
            product_id=product_id,
            retailer=retailer,
            prices=prices,
            avg_price=round(avg_price, 2),
            min_price=min_price,
            max_price=max_price,
            trend=trend
        )
    
    async def get_promotional_deals(self, limit: int = 20) -> List[Price]:
        """Get current promotional deals"""
        return await self.price_repo.get_promotional_deals(limit)

