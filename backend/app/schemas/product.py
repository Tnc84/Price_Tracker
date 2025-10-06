"""Product schemas for API validation"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema with common fields"""
    
    name: str = Field(..., min_length=1, max_length=500, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")
    sku: Optional[str] = Field(None, max_length=100, description="Product SKU")
    image_url: Optional[str] = Field(None, max_length=1000, description="Product image URL")
    target_price: Optional[float] = Field(None, gt=0, description="Target price in RON")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProductWithPrices(ProductResponse):
    """Product with current price information"""
    
    current_lowest_price: Optional[float] = None
    current_highest_price: Optional[float] = None
    price_drop_percentage: Optional[float] = None
    best_retailer: Optional[str] = None
    total_retailers: int = 0


class ProductSearch(BaseModel):
    """Schema for product search"""
    
    query: str = Field(..., min_length=2, description="Search query")
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)

