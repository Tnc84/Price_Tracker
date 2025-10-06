"""Price schemas for API validation"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class PriceBase(BaseModel):
    """Base price schema"""
    
    retailer: str = Field(..., min_length=1, max_length=100, description="Retailer name")
    price: float = Field(..., gt=0, description="Product price in RON")
    original_price: Optional[float] = Field(None, gt=0, description="Original price before discount")
    currency: str = Field("RON", max_length=3)
    availability: bool = True
    stock_status: Optional[str] = Field(None, max_length=50)
    url: Optional[str] = Field(None, max_length=2000, description="Product URL")
    is_promotional: bool = False
    promotion_text: Optional[str] = Field(None, max_length=500)
    delivery_info: Optional[str] = Field(None, max_length=200)


class PriceCreate(PriceBase):
    """Schema for creating a new price record"""
    
    product_id: int


class PriceResponse(PriceBase):
    """Schema for price response"""
    
    id: int
    product_id: int
    scraped_at: datetime
    
    class Config:
        from_attributes = True


class PriceComparison(BaseModel):
    """Schema for price comparison across retailers"""
    
    product_id: int
    product_name: str
    lowest_price: float
    highest_price: float
    average_price: float
    price_range: float
    savings_percentage: float
    retailers_count: int
    best_deal: PriceResponse
    all_prices: List[PriceResponse]


class PriceHistory(BaseModel):
    """Schema for price history over time"""
    
    product_id: int
    retailer: str
    prices: List[PriceResponse]
    avg_price: float
    min_price: float
    max_price: float
    trend: str  # "increasing", "decreasing", "stable"

