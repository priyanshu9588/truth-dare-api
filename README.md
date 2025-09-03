# Truth and Dare API

A production-ready FastAPI-based REST API that provides questions and challenges for the classic party game Truth or Dare. Built with modern Python practices, comprehensive testing, and robust error handling.

## 🚀 Features

- **Random Game Selection**: Get a random truth question or dare challenge
- **Category-based Truths**: Filter truth questions by categories (general, relationships, funny, deep, embarrassing)
- **Difficulty-based Dares**: Filter dare challenges by difficulty levels (easy, medium, hard)
- **Health Monitoring**: Built-in health check and statistics endpoints
- **Type Safety**: Full type hints with Pydantic v2 validation
- **Comprehensive Testing**: 84.49% test coverage with 71 passing tests
- **Production Ready**: CORS support, error handling, and configuration management

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Installation](#installation)
- [Development](#development)
- [Testing](#testing)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 📚 Documentation

### Comprehensive Documentation
The API includes extensive documentation in the `docs/` folder:

- **[API Reference](docs/api/README.md)** - Complete API documentation with examples
- **[Architecture Guide](docs/architecture/README.md)** - Technical architecture and design patterns
- **[Deployment Guide](docs/deployment/README.md)** - Production deployment instructions
- **[Development Guide](docs/guides/README.md)** - Development setup and workflows

### Interactive API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## ⚡ Quick Start

### Prerequisites

- Python 3.11+ (developed with Python 3.13.7)
- pip or uv for package management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd truth-dare-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API**
   ```bash
   fastapi dev app/main.py --port 8000
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Game Endpoints

**Get Random Truth or Dare**
```http
GET /api/v1/game/random
```

Response:
```json
{
  "id": 1,
  "type": "truth",
  "content": "What's the most embarrassing thing you've ever done?",
  "category": "embarrassing",
  "difficulty": null
}
```

**Health Check**
```http
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "total_truths": 55,
    "total_dares": 55,
    "truth_categories": 5,
    "dare_difficulties": 3
  },
  "categories": {
    "general": 11,
    "relationships": 11,
    "funny": 11,
    "deep": 11,
    "embarrassing": 11
  },
  "difficulties": {
    "easy": 18,
    "medium": 18,
    "hard": 19
  }
}
```

**Get Statistics**
```http
GET /api/v1/stats
```

#### Truth Endpoints

**Get Random Truth**
```http
GET /api/v1/truth
```

**Get Truth by Category**
```http
GET /api/v1/truth/{category}
```

Available categories: `general`, `relationships`, `funny`, `deep`, `embarrassing`

Example:
```http
GET /api/v1/truth/funny
```

**Get Available Categories**
```http
GET /api/v1/truth/categories/list
```

Response:
```json
["deep", "embarrassing", "funny", "general", "relationships"]
```

#### Dare Endpoints

**Get Random Dare**
```http
GET /api/v1/dare
```

**Get Dare by Difficulty**
```http
GET /api/v1/dare/{difficulty}
```

Available difficulties: `easy`, `medium`, `hard`

Example:
```http
GET /api/v1/dare/medium
```

**Get Available Difficulties**
```http
GET /api/v1/dare/difficulties/list
```

Response:
```json
["easy", "medium", "hard"]
```

### Response Format

All successful responses follow this structure:

```json
{
  "id": 1,
  "type": "truth|dare",
  "content": "Question or challenge text",
  "category": "optional category for truths",
  "difficulty": "optional difficulty for dares"
}
```

### Error Responses

```json
{
  "detail": "Error message",
  "error_code": "CATEGORY_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

HTTP Status Codes:
- `200`: Success
- `404`: Category/difficulty not found
- `422`: Validation error
- `500`: Internal server error

## 🛠 Installation & Development

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run with auto-reload**
   ```bash
   fastapi dev app/main.py --port 8000
   ```

### Project Structure

```
truth-dare-api/
├── app/                    # Main application directory
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   └── exceptions.py  # Custom exceptions
│   ├── data/              # JSON data files
│   │   ├── truths.json    # Truth questions database
│   │   └── dares.json     # Dare challenges database
│   ├── models/            # Pydantic models
│   │   └── responses.py   # API response models
│   ├── routes/            # API route handlers
│   │   ├── dare.py        # Dare endpoints
│   │   ├── game.py        # Game and health endpoints
│   │   └── truth.py       # Truth endpoints
│   ├── services/          # Business logic
│   │   ├── dare_service.py
│   │   ├── game_service.py
│   │   └── truth_service.py
│   └── utils/             # Utility modules
│       └── data_loader.py # Data loading and caching
├── tests/                  # Test suite
│   ├── integration/       # Integration tests
│   ├── unit/             # Unit tests
│   └── conftest.py       # Test configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml        # Tool configuration
└── .env.example          # Environment variables template
```

### Code Quality Tools

The project uses several tools to maintain code quality:

**Black** - Code formatting
```bash
black .
```

**Ruff** - Linting and code analysis
```bash
ruff check .
ruff check . --fix  # Auto-fix issues
```

**MyPy** - Type checking
```bash
mypy app/
```

**All tools together**
```bash
black . && ruff check . --fix && mypy app/
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_truth_service.py

# Run with verbose output
pytest -v
```

### Test Coverage

Current test coverage: **84.49%** with **71 passing tests**

Coverage breakdown:
- `app/services/`: 95%+ coverage
- `app/routes/`: 90%+ coverage  
- `app/utils/`: 85%+ coverage
- `app/models/`: 100% coverage

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints end-to-end
- **Fixtures**: Shared test data and configuration

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server Configuration
TRUTH_DARE_HOST=127.0.0.1
TRUTH_DARE_PORT=8000
TRUTH_DARE_DEBUG=false

# API Configuration
TRUTH_DARE_API_V1_PREFIX=/api/v1
TRUTH_DARE_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Data Configuration
TRUTH_DARE_TRUTHS_FILE_PATH=app/data/truths.json
TRUTH_DARE_DARES_FILE_PATH=app/data/dares.json

# Logging Configuration
TRUTH_DARE_LOG_LEVEL=INFO
TRUTH_DARE_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Performance Configuration
TRUTH_DARE_CACHE_EXPIRY_SECONDS=3600
TRUTH_DARE_MAX_CONCURRENT_REQUESTS=1000

# Application Information
TRUTH_DARE_APP_NAME=Truth and Dare API
TRUTH_DARE_APP_VERSION=0.1.0
```

### Configuration Details

All configuration is handled through Pydantic Settings with:
- Type validation and conversion
- Environment variable support with `TRUTH_DARE_` prefix
- Default values for all settings
- Validation for critical settings (log levels, CORS origins)

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
   ```env
   TRUTH_DARE_DEBUG=false
   TRUTH_DARE_LOG_LEVEL=WARNING
   TRUTH_DARE_HOST=0.0.0.0
   TRUTH_DARE_PORT=8000
   ```

2. **Install production dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run with Uvicorn**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t truth-dare-api .
docker run -p 8000:8000 truth-dare-api
```

### Health Monitoring

The API includes comprehensive health monitoring:

- **Health endpoint**: `/api/v1/health`
- **Metrics**: Data availability, counts, and statistics
- **Error tracking**: Automatic error logging and reporting
- **Status levels**: healthy, degraded, unhealthy

## 📊 Performance

### Optimization Features

- **In-memory caching**: JSON data loaded once at startup
- **LRU caching**: Settings cached with functools.lru_cache
- **Async endpoints**: All routes use async/await for better concurrency
- **Data indexing**: Pre-built indexes for categories and difficulties
- **Efficient data structures**: Optimized for random selection

### Performance Characteristics

- **Startup time**: ~100ms (data loading)
- **Response time**: <10ms for cached data
- **Memory usage**: ~50MB base + data size
- **Concurrency**: Configurable max concurrent requests

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
4. **Run tests and quality checks**
   ```bash
   pytest --cov=app
   black .
   ruff check . --fix
   mypy app/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add your feature"
   ```

6. **Push and create a Pull Request**

### Code Standards

- **Type hints**: All functions must have type hints
- **Docstrings**: All public functions and classes need docstrings
- **Error handling**: Proper exception handling with custom exceptions
- **Testing**: New features must include tests
- **Coverage**: Maintain >80% test coverage

### Adding New Content

#### Adding Truths

Edit `app/data/truths.json`:

```json
{
  "id": 36,
  "content": "Your new truth question?",
  "category": "general"
}
```

#### Adding Dares

Edit `app/data/dares.json`:

```json
{
  "id": 31,
  "content": "Your new dare challenge",
  "difficulty": "medium"
}
```

## 📄 License

[Add your license information here]

## 🙋 Support

- **Documentation**: http://localhost:8000/docs (when running)
- **Issues**: [Create an issue](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ using FastAPI and modern Python practices**