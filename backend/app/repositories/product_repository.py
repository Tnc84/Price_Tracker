"""Product repository for database operations"""

from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
import logging

logger = logging.getLogger(__name__)


class ProductRepository:
    """
    Repository for Product model following Repository pattern
    
    Benefits:
    - Separation of concerns (database logic separate from business logic)
    - Easy testing with mock repositories
    - Database agnostic interface
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        result = await self.db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Product]:
        """List products with optional filtering"""
        query = select(Product)
        
        # Apply filters
        conditions = []
        if category:
            conditions.append(Product.category == category)
        if brand:
            conditions.append(Product.brand == brand)
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Search products by name or description"""
        search_query = select(Product).where(
            or_(
                Product.name.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%"),
                Product.brand.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(search_query)
        return list(result.scalars().all())
    
    async def update(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        # Update only provided fields
        for field, value in product_data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Delete product"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.delete(product)
        await self.db.flush()
        return True
    
    async def count(self, is_active: Optional[bool] = None) -> int:
        """Count products"""
        from sqlalchemy import func
        
        query = select(func.count(Product.id))
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar_one()

