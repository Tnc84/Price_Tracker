"""Price API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.price import PriceResponse, PriceComparison, PriceHistory
from app.services.price_service import PriceService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/comparison/{product_id}", response_model=PriceComparison)
async def get_price_comparison(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive price comparison for a product across all retailers
    
    Returns:
    - Lowest, highest, and average prices
    - Price range and savings percentage
    - Best deal (retailer with lowest price)
    - All current prices from different retailers
    """
    service = PriceService(db)
    comparison = await service.get_price_comparison(product_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prices found for product ID {product_id}"
        )
    return comparison


@router.get("/history/{product_id}", response_model=PriceHistory)
async def get_price_history(
    product_id: int,
    retailer: str = Query(..., description="Retailer name (emag, altex, etc.)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get price history for a product at a specific retailer
    
    Returns:
    - Historical prices for the specified period
    - Average, minimum, and maximum prices
    - Price trend (increasing, decreasing, or stable)
    """
    service = PriceService(db)
    history = await service.get_price_history(product_id, retailer, days)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price history found for product ID {product_id} at {retailer}"
        )
    return history


@router.get("/deals", response_model=List[PriceResponse])
async def get_promotional_deals(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of deals to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current promotional deals across all retailers
    
    Returns products with active promotions and discounts
    """
    service = PriceService(db)
    return await service.get_promotional_deals(limit)

