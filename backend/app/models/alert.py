"""Alert model for database"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Alert(Base):
    """
    Alert model for price drop notifications
    
    Notifies users when product prices drop below target
    """
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_email = Column(String(255), nullable=False, index=True)
    target_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True))
    last_checked_at = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, product_id={self.product_id}, target_price={self.target_price})>"

