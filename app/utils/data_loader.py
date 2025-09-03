"""
Data loading and caching utilities for Truth and Dare API.

This module handles loading JSON data files and provides caching
functionality for efficient data access.
"""

import json
import logging
import random
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import (
    CategoryNotFoundError,
    DataLoadError,
    DifficultyNotFoundError,
    NoDataAvailableError,
)

logger = logging.getLogger(__name__)


class DataCache:
    """
    Data cache manager for Truth and Dare content.

    Handles loading, caching, and filtering of truth and dare data
    with automatic cache invalidation.
    """

    def __init__(self):
        """Initialize the data cache."""
        self._truths: list[dict[str, Any]] = []
        self._dares: list[dict[str, Any]] = []
        self._truths_by_category: dict[str, list[dict[str, Any]]] = {}
        self._dares_by_difficulty: dict[str, list[dict[str, Any]]] = {}
        self._loaded = False
        self.settings = get_settings()

    def load_data(self) -> None:
        """
        Load truth and dare data from JSON files.

        Raises:
            DataLoadError: If files cannot be loaded or parsed
        """
        try:
            # Load truths
            truths_path = Path(self.settings.truths_file_path)
            if not truths_path.exists():
                raise DataLoadError(str(truths_path), {"reason": "File does not exist"})

            with open(truths_path, encoding="utf-8") as f:
                self._truths = json.load(f)

            # Load dares
            dares_path = Path(self.settings.dares_file_path)
            if not dares_path.exists():
                raise DataLoadError(str(dares_path), {"reason": "File does not exist"})

            with open(dares_path, encoding="utf-8") as f:
                self._dares = json.load(f)

            # Build category and difficulty indexes
            self._build_indexes()
            self._loaded = True

            logger.info(f"Loaded {len(self._truths)} truths and {len(self._dares)} dares")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise DataLoadError("JSON file", {"reason": f"Invalid JSON format: {e}"})
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise DataLoadError(str(e), {"reason": "File not found"})
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            raise DataLoadError("Unknown", {"reason": f"Unexpected error: {e}"})

    def _build_indexes(self) -> None:
        """Build category and difficulty indexes for fast filtering."""
        # Build truths by category index
        self._truths_by_category = {}
        for truth in self._truths:
            category = truth.get("category", "general")
            if category not in self._truths_by_category:
                self._truths_by_category[category] = []
            self._truths_by_category[category].append(truth)

        # Build dares by difficulty index
        self._dares_by_difficulty = {}
        for dare in self._dares:
            difficulty = dare.get("difficulty", "medium")
            if difficulty not in self._dares_by_difficulty:
                self._dares_by_difficulty[difficulty] = []
            self._dares_by_difficulty[difficulty].append(dare)

    def ensure_loaded(self) -> None:
        """Ensure data is loaded, load if necessary."""
        if not self._loaded:
            self.load_data()

    def get_random_truth(self) -> dict[str, Any]:
        """
        Get a random truth question.

        Returns:
            Dict[str, Any]: Random truth object

        Raises:
            NoDataAvailableError: If no truths are available
        """
        self.ensure_loaded()
        if not self._truths:
            raise NoDataAvailableError("truths", "any")
        return random.choice(self._truths)

    def get_truth_by_category(self, category: str) -> dict[str, Any]:
        """
        Get a random truth question from a specific category.

        Args:
            category: The category to filter by

        Returns:
            Dict[str, Any]: Random truth object from the category

        Raises:
            CategoryNotFoundError: If category doesn't exist
            NoDataAvailableError: If no truths in category
        """
        self.ensure_loaded()

        available_categories = list(self._truths_by_category.keys())
        if category not in available_categories:
            raise CategoryNotFoundError(category, available_categories)

        category_truths = self._truths_by_category[category]
        if not category_truths:
            raise NoDataAvailableError("category", category)

        return random.choice(category_truths)

    def get_random_dare(self) -> dict[str, Any]:
        """
        Get a random dare challenge.

        Returns:
            Dict[str, Any]: Random dare object

        Raises:
            NoDataAvailableError: If no dares are available
        """
        self.ensure_loaded()
        if not self._dares:
            raise NoDataAvailableError("dares", "any")
        return random.choice(self._dares)

    def get_dare_by_difficulty(self, difficulty: str) -> dict[str, Any]:
        """
        Get a random dare challenge from a specific difficulty level.

        Args:
            difficulty: The difficulty level to filter by

        Returns:
            Dict[str, Any]: Random dare object from the difficulty level

        Raises:
            DifficultyNotFoundError: If difficulty doesn't exist
            NoDataAvailableError: If no dares in difficulty level
        """
        self.ensure_loaded()

        available_difficulties = list(self._dares_by_difficulty.keys())
        if difficulty not in available_difficulties:
            raise DifficultyNotFoundError(difficulty, available_difficulties)

        difficulty_dares = self._dares_by_difficulty[difficulty]
        if not difficulty_dares:
            raise NoDataAvailableError("difficulty", difficulty)

        return random.choice(difficulty_dares)

    def get_available_categories(self) -> list[str]:
        """
        Get list of available truth categories.

        Returns:
            List[str]: List of available categories
        """
        self.ensure_loaded()
        return list(self._truths_by_category.keys())

    def get_available_difficulties(self) -> list[str]:
        """
        Get list of available dare difficulty levels.

        Returns:
            List[str]: List of available difficulty levels
        """
        self.ensure_loaded()
        return list(self._dares_by_difficulty.keys())

    def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about loaded data.

        Returns:
            Dict[str, Any]: Statistics about truths and dares
        """
        self.ensure_loaded()
        return {
            "total_truths": len(self._truths),
            "total_dares": len(self._dares),
            "categories": {
                category: len(truths) for category, truths in self._truths_by_category.items()
            },
            "difficulties": {
                difficulty: len(dares) for difficulty, dares in self._dares_by_difficulty.items()
            },
        }


# Global cache instance
_data_cache: DataCache | None = None


def get_data_cache() -> DataCache:
    """
    Get the global data cache instance.

    Returns:
        DataCache: Global cache instance
    """
    global _data_cache
    if _data_cache is None:
        _data_cache = DataCache()
    return _data_cache


@lru_cache(maxsize=1)
def get_cached_stats() -> dict[str, Any]:
    """
    Get cached statistics (with LRU cache for performance).

    Returns:
        Dict[str, Any]: Cached statistics
    """
    cache = get_data_cache()
    return cache.get_stats()
