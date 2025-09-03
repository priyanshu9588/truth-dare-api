# Truth and Dare API - Development Guide

## Overview

This guide covers development workflows, testing procedures, and contribution guidelines for the Truth and Dare API project.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing Guide](#testing-guide)
5. [Code Quality](#code-quality)
6. [API Development](#api-development)
7. [Data Management](#data-management)
8. [Debugging](#debugging)
9. [Contributing](#contributing)

## Development Setup

### Prerequisites

- **Python 3.11+** (developed with Python 3.13.7)
- **Git** for version control
- **VS Code** or preferred IDE
- **Docker** (optional, for containerized development)

### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd truth-dare-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
fastapi dev app/main.py --port 8000
```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

#### VS Code Extensions

- Python
- Python Docstring Generator
- Black Formatter
- MyPy Type Checker
- REST Client
- Python Test Explorer

## Project Structure

### Directory Layout

```
truth-dare-api/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   └── exceptions.py  # Custom exceptions
│   ├── data/              # JSON data files
│   │   ├── truths.json    # Truth questions
│   │   └── dares.json     # Dare challenges
│   ├── models/            # Pydantic models
│   │   ├── __init__.py
│   │   └── responses.py   # API response models
│   ├── routes/            # API route handlers
│   │   ├── __init__.py
│   │   ├── dare.py        # Dare endpoints
│   │   ├── game.py        # Game and health endpoints
│   │   └── truth.py       # Truth endpoints
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── dare_service.py
│   │   ├── game_service.py
│   │   └── truth_service.py
│   └── utils/             # Utility modules
│       ├── __init__.py
│       └── data_loader.py # Data loading and caching
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py       # Test configuration
│   ├── test_*.py         # Test files
│   └── fixtures/         # Test data
├── docs/                 # Documentation
│   ├── api/              # API documentation
│   ├── architecture/     # Architecture docs
│   ├── deployment/       # Deployment guides
│   └── guides/           # Development guides
├── .github/              # GitHub workflows
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml       # Tool configuration
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
└── README.md            # Project overview
```

### Architecture Patterns

#### Service Layer Pattern
```python
# services/truth_service.py
class TruthService:
    def __init__(self, data_loader: DataLoader):
        self._data_loader = data_loader
    
    def get_random_truth(self) -> dict:
        """Get a random truth question."""
        truths = self._data_loader.get_truths()
        return random.choice(truths)
```

#### Dependency Injection
```python
# Singleton pattern for services
@lru_cache
def get_truth_service() -> TruthService:
    return TruthService(get_data_cache())
```

#### Repository Pattern
```python
# utils/data_loader.py
class DataCache:
    def load_data(self) -> None:
        """Load and cache data from JSON files."""
        # Implementation here
        pass
```

## Development Workflow

### Git Workflow

#### Branch Strategy

```bash
# Feature development
git checkout -b feature/add-new-category
git commit -m "Add new truth category: lifestyle"
git push origin feature/add-new-category

# Bug fixes
git checkout -b bugfix/fix-category-validation
git commit -m "Fix category case sensitivity validation"
git push origin bugfix/fix-category-validation

# Hotfixes
git checkout -b hotfix/critical-data-loading-fix
git commit -m "Fix critical data loading issue"
git push origin hotfix/critical-data-loading-fix
```

#### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(api): add new truth category endpoint"
git commit -m "fix(data): resolve case sensitivity in category validation"
git commit -m "docs(api): update endpoint documentation"
git commit -m "test(services): add comprehensive service layer tests"
```

### Development Commands

```bash
# Start development server with auto-reload
fastapi dev app/main.py --port 8000

# Run tests
pytest
pytest -v                    # Verbose output
pytest --cov=app            # With coverage
pytest tests/unit/          # Specific directory
pytest -k "test_truth"      # Specific test pattern

# Code quality checks
black .                     # Format code
ruff check .               # Lint code
ruff check . --fix         # Auto-fix linting issues
mypy app/                  # Type checking

# All quality checks at once
black . && ruff check . --fix && mypy app/ && pytest --cov=app
```

### Environment Management

#### Development Environment

```env
# .env.development
TRUTH_DARE_DEBUG=true
TRUTH_DARE_LOG_LEVEL=DEBUG
TRUTH_DARE_HOST=127.0.0.1
TRUTH_DARE_PORT=8000
TRUTH_DARE_CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### Testing Environment

```env
# .env.testing
TRUTH_DARE_DEBUG=false
TRUTH_DARE_LOG_LEVEL=WARNING
TRUTH_DARE_TRUTHS_FILE_PATH=tests/fixtures/test_truths.json
TRUTH_DARE_DARES_FILE_PATH=tests/fixtures/test_dares.json
```

## Testing Guide

### Test Structure

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_truth():
    return {
        "id": 1,
        "content": "What is your biggest fear?",
        "category": "deep"
    }
```

### Unit Testing

```python
# tests/unit/test_truth_service.py
import pytest
from app.services.truth_service import TruthService
from app.utils.data_loader import DataCache

class TestTruthService:
    def setup_method(self):
        self.data_cache = DataCache()
        self.service = TruthService(self.data_cache)
    
    def test_get_random_truth(self):
        """Test random truth retrieval."""
        truth = self.service.get_random_truth()
        
        assert "id" in truth
        assert "content" in truth
        assert "category" in truth
        assert isinstance(truth["id"], int)
        assert isinstance(truth["content"], str)
        assert len(truth["content"]) > 0
    
    def test_get_truth_by_category(self):
        """Test category-specific truth retrieval."""
        truth = self.service.get_truth_by_category("funny")
        
        assert truth["category"] == "funny"
        assert isinstance(truth["content"], str)
    
    def test_invalid_category_raises_exception(self):
        """Test invalid category handling."""
        with pytest.raises(CategoryNotFoundError):
            self.service.get_truth_by_category("invalid")
```

### Integration Testing

```python
# tests/integration/test_truth_routes.py
import pytest
from fastapi.testclient import TestClient

class TestTruthRoutes:
    def test_get_random_truth(self, client: TestClient):
        """Test random truth endpoint."""
        response = client.get("/api/v1/truth")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "type" in data
        assert "content" in data
        assert "category" in data
        assert data["type"] == "truth"
    
    def test_get_truth_by_category(self, client: TestClient):
        """Test category-specific truth endpoint."""
        response = client.get("/api/v1/truth/funny")
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "funny"
    
    def test_invalid_category_returns_404(self, client: TestClient):
        """Test invalid category handling."""
        response = client.get("/api/v1/truth/invalid")
        
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert "message" in error
```

### Performance Testing

```python
# tests/performance/test_load.py
import time
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

class TestPerformance:
    def test_response_time(self, client: TestClient):
        """Test single request response time."""
        start_time = time.time()
        response = client.get("/api/v1/truth")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.1  # Less than 100ms
    
    def test_concurrent_requests(self, client: TestClient):
        """Test concurrent request handling."""
        def make_request():
            return client.get("/api/v1/truth")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
```

### Test Data Management

```json
// tests/fixtures/test_truths.json
[
  {
    "id": 1,
    "content": "Test truth question 1?",
    "category": "general"
  },
  {
    "id": 2,
    "content": "Test truth question 2?",
    "category": "funny"
  }
]
```

```python
# tests/fixtures/data.py
SAMPLE_TRUTHS = [
    {"id": 1, "content": "Test truth 1?", "category": "general"},
    {"id": 2, "content": "Test truth 2?", "category": "funny"},
]

SAMPLE_DARES = [
    {"id": 1, "content": "Test dare 1", "difficulty": "easy"},
    {"id": 2, "content": "Test dare 2", "difficulty": "medium"},
]
```

## Code Quality

### Formatting with Black

```python
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | \.pytest_cache
  | build
  | dist
)/
'''
```

### Linting with Ruff

```python
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
```

### Type Checking with MyPy

```python
# pyproject.toml
[tool.mypy]
python_version = "3.11"
check_untyped_defs = true
disallow_any_generics = true
disallow_untyped_defs = true
follow_imports = "silent"
strict_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_unimported = true
no_implicit_optional = true
warn_return_any = true
warn_unused_configs = true
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.264
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## API Development

### Adding New Endpoints

#### 1. Define Response Model

```python
# app/models/responses.py
class NewFeatureResponse(BaseResponse):
    """Response model for new feature."""
    
    id: int = Field(..., description="Unique identifier")
    data: str = Field(..., description="Feature data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "data": "Sample data"
            }
        }
```

#### 2. Implement Service Logic

```python
# app/services/new_feature_service.py
from typing import Dict, Any

class NewFeatureService:
    def __init__(self, data_loader: DataLoader):
        self._data_loader = data_loader
    
    def get_feature_data(self) -> Dict[str, Any]:
        """Get feature data."""
        # Implement business logic
        return {"id": 1, "data": "sample"}

@lru_cache
def get_new_feature_service() -> NewFeatureService:
    return NewFeatureService(get_data_cache())
```

#### 3. Create Route Handler

```python
# app/routes/new_feature.py
from fastapi import APIRouter, HTTPException
from app.models.responses import NewFeatureResponse
from app.services.new_feature_service import get_new_feature_service

router = APIRouter(
    prefix="/feature",
    tags=["new-feature"],
    responses={500: {"description": "Internal server error"}}
)

@router.get(
    "",
    response_model=NewFeatureResponse,
    summary="Get Feature Data",
    description="Retrieve feature data from the API."
)
async def get_feature() -> NewFeatureResponse:
    """Get feature data."""
    try:
        service = get_new_feature_service()
        data = service.get_feature_data()
        return NewFeatureResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### 4. Register Route

```python
# app/main.py
from app.routes import new_feature

app.include_router(new_feature.router, prefix=settings.api_v1_prefix)
```

#### 5. Add Tests

```python
# tests/test_new_feature.py
def test_new_feature_endpoint(client: TestClient):
    response = client.get("/api/v1/feature")
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "data" in data
```

### Error Handling Patterns

```python
# app/core/exceptions.py
class FeatureNotFoundError(TruthDareAPIException):
    """Raised when feature is not found."""
    
    def __init__(self, feature_id: int):
        super().__init__(
            message=f"Feature with ID {feature_id} not found",
            status_code=404,
            details={"feature_id": feature_id}
        )
```

### Validation Patterns

```python
from pydantic import validator, Field

class FeatureRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., regex="^[a-zA-Z]+$")
    
    @validator("category")
    def validate_category(cls, v):
        valid_categories = ["general", "special"]
        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        return v.lower()
```

## Data Management

### JSON Data Format

#### Truth Questions

```json
{
  "id": 1,
  "content": "What is your biggest fear?",
  "category": "deep"
}
```

#### Dare Challenges

```json
{
  "id": 1,
  "content": "Do 10 jumping jacks",
  "difficulty": "easy"
}
```

### Adding New Content

#### Script for Adding Truths

```python
# scripts/add_truth.py
import json
import sys
from pathlib import Path

def add_truth(content: str, category: str):
    """Add a new truth question."""
    truths_file = Path("app/data/truths.json")
    
    with open(truths_file, "r") as f:
        truths = json.load(f)
    
    # Find next ID
    max_id = max(truth["id"] for truth in truths)
    new_id = max_id + 1
    
    # Add new truth
    new_truth = {
        "id": new_id,
        "content": content,
        "category": category
    }
    truths.append(new_truth)
    
    # Write back to file
    with open(truths_file, "w") as f:
        json.dump(truths, f, indent=2)
    
    print(f"Added truth {new_id}: {content}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_truth.py <content> <category>")
        sys.exit(1)
    
    add_truth(sys.argv[1], sys.argv[2])
```

#### Data Validation Script

```python
# scripts/validate_data.py
import json
from pathlib import Path
from typing import List, Dict, Any

def validate_truths(truths: List[Dict[str, Any]]) -> bool:
    """Validate truth data structure."""
    required_fields = ["id", "content", "category"]
    valid_categories = ["general", "relationships", "funny", "deep", "embarrassing"]
    
    ids = set()
    for truth in truths:
        # Check required fields
        if not all(field in truth for field in required_fields):
            print(f"Truth missing required fields: {truth}")
            return False
        
        # Check ID uniqueness
        if truth["id"] in ids:
            print(f"Duplicate truth ID: {truth['id']}")
            return False
        ids.add(truth["id"])
        
        # Check category
        if truth["category"] not in valid_categories:
            print(f"Invalid category: {truth['category']}")
            return False
        
        # Check content
        if not isinstance(truth["content"], str) or len(truth["content"]) == 0:
            print(f"Invalid content: {truth['content']}")
            return False
    
    return True

def main():
    """Validate all data files."""
    truths_file = Path("app/data/truths.json")
    dares_file = Path("app/data/dares.json")
    
    # Validate truths
    with open(truths_file, "r") as f:
        truths = json.load(f)
    
    if not validate_truths(truths):
        print("Truth validation failed")
        return False
    
    print(f"Validated {len(truths)} truths successfully")
    return True

if __name__ == "__main__":
    main()
```

## Debugging

### Debug Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    
    @property
    def is_debug(self) -> bool:
        return self.debug and self.log_level.upper() == "DEBUG"
```

### Logging Setup

```python
# app/main.py
import logging
import sys

def setup_logging(settings: Settings):
    """Configure application logging."""
    level = getattr(logging, settings.log_level.upper())
    
    logging.basicConfig(
        level=level,
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log") if settings.debug else logging.NullHandler()
        ]
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
```

### Debug Endpoints

```python
# app/routes/debug.py (only in development)
from fastapi import APIRouter, Depends
from app.core.config import get_settings

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/info")
async def debug_info(settings: Settings = Depends(get_settings)):
    """Get debug information."""
    if not settings.is_debug:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "config": settings.dict(),
        "data_stats": get_data_cache().get_stats(),
        "memory_usage": get_memory_usage()
    }
```

### Performance Profiling

```python
# scripts/profile_app.py
import cProfile
import pstats
from app.main import app
from fastapi.testclient import TestClient

def profile_endpoint(endpoint: str, num_requests: int = 100):
    """Profile an API endpoint."""
    client = TestClient(app)
    
    def make_requests():
        for _ in range(num_requests):
            response = client.get(endpoint)
            assert response.status_code == 200
    
    # Profile the function
    profiler = cProfile.Profile()
    profiler.enable()
    make_requests()
    profiler.disable()
    
    # Save results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

if __name__ == "__main__":
    profile_endpoint("/api/v1/truth", 1000)
```

## Contributing

### Pull Request Process

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/truth-dare-api.git
   cd truth-dare-api
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

4. **Quality Checks**
   ```bash
   # Run all quality checks
   make quality-check
   
   # Or manually
   black .
   ruff check . --fix
   mypy app/
   pytest --cov=app
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use clear title and description
   - Reference any related issues
   - Include screenshots if applicable

### Code Review Guidelines

#### For Authors
- Keep PRs small and focused
- Write clear commit messages
- Add comprehensive tests
- Update documentation
- Respond to feedback promptly

#### For Reviewers
- Check functionality and logic
- Verify test coverage
- Review for security issues
- Ensure code style compliance
- Test locally if needed

### Makefile Commands

```makefile
# Makefile
.PHONY: install dev test quality-check clean

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest --cov=app --cov-report=term-missing

quality-check:
	black .
	ruff check . --fix
	mypy app/
	pytest --cov=app

clean:
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage .pytest_cache .mypy_cache

dev-server:
	fastapi dev app/main.py --port 8000

build:
	docker build -t truth-dare-api .

run:
	docker run -p 8000:8000 truth-dare-api
```

This development guide provides comprehensive instructions for setting up, developing, testing, and contributing to the Truth and Dare API project.