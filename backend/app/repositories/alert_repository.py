"""Alert repository for database operations"""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate
import logging

logger = logging.getLogger(__name__)


class AlertRepository:
    """Repository for Alert model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert"""
        alert = Alert(**alert_data.model_dump())
        self.db.add(alert)
        await self.db.flush()
        await self.db.refresh(alert)
        return alert
    
    async def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get alert by ID"""
        result = await self.db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_product(self, product_id: int) -> List[Alert]:
        """Get all alerts for a product"""
        result = await self.db.execute(
            select(Alert).where(Alert.product_id == product_id)
        )
        return list(result.scalars().all())
    
    async def get_by_email(self, email: str) -> List[Alert]:
        """Get all alerts for a user email"""
        result = await self.db.execute(
            select(Alert).where(Alert.user_email == email)
        )
        return list(result.scalars().all())
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        result = await self.db.execute(
            select(Alert).where(Alert.is_active == True)
        )
        return list(result.scalars().all())
    
    async def update(self, alert_id: int, alert_data: AlertUpdate) -> Optional[Alert]:
        """Update alert"""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None
        
        for field, value in alert_data.model_dump(exclude_unset=True).items():
            setattr(alert, field, value)
        
        await self.db.flush()
        await self.db.refresh(alert)
        return alert
    
    async def delete(self, alert_id: int) -> bool:
        """Delete alert"""
        alert = await self.get_by_id(alert_id)
        if not alert:
            return False
        
        await self.db.delete(alert)
        await self.db.flush()
        return True

