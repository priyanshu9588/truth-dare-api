# Project Structure

## Directory Organization

```
truth-dare-api/
├── app/                    # Main application source code
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Core configuration and cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py      # Pydantic Settings configuration
│   │   └── exceptions.py  # Custom exception classes
│   ├── models/            # Pydantic response models and enums
│   │   ├── __init__.py
│   │   └── responses.py   # API response models with validation
│   ├── routes/            # FastAPI route handlers (controllers)
│   │   ├── __init__.py
│   │   ├── truth.py       # Truth-related endpoints
│   │   ├── dare.py        # Dare-related endpoints
│   │   └── game.py        # Game and health endpoints
│   ├── services/          # Business logic layer
│   │   ├── __init__.py
│   │   ├── truth_service.py    # Truth business logic
│   │   ├── dare_service.py     # Dare business logic
│   │   └── game_service.py     # Game logic and random selection
│   ├── data/              # Static JSON data files
│   │   ├── truths.json    # Truth questions with categories
│   │   └── dares.json     # Dare challenges with difficulties
│   └── utils/             # Shared utilities and helpers
│       ├── __init__.py
│       └── data_loader.py # Data loading and caching system
├── tests/                  # Test suite organized by component
│   ├── __init__.py
│   ├── test_truth_service.py      # Truth service unit tests
│   ├── test_dare_service.py       # Dare service unit tests
│   ├── test_game_service.py       # Game service unit tests
│   ├── test_data_loader.py        # Data loader unit tests
│   ├── test_truth_routes.py       # Truth API integration tests
│   ├── test_dare_routes.py        # Dare API integration tests
│   ├── test_game_routes.py        # Game API integration tests
│   ├── test_health_routes.py      # Health check integration tests
│   └── test_performance.py        # Performance and load tests
├── .claude/                # Claude Code configuration and context
│   ├── steering/          # Project steering documents
│   └── specs/             # Specifications and task definitions
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
├── CLAUDE.md              # Project instructions for Claude Code
└── README.md              # Project documentation
```

## Naming Conventions

### Files
- **Modules**: `snake_case` for all Python files (e.g., `truth_service.py`, `data_loader.py`)
- **Packages**: `snake_case` for directories with `__init__.py` (e.g., `models/`, `services/`)
- **Data Files**: `snake_case` with descriptive names (e.g., `truths.json`, `dares.json`)
- **Tests**: `test_[module_name].py` pattern for test files (e.g., `test_truth_service.py`)

### Code
- **Classes/Types**: `PascalCase` for all classes and Pydantic models (e.g., `TruthResponse`, `DataCache`)
- **Functions/Methods**: `snake_case` for all functions and methods (e.g., `get_random_truth`, `load_data`)
- **Constants**: `UPPER_SNAKE_CASE` for module-level constants (e.g., `DEFAULT_PORT`, `API_PREFIX`)
- **Variables**: `snake_case` for all variables and parameters (e.g., `truth_data`, `category_filter`)
- **Enums**: `PascalCase` for enum classes, `UPPER_CASE` for values (e.g., `TruthCategory.GENERAL`)

## Import Patterns

### Import Order
1. Standard library imports
2. Third-party library imports (FastAPI, Pydantic, etc.)
3. Local application imports (app.* modules)
4. Relative imports within the same package

### Module Organization
```python
# Standard library
import logging
from typing import Any, Dict, List

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Local application
from app.core.config import get_settings
from app.models.responses import TruthResponse
from app.services.truth_service import get_random_truth

# Relative imports
from .exceptions import CategoryNotFoundError
```

## Code Structure Patterns

### Module Organization
```python
# 1. Module docstring
"""
Module description and purpose.
"""

# 2. Imports (following import order)
import standard_library
from third_party import module
from app.local import module

# 3. Constants and configuration
DEFAULT_CATEGORY = "general"
MAX_RETRIES = 3

# 4. Type definitions and enums
class CategoryEnum(str, Enum):
    GENERAL = "general"

# 5. Main implementation (classes, functions)
class ServiceClass:
    def __init__(self):
        pass

def utility_function():
    pass

# 6. Module-level initialization or exports
__all__ = ["ServiceClass", "utility_function"]
```

### Function Organization
```python
def service_function(input_param: str) -> ResponseModel:
    """
    Function docstring with Args and Returns.
    """
    # 1. Input validation
    if not input_param:
        raise ValueError("Input parameter required")
    
    # 2. Core business logic
    result = process_input(input_param)
    
    # 3. Response preparation
    return ResponseModel(data=result)
```

