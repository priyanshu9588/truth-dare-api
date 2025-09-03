"""
Core configuration module for Truth and Dare API.

This module handles all application configuration using Pydantic Settings
for type safety and validation.
"""

from functools import lru_cache

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables
    with the prefix 'TRUTH_DARE_'.
    """

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Data Configuration
    truths_file_path: str = "app/data/truths.json"
    dares_file_path: str = "app/data/dares.json"

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Performance Configuration
    cache_expiry_seconds: int = 3600
    max_concurrent_requests: int = 1000

    # Application Information
    app_name: str = "Truth and Dare API"
    app_version: str = "0.1.0"
    app_description: str = (
        "A FastAPI-based REST API providing questions and challenges for the classic party game"
    )

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v

    class Config:
        env_prefix = "TRUTH_DARE_"
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are loaded only once
    during the application lifecycle.

    Returns:
        Settings: Application configuration object
    """
    return Settings()
