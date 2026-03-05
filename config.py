"""
Configuration and logging setup for HireMate AI.
"""
import logging
import logging.config
import sys
from typing import Optional

# Configure logging format
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "hiremate.log",
            "mode": "a",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Setup and return a logger instance.
    
    Args:
        name: Logger name (defaults to __name__)
    
    Returns:
        Configured logger instance
    """
    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    logger = logging.getLogger(name or __name__)
    return logger


# Default logger
logger = setup_logging("hiremate")


# Application settings
class Settings:
    """Application configuration settings."""
    
    # File validation
    MAX_FILE_SIZE_MB: int = 5
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_CONTENT_TYPES: list = ["application/pdf"]
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    # Job description validation
    MIN_JOB_DESCRIPTION_LENGTH: int = 10
    MAX_JOB_DESCRIPTION_LENGTH: int = 10000
    
    # API settings
    API_TITLE: str = "HireMate AI"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "AI-powered resume analysis and job application assistant"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # AI settings
    GEMINI_MODEL: str = "gemini-2.0-flash"
    MAX_TOKENS_SUMMARY: int = 500
    MAX_TOKENS_COVER_LETTER: int = 1000


# Create settings instance
settings = Settings()

