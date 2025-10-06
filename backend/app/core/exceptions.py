"""Custom exceptions for the application"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ScraperException(AppException):
    """Exception raised during web scraping"""
    pass


class ProductNotFoundException(AppException):
    """Exception raised when product is not found"""
    pass


class InvalidPriceException(AppException):
    """Exception raised when price data is invalid"""
    pass


class RetailerUnavailableException(AppException):
    """Exception raised when retailer website is unavailable"""
    pass

