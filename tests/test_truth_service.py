"""
Unit tests for Truth service.

Tests the truth service business logic including random selection,
category filtering, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from app.services.truth_service import TruthService, get_truth_service
from app.core.exceptions import CategoryNotFoundError, NoDataAvailableError, ValidationError


class TestTruthService:
    """Test suite for TruthService class."""
    
    @pytest.fixture
    def truth_service(self):
        """Create a TruthService instance for testing."""
        return TruthService()
    
    @pytest.fixture
    def mock_data_cache(self):
        """Create a mock data cache with test data."""
        mock_cache = Mock()
        mock_cache.get_random_truth.return_value = {
            "id": 1,
            "content": "What is your biggest fear?",
            "category": "deep"
        }
        mock_cache.get_truth_by_category.return_value = {
            "id": 2,
            "content": "What's the funniest thing that happened to you?",
            "category": "funny"
        }
        mock_cache.get_available_categories.return_value = ["general", "funny", "deep", "embarrassing", "relationships"]
        mock_cache.get_stats.return_value = {
            "categories": {
                "general": 10,
                "funny": 12,
                "deep": 8,
                "embarrassing": 15,
                "relationships": 10
            }
        }
        return mock_cache
    
    def test_get_random_truth_success(self, truth_service, mock_data_cache):
        """Test successful random truth retrieval."""
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.get_random_truth()
        
        assert result["id"] == 1
        assert result["content"] == "What is your biggest fear?"
        assert result["category"] == "deep"
        mock_data_cache.get_random_truth.assert_called_once()
    
    def test_get_random_truth_no_data(self, truth_service, mock_data_cache):
        """Test random truth retrieval when no data is available."""
        mock_data_cache.get_random_truth.side_effect = NoDataAvailableError("truths", "any")
        
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            with pytest.raises(NoDataAvailableError):
                truth_service.get_random_truth()
    
    def test_get_truth_by_category_success(self, truth_service, mock_data_cache):
        """Test successful truth retrieval by category."""
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.get_truth_by_category("funny")
        
        assert result["id"] == 2
        assert result["content"] == "What's the funniest thing that happened to you?"
        assert result["category"] == "funny"
        mock_data_cache.get_truth_by_category.assert_called_once_with("funny")
    
    def test_get_truth_by_category_normalized(self, truth_service, mock_data_cache):
        """Test that category names are normalized (lowercase, stripped)."""
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            truth_service.get_truth_by_category("  FUNNY  ")
        
        mock_data_cache.get_truth_by_category.assert_called_once_with("funny")
    
    def test_get_truth_by_category_empty(self, truth_service):
        """Test truth retrieval with empty category."""
        with pytest.raises(ValidationError) as exc_info:
            truth_service.get_truth_by_category("")
        
        assert "Category cannot be empty" in str(exc_info.value)
        assert exc_info.value.status_code == 422
    
    def test_get_truth_by_category_invalid_type(self, truth_service):
        """Test truth retrieval with non-string category."""
        with pytest.raises(ValidationError) as exc_info:
            truth_service.get_truth_by_category(123)
        
        assert "Category must be a string" in str(exc_info.value)
        assert exc_info.value.status_code == 422
    
    def test_get_truth_by_category_not_found(self, truth_service, mock_data_cache):
        """Test truth retrieval with non-existent category."""
        mock_data_cache.get_truth_by_category.side_effect = CategoryNotFoundError("invalid", ["general", "funny"])
        mock_data_cache.get_available_categories.return_value = ["general", "funny"]
        
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            with pytest.raises(CategoryNotFoundError) as exc_info:
                truth_service.get_truth_by_category("invalid")
        
        assert "invalid" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_available_categories(self, truth_service, mock_data_cache):
        """Test getting available categories."""
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.get_available_categories()
        
        expected = ["general", "funny", "deep", "embarrassing", "relationships"]
        assert result == sorted(expected)  # Should be sorted
        mock_data_cache.get_available_categories.assert_called_once()
    
    def test_validate_category_valid(self, truth_service, mock_data_cache):
        """Test category validation with valid category."""
        mock_data_cache.get_available_categories.return_value = ["general", "funny", "deep"]
        
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.validate_category("funny")
        
        assert result is True
    
    def test_validate_category_invalid(self, truth_service, mock_data_cache):
        """Test category validation with invalid category."""
        mock_data_cache.get_available_categories.return_value = ["general", "funny", "deep"]
        
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.validate_category("invalid")
        
        assert result is False
    
    def test_validate_category_empty(self, truth_service):
        """Test category validation with empty string."""
        result = truth_service.validate_category("")
        assert result is False
    
    def test_validate_category_none(self, truth_service):
        """Test category validation with None."""
        result = truth_service.validate_category(None)
        assert result is False
    
    def test_validate_category_non_string(self, truth_service):
        """Test category validation with non-string type."""
        result = truth_service.validate_category(123)
        assert result is False
    
    def test_get_category_stats(self, truth_service, mock_data_cache):
        """Test getting category statistics."""
        with patch.object(truth_service, 'data_cache', mock_data_cache):
            result = truth_service.get_category_stats()
        
        expected = {
            "general": 10,
            "funny": 12,
            "deep": 8,
            "embarrassing": 15,
            "relationships": 10
        }
        assert result == expected
        mock_data_cache.get_stats.assert_called_once()


class TestTruthServiceSingleton:
    """Test the truth service singleton."""
    
    def test_get_truth_service_singleton(self):
        """Test that get_truth_service returns the same instance."""
        service1 = get_truth_service()
        service2 = get_truth_service()
        
        assert service1 is service2
        assert isinstance(service1, TruthService)