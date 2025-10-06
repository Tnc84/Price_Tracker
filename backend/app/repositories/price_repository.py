"""Price repository for database operations"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.price import Price
from app.schemas.price import PriceCreate
import logging

logger = logging.getLogger(__name__)


class PriceRepository:
    """Repository for Price model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, price_data: PriceCreate) -> Price:
        """Create a new price record"""
        price = Price(**price_data.model_dump())
        self.db.add(price)
        await self.db.flush()
        await self.db.refresh(price)
        return price
    
    async def create_many(self, price_data_list: List[PriceCreate]) -> List[Price]:
        """Create multiple price records (bulk insert)"""
        prices = [Price(**price_data.model_dump()) for price_data in price_data_list]
        self.db.add_all(prices)
        await self.db.flush()
        return prices
    
    async def get_by_id(self, price_id: int) -> Optional[Price]:
        """Get price by ID"""
        result = await self.db.execute(
            select(Price).where(Price.id == price_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_product_id(self, product_id: int, limit: int = 50) -> List[Price]:
        """Get all prices for a product (recent first)"""
        result = await self.db.execute(
            select(Price)
            .where(Price.product_id == product_id)
            .order_by(desc(Price.scraped_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_latest_by_product(self, product_id: int) -> List[Price]:
        """Get the latest price from each retailer for a product"""
        from sqlalchemy import distinct
        
        # Subquery to get latest scrape time per retailer
        subquery = (
            select(
                Price.retailer,
                func.max(Price.scraped_at).label('max_scraped')
            )
            .where(Price.product_id == product_id)
            .group_by(Price.retailer)
            .subquery()
        )
        
        # Get prices matching latest scrape time
        result = await self.db.execute(
            select(Price)
            .join(
                subquery,
                and_(
                    Price.retailer == subquery.c.retailer,
                    Price.scraped_at == subquery.c.max_scraped,
                    Price.product_id == product_id
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_lowest_price(self, product_id: int) -> Optional[Price]:
        """Get the lowest current price for a product"""
        latest_prices = await self.get_latest_by_product(product_id)
        if not latest_prices:
            return None
        
        # Filter only available products
        available_prices = [p for p in latest_prices if p.availability]
        if not available_prices:
            return None
        
        return min(available_prices, key=lambda p: p.price)
    
    async def get_recent_prices(self, product_id: int, days: int = 30) -> List[Price]:
        """Get prices from the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Price)
            .where(
                and_(
                    Price.product_id == product_id,
                    Price.scraped_at >= since_date
                )
            )
            .order_by(desc(Price.scraped_at))
        )
        return list(result.scalars().all())
    
    async def get_promotional_deals(self, limit: int = 20) -> List[Price]:
        """Get current promotional deals"""
        # Get latest prices that are promotional
        result = await self.db.execute(
            select(Price)
            .where(
                and_(
                    Price.is_promotional == True,
                    Price.availability == True
                )
            )
            .order_by(desc(Price.scraped_at))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_price_history(
        self,
        product_id: int,
        retailer: str,
        days: int = 30
    ) -> List[Price]:
        """Get price history for a product at a specific retailer"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(Price)
            .where(
                and_(
                    Price.product_id == product_id,
                    Price.retailer == retailer,
                    Price.scraped_at >= since_date
                )
            )
            .order_by(Price.scraped_at)
        )
        return list(result.scalars().all())
    
    async def get_by_retailer(self, retailer: str, limit: int = 100) -> List[Price]:
        """Get latest prices from a specific retailer"""
        result = await self.db.execute(
            select(Price)
            .where(Price.retailer == retailer)
            .order_by(desc(Price.scraped_at))
            .limit(limit)
        )
        return list(result.scalars().all())

