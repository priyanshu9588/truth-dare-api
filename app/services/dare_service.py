"""
Dare service module for Truth and Dare API.

This module handles all business logic related to dare challenges,
including random selection and difficulty filtering.
"""

import logging
from typing import Any

from app.core.exceptions import DifficultyNotFoundError, ValidationError
from app.utils.data_loader import get_data_cache

logger = logging.getLogger(__name__)


class DareService:
    """Service class for managing dare challenges."""

    def __init__(self):
        """Initialize the dare service."""
        self.data_cache = get_data_cache()

    def get_random_dare(self) -> dict[str, Any]:
        """
        Get a random dare challenge from all available dares.

        Returns:
            Dict[str, Any]: Random dare challenge with id, content, and difficulty

        Raises:
            NoDataAvailableError: If no dares are available
        """
        try:
            dare = self.data_cache.get_random_dare()
            logger.debug(f"Retrieved random dare: {dare.get('id')}")
            return dare
        except Exception as e:
            logger.error(f"Error getting random dare: {e}")
            raise

    def get_dare_by_difficulty(self, difficulty: str) -> dict[str, Any]:
        """
        Get a random dare challenge from a specific difficulty level.

        Args:
            difficulty: The difficulty level to filter by (e.g., 'easy', 'medium', 'hard')

        Returns:
            Dict[str, Any]: Random dare challenge from the specified difficulty level

        Raises:
            ValidationError: If difficulty is invalid
            DifficultyNotFoundError: If difficulty doesn't exist
            NoDataAvailableError: If no dares in difficulty level
        """
        # Validate input
        if not difficulty:
            raise ValidationError("difficulty", difficulty, "Difficulty cannot be empty")

        if not isinstance(difficulty, str):
            raise ValidationError("difficulty", difficulty, "Difficulty must be a string")

        # Normalize difficulty (lowercase, strip whitespace)
        normalized_difficulty = difficulty.lower().strip()

        try:
            dare = self.data_cache.get_dare_by_difficulty(normalized_difficulty)
            logger.debug(
                f"Retrieved dare from difficulty '{normalized_difficulty}': {dare.get('id')}"
            )
            return dare
        except DifficultyNotFoundError:
            # Re-raise with original difficulty name for better user experience
            available_difficulties = self.get_available_difficulties()
            raise DifficultyNotFoundError(difficulty, available_difficulties)
        except Exception as e:
            logger.error(f"Error getting dare by difficulty '{difficulty}': {e}")
            raise

    def get_available_difficulties(self) -> list[str]:
        """
        Get list of all available dare difficulty levels.

        Returns:
            List[str]: List of available difficulty level names
        """
        try:
            difficulties = self.data_cache.get_available_difficulties()
            logger.debug(f"Retrieved {len(difficulties)} available difficulties")
            # Return in order: easy, medium, hard
            ordered_difficulties = []
            for level in ["easy", "medium", "hard"]:
                if level in difficulties:
                    ordered_difficulties.append(level)
            # Add any other difficulties not in the standard order
            for level in difficulties:
                if level not in ordered_difficulties:
                    ordered_difficulties.append(level)
            return ordered_difficulties
        except Exception as e:
            logger.error(f"Error getting available difficulties: {e}")
            raise

    def validate_difficulty(self, difficulty: str) -> bool:
        """
        Validate if a difficulty level exists.

        Args:
            difficulty: The difficulty level to validate

        Returns:
            bool: True if difficulty exists, False otherwise
        """
        if not difficulty or not isinstance(difficulty, str):
            return False

        normalized_difficulty = difficulty.lower().strip()
        available_difficulties = self.get_available_difficulties()
        return normalized_difficulty in available_difficulties

    def get_difficulty_stats(self) -> dict[str, int]:
        """
        Get statistics about dare difficulty levels.

        Returns:
            Dict[str, int]: Dictionary mapping difficulties to their dare counts
        """
        try:
            stats = self.data_cache.get_stats()
            return stats.get("difficulties", {})
        except Exception as e:
            logger.error(f"Error getting difficulty stats: {e}")
            raise


# Global service instance
_dare_service: DareService = None


def get_dare_service() -> DareService:
    """
    Get the global dare service instance.

    Returns:
        DareService: Global service instance
    """
    global _dare_service
    if _dare_service is None:
        _dare_service = DareService()
    return _dare_service
