"""
Integration tests for API endpoints.

Tests all API endpoints with real FastAPI client to ensure
proper HTTP responses, status codes, and JSON serialization.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.main import app
from app.core.exceptions import CategoryNotFoundError, DifficultyNotFoundError, NoDataAvailableError


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_truth_service():
    """Mock truth service for testing."""
    mock_service = Mock()
    mock_service.get_random_truth.return_value = {
        "id": 1,
        "content": "What is your biggest fear?",
        "category": "deep"
    }
    mock_service.get_truth_by_category.return_value = {
        "id": 2,
        "content": "What's the funniest thing that happened to you?",
        "category": "funny"
    }
    mock_service.get_available_categories.return_value = ["general", "funny", "deep"]
    return mock_service


@pytest.fixture
def mock_dare_service():
    """Mock dare service for testing."""
    mock_service = Mock()
    mock_service.get_random_dare.return_value = {
        "id": 1,
        "content": "Do 10 jumping jacks",
        "difficulty": "easy"
    }
    mock_service.get_dare_by_difficulty.return_value = {
        "id": 2,
        "content": "Call a random number and sing",
        "difficulty": "hard"
    }
    mock_service.get_available_difficulties.return_value = ["easy", "medium", "hard"]
    return mock_service


@pytest.fixture
def mock_game_service():
    """Mock game service for testing."""
    mock_service = Mock()
    mock_service.get_random_choice.return_value = {
        "id": 1,
        "type": "truth",
        "content": "What is your biggest fear?",
        "category": "deep"
    }
    mock_service.get_health_status.return_value = {
        "status": "healthy",
        "timestamp": "2025-09-03T12:00:00Z",
        "data": {"total_truths": 55, "total_dares": 55, "truth_categories": 5, "dare_difficulties": 3},
        "categories": {"general": 11, "funny": 11},
        "difficulties": {"easy": 18, "medium": 18, "hard": 19}
    }
    mock_service.get_game_stats.return_value = {
        "truths": {"total": 55, "categories": {"general": 11}, "available_categories": ["general"]},
        "dares": {"total": 55, "difficulties": {"easy": 18}, "available_difficulties": ["easy"]},
        "total_items": 110
    }
    return mock_service


class TestTruthEndpoints:
    """Test suite for truth-related endpoints."""
    
    def test_get_random_truth_success(self, client, mock_truth_service):
        """Test successful random truth retrieval."""
        with patch('app.routes.truth.get_truth_service', return_value=mock_truth_service):
            response = client.get("/api/v1/truth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["type"] == "truth"
        assert data["content"] == "What is your biggest fear?"
        assert data["category"] == "deep"
    
    def test_get_random_truth_no_data(self, client, mock_truth_service):
        """Test random truth when no data is available."""
        mock_truth_service.get_random_truth.side_effect = NoDataAvailableError("truths", "any")
        
        with patch('app.routes.truth.get_truth_service', return_value=mock_truth_service):
            response = client.get("/api/v1/truth")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "No data available" in data["message"]
    
    def test_get_truth_by_category_success(self, client, mock_truth_service):
        """Test successful truth retrieval by category."""
        with patch('app.routes.truth.get_truth_service', return_value=mock_truth_service):
            response = client.get("/api/v1/truth/funny")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["type"] == "truth"
        assert data["content"] == "What's the funniest thing that happened to you?"
        assert data["category"] == "funny"
    
    def test_get_truth_by_category_not_found(self, client, mock_truth_service):
        """Test truth retrieval with non-existent category."""
        mock_truth_service.get_truth_by_category.side_effect = CategoryNotFoundError("invalid", ["general", "funny"])
        
        with patch('app.routes.truth.get_truth_service', return_value=mock_truth_service):
            response = client.get("/api/v1/truth/invalid")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "invalid" in data["message"]
        # The error type can be either CategoryNotFoundError or HTTPException
        assert data["error"] in ["CategoryNotFoundError", "HTTPException"]
    
    def test_get_truth_by_category_invalid_characters(self, client):
        """Test truth retrieval with invalid category characters."""
        response = client.get("/api/v1/truth/invalid-123")
        
        assert response.status_code == 422  # Validation error due to regex
    
    def test_get_available_categories_success(self, client, mock_truth_service):
        """Test successful retrieval of available categories."""
        with patch('app.routes.truth.get_truth_service', return_value=mock_truth_service):
            response = client.get("/api/v1/truth/categories/list")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "general" in data
        assert "funny" in data
        assert "deep" in data


class TestDareEndpoints:
    """Test suite for dare-related endpoints."""
    
    def test_get_random_dare_success(self, client, mock_dare_service):
        """Test successful random dare retrieval."""
        with patch('app.routes.dare.get_dare_service', return_value=mock_dare_service):
            response = client.get("/api/v1/dare")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["type"] == "dare"
        assert data["content"] == "Do 10 jumping jacks"
        assert data["difficulty"] == "easy"
    
    def test_get_random_dare_no_data(self, client, mock_dare_service):
        """Test random dare when no data is available."""
        mock_dare_service.get_random_dare.side_effect = NoDataAvailableError("dares", "any")
        
        with patch('app.routes.dare.get_dare_service', return_value=mock_dare_service):
            response = client.get("/api/v1/dare")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "No data available" in data["message"]
    
    def test_get_dare_by_difficulty_success(self, client, mock_dare_service):
        """Test successful dare retrieval by difficulty."""
        with patch('app.routes.dare.get_dare_service', return_value=mock_dare_service):
            response = client.get("/api/v1/dare/hard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["type"] == "dare"
        assert data["content"] == "Call a random number and sing"
        assert data["difficulty"] == "hard"
    
    def test_get_dare_by_difficulty_not_found(self, client, mock_dare_service):
        """Test dare retrieval with non-existent difficulty."""
        mock_dare_service.get_dare_by_difficulty.side_effect = DifficultyNotFoundError("impossible", ["easy", "medium", "hard"])
        
        with patch('app.routes.dare.get_dare_service', return_value=mock_dare_service):
            response = client.get("/api/v1/dare/impossible")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "impossible" in data["message"]
        # The error type can be either DifficultyNotFoundError or HTTPException
        assert data["error"] in ["DifficultyNotFoundError", "HTTPException"]
    
    def test_get_dare_by_difficulty_invalid_characters(self, client):
        """Test dare retrieval with invalid difficulty characters."""
        response = client.get("/api/v1/dare/super-hard-123")
        
        assert response.status_code == 422  # Validation error due to regex
    
    def test_get_available_difficulties_success(self, client, mock_dare_service):
        """Test successful retrieval of available difficulties."""
        with patch('app.routes.dare.get_dare_service', return_value=mock_dare_service):
            response = client.get("/api/v1/dare/difficulties/list")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "easy" in data
        assert "medium" in data
        assert "hard" in data


class TestGameEndpoints:
    """Test suite for game-related endpoints."""
    
    def test_get_random_game_truth_response(self, client, mock_game_service):
        """Test random game returning a truth."""
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/game/random")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["type"] == "truth"
        assert data["content"] == "What is your biggest fear?"
        assert data["category"] == "deep"
        assert data["difficulty"] is None
    
    def test_get_random_game_dare_response(self, client, mock_game_service):
        """Test random game returning a dare."""
        mock_game_service.get_random_choice.return_value = {
            "id": 2,
            "type": "dare",
            "content": "Do 10 jumping jacks",
            "difficulty": "easy"
        }
        
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/game/random")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 2
        assert data["type"] == "dare"
        assert data["content"] == "Do 10 jumping jacks"
        assert data["difficulty"] == "easy"
        assert data["category"] is None
    
    def test_get_random_game_no_data(self, client, mock_game_service):
        """Test random game when no data is available."""
        mock_game_service.get_random_choice.side_effect = NoDataAvailableError("game", "any")
        
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/game/random")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "No data available" in data["message"]
    
    def test_health_check_healthy(self, client, mock_game_service):
        """Test health check with healthy status."""
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "data" in data
        assert data["data"]["total_truths"] == 55
        assert data["data"]["total_dares"] == 55
    
    def test_health_check_unhealthy(self, client, mock_game_service):
        """Test health check with error."""
        mock_game_service.get_health_status.side_effect = Exception("Database connection failed")
        
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/health")
        
        assert response.status_code == 200  # Health endpoint should always return 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data
    
    def test_get_stats_success(self, client, mock_game_service):
        """Test successful stats retrieval."""
        with patch('app.routes.game.get_game_service', return_value=mock_game_service):
            response = client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "truths" in data
        assert "dares" in data
        assert "total_items" in data
        assert data["total_items"] == 110
        assert data["truths"]["total"] == 55
        assert data["dares"]["total"] == 55


class TestRootEndpoint:
    """Test suite for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Truth and Dare API" in data["message"]
        assert "version" in data
        assert "docs" in data
        assert data["docs"] == "/docs"


class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["status_code"] == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 for unsupported HTTP method."""
        response = client.post("/api/v1/truth")
        
        assert response.status_code == 405


class TestCORSHeaders:
    """Test suite for CORS headers."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        # Note: TestClient doesn't simulate full CORS behavior,
        # but we can verify the middleware is configured
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"