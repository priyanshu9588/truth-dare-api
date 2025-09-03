"""
Pydantic response models for Truth and Dare API.

This module defines all response models used by the API endpoints
with proper validation and documentation.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class TruthCategory(str, Enum):
    """Enumeration of available truth categories."""

    GENERAL = "general"
    RELATIONSHIPS = "relationships"
    FUNNY = "funny"
    DEEP = "deep"
    EMBARRASSING = "embarrassing"


class DareDifficulty(str, Enum):
    """Enumeration of available dare difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GameType(str, Enum):
    """Enumeration of game types."""

    TRUTH = "truth"
    DARE = "dare"


class BaseResponse(BaseModel):
    """Base response model with common fields."""

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {"example": {"success": True, "timestamp": "2025-09-03T12:00:00Z"}}


class TruthResponse(BaseResponse):
    """
    Response model for truth questions.

    Attributes:
        id: Unique identifier for the truth question
        type: Always 'truth' for truth responses
        content: The truth question text
        category: The category of the truth question
    """

    id: int = Field(..., description="Unique identifier for the truth question", example=1)
    type: GameType = Field(GameType.TRUTH, description="Type of game item", example="truth")
    content: str = Field(
        ..., description="The truth question text", example="What is your biggest fear?"
    )
    category: TruthCategory = Field(
        ..., description="Category of the truth question", example="deep"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "truth",
                "content": "What is the most embarrassing thing you've ever done in public?",
                "category": "embarrassing",
            }
        }


class DareResponse(BaseResponse):
    """
    Response model for dare challenges.

    Attributes:
        id: Unique identifier for the dare challenge
        type: Always 'dare' for dare responses
        content: The dare challenge text
        difficulty: The difficulty level of the dare
    """

    id: int = Field(..., description="Unique identifier for the dare challenge", example=1)
    type: GameType = Field(GameType.DARE, description="Type of game item", example="dare")
    content: str = Field(..., description="The dare challenge text", example="Do 10 jumping jacks")
    difficulty: DareDifficulty = Field(
        ..., description="Difficulty level of the dare", example="easy"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "dare",
                "content": "Do 10 jumping jacks",
                "difficulty": "easy",
            }
        }


class GameResponse(BaseResponse):
    """
    Response model for random game items (truth or dare).

    This model can represent either a truth or dare, depending on the random selection.

    Attributes:
        id: Unique identifier for the game item
        type: Type of game item ('truth' or 'dare')
        content: The question or challenge text
        category: Category (only present for truths)
        difficulty: Difficulty level (only present for dares)
    """

    id: int = Field(..., description="Unique identifier for the game item", example=1)
    type: GameType = Field(..., description="Type of game item (truth or dare)", example="truth")
    content: str = Field(
        ..., description="The question or challenge text", example="What is your biggest fear?"
    )
    category: TruthCategory | None = Field(
        None, description="Category (only for truths)", example="deep"
    )
    difficulty: DareDifficulty | None = Field(
        None, description="Difficulty level (only for dares)", example="easy"
    )

    @validator("category")
    def category_only_for_truth(cls, v, values):
        """Ensure category is only present for truth items."""
        if "type" in values and values["type"] == GameType.TRUTH and v is None:
            raise ValueError("category is required for truth items")
        if "type" in values and values["type"] == GameType.DARE and v is not None:
            raise ValueError("category should not be present for dare items")
        return v

    @validator("difficulty")
    def difficulty_only_for_dare(cls, v, values):
        """Ensure difficulty is only present for dare items."""
        if "type" in values and values["type"] == GameType.DARE and v is None:
            raise ValueError("difficulty is required for dare items")
        if "type" in values and values["type"] == GameType.TRUTH and v is not None:
            raise ValueError("difficulty should not be present for truth items")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "truth",
                "content": "What is the most embarrassing thing you've ever done in public?",
                "category": "embarrassing",
                "difficulty": None,
            }
        }


class HealthResponse(BaseResponse):
    """
    Response model for health check endpoint.

    Attributes:
        status: Health status (healthy, degraded, unhealthy)
        timestamp: Timestamp of the health check
        data: Basic statistics about available data
        categories: Truth categories and their counts
        difficulties: Dare difficulties and their counts
    """

    status: str = Field(..., description="Health status", example="healthy")
    timestamp: str = Field(
        ..., description="Timestamp of health check", example="2025-09-03T12:00:00Z"
    )
    data: dict[str, int] = Field(..., description="Basic data statistics")
    categories: dict[str, int] = Field(..., description="Truth categories and counts")
    difficulties: dict[str, int] = Field(..., description="Dare difficulties and counts")
    error: str | None = Field(None, description="Error message if unhealthy")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-09-03T12:00:00Z",
                "data": {
                    "total_truths": 55,
                    "total_dares": 55,
                    "truth_categories": 5,
                    "dare_difficulties": 3,
                },
                "categories": {
                    "general": 11,
                    "relationships": 11,
                    "funny": 11,
                    "deep": 11,
                    "embarrassing": 11,
                },
                "difficulties": {"easy": 18, "medium": 18, "hard": 19},
            }
        }


class ErrorResponse(BaseResponse):
    """
    Response model for API errors.

    Attributes:
        error: Error type or code
        message: Human-readable error message
        details: Additional error details
        status_code: HTTP status code
    """

    error: str = Field(..., description="Error type or code", example="CategoryNotFoundError")
    message: str = Field(
        ..., description="Human-readable error message", example="Category 'invalid' not found"
    )
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code", example=404)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "CategoryNotFoundError",
                "message": "Category 'invalid' not found. Available categories: general, relationships, funny, deep, embarrassing",
                "details": {
                    "requested_category": "invalid",
                    "available_categories": [
                        "general",
                        "relationships",
                        "funny",
                        "deep",
                        "embarrassing",
                    ],
                },
                "status_code": 404,
            }
        }


class StatsResponse(BaseResponse):
    """
    Response model for statistics endpoint.

    Attributes:
        truths: Truth statistics
        dares: Dare statistics
        total_items: Total number of items
    """

    truths: dict[str, Any] = Field(..., description="Truth statistics")
    dares: dict[str, Any] = Field(..., description="Dare statistics")
    total_items: int = Field(..., description="Total number of items", example=110)

    class Config:
        json_schema_extra = {
            "example": {
                "truths": {
                    "total": 55,
                    "categories": {
                        "general": 11,
                        "relationships": 11,
                        "funny": 11,
                        "deep": 11,
                        "embarrassing": 11,
                    },
                    "available_categories": [
                        "general",
                        "relationships",
                        "funny",
                        "deep",
                        "embarrassing",
                    ],
                },
                "dares": {
                    "total": 55,
                    "difficulties": {"easy": 18, "medium": 18, "hard": 19},
                    "available_difficulties": ["easy", "medium", "hard"],
                },
                "total_items": 110,
            }
        }
