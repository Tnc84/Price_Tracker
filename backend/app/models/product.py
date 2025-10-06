"""Product model for database"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """
    Product model representing items tracked across Romanian retailers
    
    Follows SOLID principles:
    - Single Responsibility: Manages product data only
    - Open/Closed: Can be extended without modification
    """
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    brand = Column(String(100), index=True)
    sku = Column(String(100), unique=True, index=True)
    image_url = Column(String(1000))
    is_active = Column(Boolean, default=True, index=True)
    target_price = Column(Float)  # User's desired price in RON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"