### Class Organization
```python
class ServiceClass:
    """Class docstring."""
    
    # Class variables
    DEFAULT_VALUE = "default"
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        self._config = config
        self._cache = {}
    
    # Public methods first
    def public_method(self) -> str:
        """Public interface method."""
        return self._private_method()
    
    # Private methods last
    def _private_method(self) -> str:
        """Internal implementation method."""
        return "result"
```

## Code Organization Principles

1. **Single Responsibility**: Each module and class has one clear purpose and reason to change
2. **Layer Separation**: Clear boundaries between routes, services, models, and data layers
3. **Dependency Injection**: Services receive dependencies through parameters, not global imports
4. **Testability**: All business logic in services layer, easily mockable dependencies
5. **Configuration Centralization**: All configuration in `app/core/config.py` with environment variables

## Module Boundaries

### Layer Dependencies (Allowed Direction)
```
Routes → Services → Data Layer
   ↓        ↓          ↓
Models ← Utilities ← Core
```

**Boundary Rules:**
- **Routes** can call Services and Models, cannot directly access Data Layer
- **Services** contain business logic, call Data Layer utilities, return Model instances
- **Models** are pure data structures with validation, no business logic
- **Core** provides configuration and exceptions, no dependencies on other layers
- **Utilities** are pure functions, minimal dependencies

### API Boundary Patterns
- **Public API**: Routes define the external interface with comprehensive OpenAPI documentation
- **Business Logic**: Services contain all game rules, validation, and data transformation
- **Data Access**: Utils/data_loader provides abstraction over data storage mechanism
- **Configuration**: Core/config centralizes all environment-dependent settings

## Code Size Guidelines

### File Size Limits
- **Route Files**: Maximum 200 lines (focused on single resource type)
- **Service Files**: Maximum 300 lines (single business domain)
- **Model Files**: Maximum 500 lines (related response models and enums)
- **Utility Files**: Maximum 200 lines (focused utility functions)

### Function/Method Size
- **Route Handlers**: Maximum 30 lines (minimal logic, delegate to services)
- **Service Methods**: Maximum 50 lines (single business operation)
- **Utility Functions**: Maximum 40 lines (focused utility operation)
- **Model Validators**: Maximum 20 lines (simple validation logic)

### Complexity Guidelines
- **Nesting Depth**: Maximum 3 levels of indentation
- **Function Parameters**: Maximum 5 parameters (use dataclasses/models for more)
- **Class Methods**: Maximum 10 public methods per class
- **Module Exports**: Explicit `__all__` for public modules

## Testing Structure

### Test Organization
```python
# Test files mirror source structure
tests/test_[module_name].py

# Test class per source class
class TestTruthService:
    
    # Test method per public method
    def test_get_random_truth_success(self):
        pass
    
    def test_get_random_truth_empty_category(self):
        pass
```

### Test Patterns
- **Unit Tests**: Test individual functions/methods in isolation with mocks
- **Integration Tests**: Test API endpoints with real FastAPI test client
- **Performance Tests**: Load testing with concurrent requests
- **Error Tests**: Comprehensive error condition coverage

## Documentation Standards

### Docstring Requirements
- **All public functions**: Google-style docstrings with Args, Returns, Raises
- **All classes**: Class purpose, key attributes, usage examples
- **All modules**: Module purpose, key exports, usage patterns
- **Complex logic**: Inline comments explaining business rules

### Example Docstring Format
```python
def get_truth_by_category(category: str) -> TruthResponse:
    """
    Retrieve a random truth question from the specified category.
    
    Args:
        category: The truth category to filter by. Must be one of:
            'general', 'relationships', 'funny', 'deep', 'embarrassing'
    
    Returns:
        TruthResponse: A truth question with id, type, content, and category
    
    Raises:
        CategoryNotFoundError: If the specified category doesn't exist
        DataNotLoadedError: If truth data hasn't been loaded yet
    """
```

### API Documentation
- **OpenAPI Specification**: Auto-generated from FastAPI decorators and Pydantic models
- **Response Examples**: Comprehensive examples in Pydantic model configs
- **Error Documentation**: All possible error responses documented with examples
- **Endpoint Descriptions**: Clear descriptions of endpoint purpose and usage