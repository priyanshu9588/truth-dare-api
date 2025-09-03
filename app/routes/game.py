"""
Game and health API routes for Truth and Dare API.

This module defines endpoints for game logic and health checks.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.core.exceptions import TruthDareAPIException
from app.models.responses import ErrorResponse, GameResponse, HealthResponse, StatsResponse
from app.services.game_service import get_game_service

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["game"], responses={500: {"model": ErrorResponse, "description": "Internal server error"}}
)


@router.get(
    "/game/random",
    response_model=GameResponse,
    summary="Get Random Truth or Dare",
    description="Get a random choice between a truth question or dare challenge.",
    response_description="A randomly selected truth question or dare challenge",
)
async def get_random_game() -> GameResponse:
    """
    Get a random choice between a truth question or dare challenge.

    Uses 50/50 probability to randomly select either a truth question or dare challenge.
    The response will include a 'type' field indicating whether it's a truth or dare.

    For truths:
    - Includes: id, type, content, category

    For dares:
    - Includes: id, type, content, difficulty

    Returns:
        GameResponse: Random truth question or dare challenge

    Raises:
        HTTPException: If no data is available (500)
    """
    try:
        game_service = get_game_service()
        game_data = game_service.get_random_choice()

        # Create response based on type
        if game_data["type"] == "truth":
            return GameResponse(
                id=game_data["id"],
                type=game_data["type"],
                content=game_data["content"],
                category=game_data["category"],
                difficulty=None,
            )
        # dare
        return GameResponse(
            id=game_data["id"],
            type=game_data["type"],
            content=game_data["content"],
            category=None,
            difficulty=game_data["difficulty"],
        )
    except TruthDareAPIException as e:
        logger.error(f"API error getting random game: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting random game: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Get the health status of the API and its data sources.",
    response_description="Health status information including data availability",
)
async def health_check() -> HealthResponse:
    """
    Get the health status of the API.

    Checks the availability and integrity of truth and dare data sources.
    Returns status information and basic statistics.

    Health statuses:
    - healthy: All systems operational, data available
    - degraded: Some issues but API still functional
    - unhealthy: Major issues, API may not function properly

    Returns:
        HealthResponse: Health status and statistics
    """
    try:
        game_service = get_game_service()
        health_data = game_service.get_health_status()

        return HealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}")
        # Return unhealthy status if health check itself fails
        return HealthResponse(
            status="unhealthy",
            timestamp="",
            data={
                "total_truths": 0,
                "total_dares": 0,
                "truth_categories": 0,
                "dare_difficulties": 0,
            },
            categories={},
            difficulties={},
            error=str(e),
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get Statistics",
    description="Get comprehensive statistics about available truths and dares.",
    response_description="Detailed statistics about all available content",
)
async def get_stats() -> StatsResponse:
    """
    Get comprehensive statistics about available truths and dares.

    Returns detailed information about:
    - Total counts for truths and dares
    - Breakdown by categories and difficulty levels
    - Available categories and difficulties

    Returns:
        StatsResponse: Comprehensive statistics

    Raises:
        HTTPException: If server error occurs (500)
    """
    try:
        game_service = get_game_service()
        stats_data = game_service.get_game_stats()

        return StatsResponse(**stats_data)
    except Exception as e:
        logger.error(f"Unexpected error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
