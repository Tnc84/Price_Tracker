"""Scraper API endpoints"""

from fastapi import APIRouter, Query
from typing import List
from app.services.scraper_service import ScraperService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.get("/retailers")
async def get_supported_retailers():
    """
    Get list of supported Romanian retailers
    
    Returns all retailers that can be scraped for price information
    """
    service = ScraperService()
    retailers = service.get_supported_retailers()
    return {
        "retailers": retailers,
        "count": len(retailers)
    }


@router.get("/search")
async def search_product(
    product_name: str = Query(..., min_length=2, description="Product name to search"),
    retailers: List[str] = Query(None, description="Specific retailers to search")
):
    """
    Search for a product across Romanian retailers without saving to database
    
    This is useful for quick price checks before creating a product
    
    - **product_name**: Name of the product to search
    - **retailers**: Optional list of specific retailers (defaults to all)
    """
    service = ScraperService()
    results = await service.search_all_retailers(product_name, retailers=retailers)
    
    # Format response with retailer status information
    total_found = sum(len(prices) for prices in results.values())
    retailer_status = {
        retailer: {
            "searched": True,
            "prices_found": len(prices),
            "success": len(prices) > 0
        }
        for retailer, prices in results.items()
    }
    
    return {
        "query": product_name,
        "total_prices_found": total_found,
        "results": results,
        "retailer_status": retailer_status
    }

