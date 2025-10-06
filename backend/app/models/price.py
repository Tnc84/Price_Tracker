"""Price model for database"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Price(Base):
    """
    Price model representing product prices from Romanian retailers
    
    Stores historical price data for trend analysis
    """
    
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    retailer = Column(String(100), nullable=False, index=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float)  # For promotional prices
    currency = Column(String(3), default="RON")
    availability = Column(Boolean, default=True)
    stock_status = Column(String(50))  # "In stock", "Limited", "Out of stock"
    url = Column(String(2000))
    is_promotional = Column(Boolean, default=False, index=True)
    promotion_text = Column(String(500))
    delivery_info = Column(String(200))  # "Livrare gratuita", "Livrare rapida"
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    product = relationship("Product", back_populates="prices")
    
    # Composite indexes for better query performance
    __table_args__ = (
        Index('idx_product_retailer_date', 'product_id', 'retailer', 'scraped_at'),
        Index('idx_retailer_promotional', 'retailer', 'is_promotional'),
    )
    
    def __repr__(self):
        return f"<Price(id={self.id}, product_id={self.product_id}, retailer='{self.retailer}', price={self.price})>"

