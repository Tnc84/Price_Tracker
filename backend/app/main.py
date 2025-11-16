"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import products, prices, scraper
import logging
import os

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
    - **eMAG** - Romania's largest online marketplace ✅ (Active)
    - **Altex** - Electronics and home appliances ⏸️ (Temporarily disabled)
    - **Carrefour** - Supermarket and general goods ⏸️ (Temporarily disabled)
    - **Kaufland** - Supermarket products ⏸️ (Temporarily disabled)
    - **Selgros** - Cash & Carry products ⏸️ (Temporarily disabled)
    
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

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve the main search UI page"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "🇷🇴 Romanian Price Tracker API",
        "version": settings.version,
        "status": "healthy",
        "docs": "/docs",
        "supported_retailers": [
            "eMAG",
            # "Altex",  # Temporarily disabled
            # "Carrefour",  # Temporarily disabled
            # "Kaufland",  # Temporarily disabled
            # "Selgros"  # Temporarily disabled
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

