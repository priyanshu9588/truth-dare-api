"""
Truth service module for Truth and Dare API.

This module handles all business logic related to truth questions,
including random selection and category filtering.
"""

import logging
from typing import Any

from app.core.exceptions import CategoryNotFoundError, ValidationError
from app.utils.data_loader import get_data_cache

logger = logging.getLogger(__name__)


class TruthService:
    """Service class for managing truth questions."""

    def __init__(self):
        """Initialize the truth service."""
        self.data_cache = get_data_cache()

    def get_random_truth(self) -> dict[str, Any]:
        """
        Get a random truth question from all available truths.

        Returns:
            Dict[str, Any]: Random truth question with id, content, and category

        Raises:
            NoDataAvailableError: If no truths are available
        """
        try:
            truth = self.data_cache.get_random_truth()
            logger.debug(f"Retrieved random truth: {truth.get('id')}")
            return truth
        except Exception as e:
            logger.error(f"Error getting random truth: {e}")
            raise

    def get_truth_by_category(self, category: str) -> dict[str, Any]:
        """
        Get a random truth question from a specific category.

        Args:
            category: The category to filter by (e.g., 'funny', 'deep', 'embarrassing')

        Returns:
            Dict[str, Any]: Random truth question from the specified category

        Raises:
            ValidationError: If category is invalid
            CategoryNotFoundError: If category doesn't exist
            NoDataAvailableError: If no truths in category
        """
        # Validate input
        if not category:
            raise ValidationError("category", category, "Category cannot be empty")

        if not isinstance(category, str):
            raise ValidationError("category", category, "Category must be a string")

        # Normalize category (lowercase, strip whitespace)
        normalized_category = category.lower().strip()

        try:
            truth = self.data_cache.get_truth_by_category(normalized_category)
            logger.debug(
                f"Retrieved truth from category '{normalized_category}': {truth.get('id')}"
            )
            return truth
        except CategoryNotFoundError:
            # Re-raise with original category name for better user experience
            available_categories = self.get_available_categories()
            raise CategoryNotFoundError(category, available_categories)
        except Exception as e:
            logger.error(f"Error getting truth by category '{category}': {e}")
            raise

    def get_available_categories(self) -> list[str]:
        """
        Get list of all available truth categories.

        Returns:
            List[str]: List of available category names
        """
        try:
            categories = self.data_cache.get_available_categories()
            logger.debug(f"Retrieved {len(categories)} available categories")
            return sorted(categories)  # Return sorted for consistent API responses
        except Exception as e:
            logger.error(f"Error getting available categories: {e}")
            raise

    def validate_category(self, category: str) -> bool:
        """
        Validate if a category exists.

        Args:
            category: The category to validate

        Returns:
            bool: True if category exists, False otherwise
        """
        if not category or not isinstance(category, str):
            return False

        normalized_category = category.lower().strip()
        available_categories = self.get_available_categories()
        return normalized_category in available_categories

    def get_category_stats(self) -> dict[str, int]:
        """
        Get statistics about truth categories.

        Returns:
            Dict[str, int]: Dictionary mapping categories to their truth counts
        """
        try:
            stats = self.data_cache.get_stats()
            return stats.get("categories", {})
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            raise


# Global service instance
_truth_service: TruthService = None


def get_truth_service() -> TruthService:
    """
    Get the global truth service instance.

    Returns:
        TruthService: Global service instance
    """
    global _truth_service
    if _truth_service is None:
        _truth_service = TruthService()
    return _truth_service
