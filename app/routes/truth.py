"""
Truth-related API routes for Truth and Dare API.

This module defines all endpoints related to truth questions.
"""

import logging

from fastapi import APIRouter, HTTPException, Path

from app.core.exceptions import TruthDareAPIException
from app.models.responses import ErrorResponse, TruthResponse
from app.services.truth_service import get_truth_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/truth",
    tags=["truths"],
    responses={
        404: {"model": ErrorResponse, "description": "Category not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)


@router.get(
    "",
    response_model=TruthResponse,
    summary="Get Random Truth",
    description="Get a random truth question from all available categories.",
    response_description="A random truth question with its category",
)
async def get_random_truth() -> TruthResponse:
    """
    Get a random truth question.

    Returns a randomly selected truth question from all available categories.
    Each truth includes an ID, content, and category.

    Returns:
        TruthResponse: Random truth question

    Raises:
        HTTPException: If no truths are available (500)
    """
    try:
        truth_service = get_truth_service()
        truth_data = truth_service.get_random_truth()

        return TruthResponse(
            id=truth_data["id"], content=truth_data["content"], category=truth_data["category"]
        )
    except TruthDareAPIException as e:
        logger.error(f"API error getting random truth: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting random truth: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/{category}",
    response_model=TruthResponse,
    summary="Get Truth by Category",
    description="Get a random truth question from a specific category.",
    response_description="A random truth question from the specified category",
)
async def get_truth_by_category(
    category: str = Path(
        ..., description="The category to filter by", example="funny", regex="^[a-zA-Z]+$"
    )
) -> TruthResponse:
    """
    Get a random truth question from a specific category.

    Available categories:
    - general: General truth questions
    - relationships: Questions about relationships and dating
    - funny: Humorous and light-hearted questions
    - deep: Thought-provoking and serious questions
    - embarrassing: Potentially embarrassing questions

    Args:
        category: The category to filter by (case-insensitive)

    Returns:
        TruthResponse: Random truth question from the category

    Raises:
        HTTPException: If category is not found (404) or server error (500)
    """
    try:
        truth_service = get_truth_service()
        truth_data = truth_service.get_truth_by_category(category)

        return TruthResponse(
            id=truth_data["id"], content=truth_data["content"], category=truth_data["category"]
        )
    except TruthDareAPIException as e:
        logger.error(f"API error getting truth by category '{category}': {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting truth by category '{category}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/categories/list",
    response_model=list[str],
    summary="Get Available Categories",
    description="Get a list of all available truth categories.",
    response_description="List of available truth categories",
)
async def get_available_categories() -> list[str]:
    """
    Get list of all available truth categories.

    Returns a sorted list of all categories that have truth questions available.

    Returns:
        List[str]: List of available category names

    Raises:
        HTTPException: If server error occurs (500)
    """
    try:
        truth_service = get_truth_service()
        categories = truth_service.get_available_categories()

        return categories
    except Exception as e:
        logger.error(f"Unexpected error getting available categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
