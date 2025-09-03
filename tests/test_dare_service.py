"""
Unit tests for Dare service.

Tests the dare service business logic including random selection,
difficulty filtering, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from app.services.dare_service import DareService, get_dare_service
from app.core.exceptions import DifficultyNotFoundError, NoDataAvailableError, ValidationError


class TestDareService:
    """Test suite for DareService class."""
    
    @pytest.fixture
    def dare_service(self):
        """Create a DareService instance for testing."""
        return DareService()
    
    @pytest.fixture
    def mock_data_cache(self):
        """Create a mock data cache with test data."""
        mock_cache = Mock()
        mock_cache.get_random_dare.return_value = {
            "id": 1,
            "content": "Do 10 jumping jacks",
            "difficulty": "easy"
        }
        mock_cache.get_dare_by_difficulty.return_value = {
            "id": 2,
            "content": "Call a random number and sing",
            "difficulty": "hard"
        }
        mock_cache.get_available_difficulties.return_value = ["easy", "medium", "hard"]
        mock_cache.get_stats.return_value = {
            "difficulties": {
                "easy": 20,
                "medium": 22,
                "hard": 13
            }
        }
        return mock_cache
    
    def test_get_random_dare_success(self, dare_service, mock_data_cache):
        """Test successful random dare retrieval."""
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.get_random_dare()
        
        assert result["id"] == 1
        assert result["content"] == "Do 10 jumping jacks"
        assert result["difficulty"] == "easy"
        mock_data_cache.get_random_dare.assert_called_once()
    
    def test_get_random_dare_no_data(self, dare_service, mock_data_cache):
        """Test random dare retrieval when no data is available."""
        mock_data_cache.get_random_dare.side_effect = NoDataAvailableError("dares", "any")
        
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            with pytest.raises(NoDataAvailableError):
                dare_service.get_random_dare()
    
    def test_get_dare_by_difficulty_success(self, dare_service, mock_data_cache):
        """Test successful dare retrieval by difficulty."""
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.get_dare_by_difficulty("hard")
        
        assert result["id"] == 2
        assert result["content"] == "Call a random number and sing"
        assert result["difficulty"] == "hard"
        mock_data_cache.get_dare_by_difficulty.assert_called_once_with("hard")
    
    def test_get_dare_by_difficulty_normalized(self, dare_service, mock_data_cache):
        """Test that difficulty names are normalized (lowercase, stripped)."""
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            dare_service.get_dare_by_difficulty("  MEDIUM  ")
        
        mock_data_cache.get_dare_by_difficulty.assert_called_once_with("medium")
    
    def test_get_dare_by_difficulty_empty(self, dare_service):
        """Test dare retrieval with empty difficulty."""
        with pytest.raises(ValidationError) as exc_info:
            dare_service.get_dare_by_difficulty("")
        
        assert "Difficulty cannot be empty" in str(exc_info.value)
        assert exc_info.value.status_code == 422
    
    def test_get_dare_by_difficulty_invalid_type(self, dare_service):
        """Test dare retrieval with non-string difficulty."""
        with pytest.raises(ValidationError) as exc_info:
            dare_service.get_dare_by_difficulty(123)
        
        assert "Difficulty must be a string" in str(exc_info.value)
        assert exc_info.value.status_code == 422
    
    def test_get_dare_by_difficulty_not_found(self, dare_service, mock_data_cache):
        """Test dare retrieval with non-existent difficulty."""
        mock_data_cache.get_dare_by_difficulty.side_effect = DifficultyNotFoundError("impossible", ["easy", "medium", "hard"])
        mock_data_cache.get_available_difficulties.return_value = ["easy", "medium", "hard"]
        
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            with pytest.raises(DifficultyNotFoundError) as exc_info:
                dare_service.get_dare_by_difficulty("impossible")
        
        assert "impossible" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_available_difficulties(self, dare_service, mock_data_cache):
        """Test getting available difficulties."""
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.get_available_difficulties()
        
        # Should be ordered: easy, medium, hard
        expected = ["easy", "medium", "hard"]
        assert result == expected
        mock_data_cache.get_available_difficulties.assert_called_once()
    
    def test_get_available_difficulties_custom_order(self, dare_service, mock_data_cache):
        """Test getting available difficulties with custom ordering."""
        mock_data_cache.get_available_difficulties.return_value = ["hard", "easy", "custom", "medium"]
        
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.get_available_difficulties()
        
        # Should order standard difficulties first, then others
        assert result[:3] == ["easy", "medium", "hard"]
        assert "custom" in result
    
    def test_validate_difficulty_valid(self, dare_service, mock_data_cache):
        """Test difficulty validation with valid difficulty."""
        mock_data_cache.get_available_difficulties.return_value = ["easy", "medium", "hard"]
        
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.validate_difficulty("medium")
        
        assert result is True
    
    def test_validate_difficulty_invalid(self, dare_service, mock_data_cache):
        """Test difficulty validation with invalid difficulty."""
        mock_data_cache.get_available_difficulties.return_value = ["easy", "medium", "hard"]
        
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.validate_difficulty("impossible")
        
        assert result is False
    
    def test_validate_difficulty_empty(self, dare_service):
        """Test difficulty validation with empty string."""
        result = dare_service.validate_difficulty("")
        assert result is False
    
    def test_validate_difficulty_none(self, dare_service):
        """Test difficulty validation with None."""
        result = dare_service.validate_difficulty(None)
        assert result is False
    
    def test_validate_difficulty_non_string(self, dare_service):
        """Test difficulty validation with non-string type."""
        result = dare_service.validate_difficulty(123)
        assert result is False
    
    def test_get_difficulty_stats(self, dare_service, mock_data_cache):
        """Test getting difficulty statistics."""
        with patch.object(dare_service, 'data_cache', mock_data_cache):
            result = dare_service.get_difficulty_stats()
        
        expected = {
            "easy": 20,
            "medium": 22,
            "hard": 13
        }
        assert result == expected
        mock_data_cache.get_stats.assert_called_once()


class TestDareServiceSingleton:
    """Test the dare service singleton."""
    
    def test_get_dare_service_singleton(self):
        """Test that get_dare_service returns the same instance."""
        service1 = get_dare_service()
        service2 = get_dare_service()
        
        assert service1 is service2
        assert isinstance(service1, DareService)