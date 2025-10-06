"""Product API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithPrices
)
from app.services.product_service import ProductService
from app.core.exceptions import ProductNotFoundException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new product to track
    
    - **name**: Product name (required)
    - **description**: Product description
    - **category**: Product category
    - **brand**: Product brand
    - **sku**: Product SKU (unique)
    - **target_price**: Desired target price in RON
    """
    try:
        service = ProductService(db)
        return await service.create_product(product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all products with optional filtering
    
    Supports pagination and filtering by category, brand, and active status
    """
    service = ProductService(db)
    return await service.list_products(skip, limit, category, brand, is_active)


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Search products by name, description, or brand
    
    - **q**: Search query (minimum 2 characters)
    """
    service = ProductService(db)
    return await service.search_products(q, skip, limit)


@router.get("/{product_id}", response_model=ProductWithPrices)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details with current price information
    
    Returns product info along with:
    - Lowest current price
    - Highest current price
    - Best retailer
    - Number of retailers with availability
    """
    service = ProductService(db)
    product = await service.get_product_with_prices(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update product information
    
    All fields are optional - only provided fields will be updated
    """
    try:
        service = ProductService(db)
        return await service.update_product(product_id, product_update)
    except ProductNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a product and all its associated data
    
    This will also delete all price history and alerts for this product
    """
    service = ProductService(db)
    success = await service.delete_product(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )


@router.post("/{product_id}/scrape")
async def scrape_product_prices(
    product_id: int,
    retailers: Optional[List[str]] = Query(None, description="Specific retailers to scrape"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger price scraping for a specific product
    
    This will search for the product across all Romanian retailers and update prices
    
    - **retailers**: Optional list of specific retailers (emag, altex, carrefour, kaufland, selgros)
    """
    try:
        service = ProductService(db)
        total_prices = await service.scrape_product_prices(product_id, retailers)
        return {
            "message": "Price scraping completed",
            "product_id": product_id,
            "prices_found": total_prices
        }
    except ProductNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.message))

