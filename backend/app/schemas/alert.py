"""Alert schemas for API validation"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """Base alert schema"""
    
    user_email: EmailStr = Field(..., description="User email for notifications")
    target_price: float = Field(..., gt=0, description="Target price in RON")


class AlertCreate(AlertBase):
    """Schema for creating a new alert"""
    
    product_id: int


class AlertUpdate(BaseModel):
    """Schema for updating an alert"""
    
    target_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class AlertResponse(AlertBase):
    """Schema for alert response"""
    
    id: int
    product_id: int
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

