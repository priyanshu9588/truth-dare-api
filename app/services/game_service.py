"""
Game service module for Truth and Dare API.

This module handles game-level logic, including random selection
between truths and dares, and health check functionality.
"""

import logging
import random
from datetime import datetime
from typing import Any

from app.services.dare_service import get_dare_service
from app.services.truth_service import get_truth_service

logger = logging.getLogger(__name__)


class GameService:
    """Service class for managing game logic and health checks."""

    def __init__(self):
        """Initialize the game service."""
        self.truth_service = get_truth_service()
        self.dare_service = get_dare_service()

    def get_random_choice(self) -> dict[str, Any]:
        """
        Get a random choice between a truth question and a dare challenge.

        Uses 50/50 probability to select between truth and dare.

        Returns:
            Dict[str, Any]: Random truth or dare with type indicator

        Raises:
            NoDataAvailableError: If no data is available
        """
        try:
            # 50/50 random choice between truth and dare
            is_truth = random.choice([True, False])

            if is_truth:
                result = self.truth_service.get_random_truth()
                result["type"] = "truth"
                logger.debug(f"Game service returned random truth: {result.get('id')}")
            else:
                result = self.dare_service.get_random_dare()
                result["type"] = "dare"
                logger.debug(f"Game service returned random dare: {result.get('id')}")

            return result
        except Exception as e:
            logger.error(f"Error getting random choice: {e}")
            raise

    def get_health_status(self) -> dict[str, Any]:
        """
        Get health status of the API and its components.

        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Get data statistics
            truth_stats = self.truth_service.get_category_stats()
            dare_stats = self.dare_service.get_difficulty_stats()

            # Calculate totals
            total_truths = sum(truth_stats.values())
            total_dares = sum(dare_stats.values())

            # Determine health status
            status = "healthy"
            if total_truths == 0 or total_dares == 0:
                status = "degraded"  # Some data missing but API still functional
            if total_truths == 0 and total_dares == 0:
                status = "unhealthy"  # No data available

            health_info = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "total_truths": total_truths,
                    "total_dares": total_dares,
                    "truth_categories": len(truth_stats),
                    "dare_difficulties": len(dare_stats),
                },
                "categories": truth_stats,
                "difficulties": dare_stats,
            }

            logger.debug(f"Health check completed with status: {status}")
            return health_info

        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "data": {
                    "total_truths": 0,
                    "total_dares": 0,
                    "truth_categories": 0,
                    "dare_difficulties": 0,
                },
            }

    def get_game_stats(self) -> dict[str, Any]:
        """
        Get comprehensive game statistics.

        Returns:
            Dict[str, Any]: Game statistics including all categories and difficulties
        """
        try:
            truth_stats = self.truth_service.get_category_stats()
            dare_stats = self.dare_service.get_difficulty_stats()

            return {
                "truths": {
                    "total": sum(truth_stats.values()),
                    "categories": truth_stats,
                    "available_categories": self.truth_service.get_available_categories(),
                },
                "dares": {
                    "total": sum(dare_stats.values()),
                    "difficulties": dare_stats,
                    "available_difficulties": self.dare_service.get_available_difficulties(),
                },
                "total_items": sum(truth_stats.values()) + sum(dare_stats.values()),
            }
        except Exception as e:
            logger.error(f"Error getting game stats: {e}")
            raise


# Global service instance
_game_service: GameService = None


def get_game_service() -> GameService:
    """
    Get the global game service instance.

    Returns:
        GameService: Global service instance
    """
    global _game_service
    if _game_service is None:
        _game_service = GameService()
    return _game_service
