"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import products, prices, scraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Romanian Price Tracker API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    description="""
    ## 🇷🇴 Romanian Price Tracker API
    
    A comprehensive price comparison API for Romanian retailers including:
    - **eMAG** - Romania's largest online marketplace
    - **Altex** - Electronics and home appliances
    - **Carrefour** - Supermarket and general goods
    - **Kaufland** - Supermarket products
    - **Selgros** - Cash & Carry products
    
    ### Features:
    - 🔍 Search products across multiple retailers
    - 💰 Real-time price comparison
    - 📊 Price history and trends
    - 🔔 Price drop alerts
    - 🎯 Target price notifications
    
    ### Getting Started:
    1. Create a product using POST /products/
    2. Scrape prices using POST /products/{id}/scrape
    3. Get price comparison using GET /prices/comparison/{id}
    """,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix=settings.api_prefix)
app.include_router(prices.router, prefix=settings.api_prefix)
app.include_router(scraper.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🇷🇴 Romanian Price Tracker API",
        "version": settings.version,
        "status": "healthy",
        "docs": "/docs",
        "supported_retailers": [
            "eMAG",
            "Altex",
            "Carrefour",
            "Kaufland",
            "Selgros"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "scrapers": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

