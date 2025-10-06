"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings and configuration
    
    Follows best practices:
    - Environment-based configuration
    - Type-safe settings
    - No hardcoded values
    """
    
    # Application
    app_name: str = "Romanian Price Tracker"
    debug: bool = False
    version: str = "1.0.0"
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/promotion_search"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Scraping configuration for Romanian retailers
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    request_delay: float = 2.0  # Respect Romanian sites
    max_concurrent_requests: int = 3
    
    # Scrapers
    enable_selenium: bool = True
    headless_browser: bool = True
    
    # API
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Romanian locale
    currency: str = "RON"
    locale: str = "ro_RO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

