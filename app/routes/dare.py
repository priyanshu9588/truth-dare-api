"""
Dare-related API routes for Truth and Dare API.

This module defines all endpoints related to dare challenges.
"""

import logging

from fastapi import APIRouter, HTTPException, Path

from app.core.exceptions import TruthDareAPIException
from app.models.responses import DareResponse, ErrorResponse
from app.services.dare_service import get_dare_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dare",
    tags=["dares"],
    responses={
        404: {"model": ErrorResponse, "description": "Difficulty not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


@router.get(
    "",
    response_model=DareResponse,
    summary="Get Random Dare",
    description="Get a random dare challenge from all available difficulty levels.",
    response_description="A random dare challenge with its difficulty level",
)
async def get_random_dare() -> DareResponse:
    """
    Get a random dare challenge.

    Returns a randomly selected dare challenge from all available difficulty levels.
    Each dare includes an ID, content, and difficulty level.

    Returns:
        DareResponse: Random dare challenge

    Raises:
        HTTPException: If no dares are available (500)
    """
    try:
        dare_service = get_dare_service()
        dare_data = dare_service.get_random_dare()

        return DareResponse(
            id=dare_data["id"], content=dare_data["content"], difficulty=dare_data["difficulty"]
        )
    except TruthDareAPIException as e:
        logger.error(f"API error getting random dare: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting random dare: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{difficulty}",
    response_model=DareResponse,
    summary="Get Dare by Difficulty",
    description="Get a random dare challenge from a specific difficulty level.",
    response_description="A random dare challenge from the specified difficulty level",
)
async def get_dare_by_difficulty(
    difficulty: str = Path(
        ..., description="The difficulty level to filter by", example="medium", regex="^[a-zA-Z]+$"
    )
) -> DareResponse:
    """
    Get a random dare challenge from a specific difficulty level.

    Available difficulty levels:
    - easy: Simple and safe challenges that anyone can do
    - medium: Moderately challenging dares that require some effort
    - hard: Challenging dares that require courage or significant effort

    Args:
        difficulty: The difficulty level to filter by (case-insensitive)

    Returns:
        DareResponse: Random dare challenge from the difficulty level

    Raises:
        HTTPException: If difficulty is not found (404) or server error (500)
    """
    try:
        dare_service = get_dare_service()
        dare_data = dare_service.get_dare_by_difficulty(difficulty)

        return DareResponse(
            id=dare_data["id"], content=dare_data["content"], difficulty=dare_data["difficulty"]
        )
    except TruthDareAPIException as e:
        logger.error(f"API error getting dare by difficulty '{difficulty}': {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting dare by difficulty '{difficulty}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/difficulties/list",
    response_model=list[str],
    summary="Get Available Difficulties",
    description="Get a list of all available dare difficulty levels.",
    response_description="List of available dare difficulty levels",
)
async def get_available_difficulties() -> list[str]:
    """
    Get list of all available dare difficulty levels.

    Returns a list of all difficulty levels that have dare challenges available,
    ordered from easiest to hardest.

    Returns:
        List[str]: List of available difficulty level names

    Raises:
        HTTPException: If server error occurs (500)
    """
    try:
        dare_service = get_dare_service()
        difficulties = dare_service.get_available_difficulties()

        return difficulties
    except Exception as e:
        logger.error(f"Unexpected error getting available difficulties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
