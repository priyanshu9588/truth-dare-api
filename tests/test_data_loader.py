"""
Unit tests for Data Loader.

Tests the data loading, caching, and filtering functionality.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from app.utils.data_loader import DataCache, get_data_cache, get_cached_stats
from app.core.exceptions import DataLoadError, CategoryNotFoundError, DifficultyNotFoundError, NoDataAvailableError


class TestDataCache:
    """Test suite for DataCache class."""
    
    @pytest.fixture
    def sample_truths_data(self):
        """Sample truths data for testing."""
        return [
            {"id": 1, "content": "Truth question 1", "category": "general"},
            {"id": 2, "content": "Truth question 2", "category": "funny"},
            {"id": 3, "content": "Truth question 3", "category": "general"},
        ]
    
    @pytest.fixture
    def sample_dares_data(self):
        """Sample dares data for testing."""
        return [
            {"id": 1, "content": "Dare challenge 1", "difficulty": "easy"},
            {"id": 2, "content": "Dare challenge 2", "difficulty": "hard"},
            {"id": 3, "content": "Dare challenge 3", "difficulty": "easy"},
        ]
    
    @pytest.fixture
    def data_cache(self):
        """Create a DataCache instance for testing."""
        return DataCache()
    
    def test_load_data_success(self, data_cache, sample_truths_data, sample_dares_data):
        """Test successful data loading."""
        truths_json = json.dumps(sample_truths_data)
        dares_json = json.dumps(sample_dares_data)
        
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("pathlib.Path.exists", return_value=True):
                mock_file.side_effect = [
                    mock_open(read_data=truths_json).return_value,
                    mock_open(read_data=dares_json).return_value,
                ]
                
                data_cache.load_data()
        
        assert data_cache._loaded is True
        assert len(data_cache._truths) == 3
        assert len(data_cache._dares) == 3
        assert "general" in data_cache._truths_by_category
        assert "funny" in data_cache._truths_by_category
        assert "easy" in data_cache._dares_by_difficulty
        assert "hard" in data_cache._dares_by_difficulty
    
    def test_load_data_file_not_found(self, data_cache):
        """Test data loading when files don't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(DataLoadError) as exc_info:
                data_cache.load_data()
        
        # Could be caught by specific handler or general handler
        assert "Failed to load data file" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    def test_load_data_invalid_json(self, data_cache):
        """Test data loading with invalid JSON."""
        invalid_json = "{ invalid json }"
        
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(DataLoadError) as exc_info:
                    data_cache.load_data()
        
        # Could be caught by specific JSON handler or general handler
        assert "Failed to load data file" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    def test_get_random_truth_success(self, data_cache, sample_truths_data):
        """Test getting random truth."""
        data_cache._truths = sample_truths_data
        data_cache._loaded = True
        
        result = data_cache.get_random_truth()
        
        assert result in sample_truths_data
        assert "id" in result
        assert "content" in result
        assert "category" in result
    
    def test_get_random_truth_no_data(self, data_cache):
        """Test getting random truth when no data is available."""
        data_cache._truths = []
        data_cache._loaded = True
        
        with pytest.raises(NoDataAvailableError) as exc_info:
            data_cache.get_random_truth()
        
        assert "truths" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_truth_by_category_success(self, data_cache, sample_truths_data):
        """Test getting truth by category."""
        data_cache._truths = sample_truths_data
        data_cache._truths_by_category = {
            "general": [sample_truths_data[0], sample_truths_data[2]],
            "funny": [sample_truths_data[1]]
        }
        data_cache._loaded = True
        
        result = data_cache.get_truth_by_category("general")
        
        assert result in [sample_truths_data[0], sample_truths_data[2]]
        assert result["category"] == "general"
    
    def test_get_truth_by_category_not_found(self, data_cache, sample_truths_data):
        """Test getting truth by non-existent category."""
        data_cache._truths = sample_truths_data
        data_cache._truths_by_category = {"general": [sample_truths_data[0]]}
        data_cache._loaded = True
        
        with pytest.raises(CategoryNotFoundError) as exc_info:
            data_cache.get_truth_by_category("nonexistent")
        
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_random_dare_success(self, data_cache, sample_dares_data):
        """Test getting random dare."""
        data_cache._dares = sample_dares_data
        data_cache._loaded = True
        
        result = data_cache.get_random_dare()
        
        assert result in sample_dares_data
        assert "id" in result
        assert "content" in result
        assert "difficulty" in result
    
    def test_get_random_dare_no_data(self, data_cache):
        """Test getting random dare when no data is available."""
        data_cache._dares = []
        data_cache._loaded = True
        
        with pytest.raises(NoDataAvailableError) as exc_info:
            data_cache.get_random_dare()
        
        assert "dares" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_dare_by_difficulty_success(self, data_cache, sample_dares_data):
        """Test getting dare by difficulty."""
        data_cache._dares = sample_dares_data
        data_cache._dares_by_difficulty = {
            "easy": [sample_dares_data[0], sample_dares_data[2]],
            "hard": [sample_dares_data[1]]
        }
        data_cache._loaded = True
        
        result = data_cache.get_dare_by_difficulty("easy")
        
        assert result in [sample_dares_data[0], sample_dares_data[2]]
        assert result["difficulty"] == "easy"
    
    def test_get_dare_by_difficulty_not_found(self, data_cache, sample_dares_data):
        """Test getting dare by non-existent difficulty."""
        data_cache._dares = sample_dares_data
        data_cache._dares_by_difficulty = {"easy": [sample_dares_data[0]]}
        data_cache._loaded = True
        
        with pytest.raises(DifficultyNotFoundError) as exc_info:
            data_cache.get_dare_by_difficulty("impossible")
        
        assert "impossible" in str(exc_info.value)
        assert exc_info.value.status_code == 404
    
    def test_get_available_categories(self, data_cache, sample_truths_data):
        """Test getting available categories."""
        data_cache._truths_by_category = {
            "general": [sample_truths_data[0]],
            "funny": [sample_truths_data[1]]
        }
        data_cache._loaded = True
        
        result = data_cache.get_available_categories()
        
        assert "general" in result
        assert "funny" in result
        assert len(result) == 2
    
    def test_get_available_difficulties(self, data_cache, sample_dares_data):
        """Test getting available difficulties."""
        data_cache._dares_by_difficulty = {
            "easy": [sample_dares_data[0]],
            "hard": [sample_dares_data[1]]
        }
        data_cache._loaded = True
        
        result = data_cache.get_available_difficulties()
        
        assert "easy" in result
        assert "hard" in result
        assert len(result) == 2
    
    def test_get_stats(self, data_cache, sample_truths_data, sample_dares_data):
        """Test getting statistics."""
        data_cache._truths = sample_truths_data
        data_cache._dares = sample_dares_data
        data_cache._truths_by_category = {
            "general": [sample_truths_data[0], sample_truths_data[2]],
            "funny": [sample_truths_data[1]]
        }
        data_cache._dares_by_difficulty = {
            "easy": [sample_dares_data[0], sample_dares_data[2]],
            "hard": [sample_dares_data[1]]
        }
        data_cache._loaded = True
        
        result = data_cache.get_stats()
        
        assert result["total_truths"] == 3
        assert result["total_dares"] == 3
        assert result["categories"]["general"] == 2
        assert result["categories"]["funny"] == 1
        assert result["difficulties"]["easy"] == 2
        assert result["difficulties"]["hard"] == 1
    
    def test_ensure_loaded_calls_load_data(self, data_cache):
        """Test that ensure_loaded calls load_data when not loaded."""
        with patch.object(data_cache, 'load_data') as mock_load_data:
            data_cache._loaded = False
            data_cache.ensure_loaded()
            mock_load_data.assert_called_once()
    
    def test_ensure_loaded_skips_when_loaded(self, data_cache):
        """Test that ensure_loaded skips load_data when already loaded."""
        with patch.object(data_cache, 'load_data') as mock_load_data:
            data_cache._loaded = True
            data_cache.ensure_loaded()
            mock_load_data.assert_not_called()


class TestDataCacheSingleton:
    """Test the data cache singleton."""
    
    def test_get_data_cache_singleton(self):
        """Test that get_data_cache returns the same instance."""
        cache1 = get_data_cache()
        cache2 = get_data_cache()
        
        assert cache1 is cache2
        assert isinstance(cache1, DataCache)
    
    def test_get_cached_stats_caching(self):
        """Test that get_cached_stats uses LRU cache."""
        with patch('app.utils.data_loader.get_data_cache') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get_stats.return_value = {"test": "data"}
            mock_get_cache.return_value = mock_cache
            
            # Call twice
            result1 = get_cached_stats()
            result2 = get_cached_stats()
            
            # Should return same result
            assert result1 == result2
            # But cache should only be called once due to LRU cache
            assert mock_get_cache.call_count == 1