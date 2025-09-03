"""
FastAPI application setup for Truth and Dare API.

This module sets up the FastAPI application with all routes, middleware,
exception handlers, and configuration.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.exceptions import TruthDareAPIException
from app.routes import dare, game, truth
from app.utils.data_loader import get_data_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Truth and Dare API...")

    try:
        # Pre-load data cache during startup
        data_cache = get_data_cache()
        data_cache.load_data()
        stats = data_cache.get_stats()
        logger.info(
            f"Data loaded successfully: {stats['total_truths']} truths, {stats['total_dares']} dares"
        )
    except Exception as e:
        logger.error(f"Failed to load data during startup: {e}")
        # Don't prevent startup, but log the error

    logger.info("Truth and Dare API startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Truth and Dare API...")
    logger.info("Truth and Dare API shutdown complete")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    # Create FastAPI application
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include routers with API prefix
    app.include_router(truth.router, prefix=settings.api_v1_prefix)
    app.include_router(dare.router, prefix=settings.api_v1_prefix)
    app.include_router(game.router, prefix=settings.api_v1_prefix)

    return app


# Create the FastAPI application
app = create_application()


@app.exception_handler(TruthDareAPIException)
async def truth_dare_exception_handler(
    request: Request, exc: TruthDareAPIException
) -> JSONResponse:
    """
    Handle custom Truth and Dare API exceptions.

    Args:
        request: The HTTP request
        exc: The custom exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"TruthDareAPIException: {exc.message} (status: {exc.status_code})")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: The HTTP request
        exc: The validation exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {"validation_errors": exc.errors()},
            "status_code": 422,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: The HTTP request
        exc: The HTTP exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"HTTP exception: {exc.detail} (status: {exc.status_code})")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "details": {},
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: The HTTP request
        exc: The exception

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {},
            "status_code": 500,
        },
    )


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """
    Root endpoint that redirects to API documentation.

    Returns:
        Dict[str, str]: Welcome message and links
    """
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
