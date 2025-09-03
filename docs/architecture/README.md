# Truth and Dare API - Architecture Documentation

## System Overview

The Truth and Dare API is built using modern FastAPI patterns with a clean, modular architecture that ensures maintainability, scalability, and testability. The system follows a layered architecture with clear separation of concerns.

## Architecture Patterns

### 1. Layered Architecture
The application follows a traditional layered architecture:
- **Presentation Layer**: FastAPI routes and request/response handling
- **Business Logic Layer**: Service classes containing game logic
- **Data Access Layer**: Data loader and cache management
- **Cross-cutting Concerns**: Configuration, exception handling, logging

### 2. Dependency Injection
Services are injected using Python's built-in patterns:
- Configuration is centralized and cached using `@lru_cache`
- Services are singletons accessible via getter functions
- Dependencies are clear and testable

### 3. Repository Pattern
Data access is abstracted through:
- Centralized data loading and caching
- JSON file-based storage with in-memory caching
- Clean interface for data retrieval operations

## System Components

### Core Components

#### 1. Application Entry Point (`app/main.py`)
- **Purpose**: FastAPI application factory and configuration
- **Responsibilities**:
  - Application startup and shutdown lifecycle management
  - Middleware configuration (CORS)
  - Route registration
  - Global exception handling
  - Lifespan events management

```python
# Lifespan management with data preloading
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: preload data cache
    data_cache = get_data_cache()
    data_cache.load_data()
    yield
    # Shutdown: cleanup if needed
```

#### 2. Configuration Management (`app/core/config.py`)
- **Purpose**: Centralized configuration with environment variable support
- **Pattern**: Pydantic Settings with validation
- **Features**:
  - Type-safe configuration
  - Environment variable overrides
  - Validation and transformation
  - Caching with `@lru_cache`

#### 3. Custom Exception Handling (`app/core/exceptions.py`)
- **Purpose**: Centralized error handling and response formatting
- **Pattern**: Custom exception hierarchy with global handlers
- **Features**:
  - Consistent error response format
  - Proper HTTP status codes
  - Detailed error information for debugging

### Service Layer

#### Truth Service (`app/services/truth_service.py`)
- **Purpose**: Business logic for truth questions
- **Responsibilities**:
  - Random truth selection
  - Category-based filtering
  - Available categories listing
  - Data validation

#### Dare Service (`app/services/dare_service.py`)
- **Purpose**: Business logic for dare challenges
- **Responsibilities**:
  - Random dare selection
  - Difficulty-based filtering
  - Available difficulties listing
  - Data validation

#### Game Service (`app/services/game_service.py`)
- **Purpose**: Combined game logic and health monitoring
- **Responsibilities**:
  - Random truth/dare selection (50/50 probability)
  - Health status monitoring
  - Statistics aggregation
  - Cross-service coordination

### Data Layer

#### Data Loader (`app/utils/data_loader.py`)
- **Purpose**: Data loading and caching management
- **Pattern**: Singleton with lazy loading
- **Features**:
  - JSON file parsing and validation
  - In-memory caching for performance
  - Thread-safe operations
  - Statistics calculation

#### Data Models (`app/models/responses.py`)
- **Purpose**: Type-safe response models
- **Pattern**: Pydantic models with validation
- **Features**:
  - Request/response validation
  - OpenAPI schema generation
  - Enum-based type safety
  - Example documentation

### Routing Layer

#### Truth Routes (`app/routes/truth.py`)
- Truth-specific endpoints
- Category validation
- Error handling

#### Dare Routes (`app/routes/dare.py`)
- Dare-specific endpoints
- Difficulty validation
- Error handling

#### Game Routes (`app/routes/game.py`)
- Combined game endpoints
- Health and statistics endpoints
- System monitoring

## Data Flow Architecture

### Request Processing Flow

1. **HTTP Request** → FastAPI receives request
2. **Middleware** → CORS processing, request logging
3. **Route Handler** → Parameter validation and parsing
4. **Service Layer** → Business logic execution
5. **Data Layer** → Data retrieval from cache
6. **Response Model** → Pydantic validation and serialization
7. **HTTP Response** → JSON response with proper status codes

### Data Loading Flow

1. **Startup Event** → Application starts
2. **Data Cache** → Singleton instance created
3. **File Reading** → JSON files loaded and parsed
4. **Validation** → Data structure validation
5. **Memory Cache** → Data stored in memory for fast access
6. **Statistics** → Aggregated statistics calculated

### Error Handling Flow

1. **Exception Raised** → Any layer can raise exceptions
2. **Exception Handler** → Global or specific handler catches
3. **Error Response** → Consistent error format created
4. **Logging** → Error logged with appropriate level
5. **HTTP Response** → Proper status code and error details returned

## Design Decisions

### 1. FastAPI Framework Choice
**Decision**: Use FastAPI as the web framework
**Reasoning**:
- Automatic OpenAPI documentation generation
- Built-in request/response validation
- High performance (async support)
- Type hints integration
- Modern Python features support

### 2. JSON File Storage
**Decision**: Use JSON files instead of database
**Reasoning**:
- Simple deployment (no database setup)
- Fast read operations (cached in memory)
- Easy data management and updates
- No complex queries needed
- Perfect for read-heavy workload

### 3. In-Memory Caching
**Decision**: Cache all data in memory at startup
**Reasoning**:
- Sub-millisecond response times
- No I/O operations during requests
- Data size is small (110 items)
- Read-only operations
- Simplified architecture

### 4. Service Layer Pattern
**Decision**: Separate business logic into service classes
**Reasoning**:
- Clear separation of concerns
- Testable business logic
- Reusable across different interfaces
- Easy to modify and extend
- Clean dependency injection

### 5. Pydantic Response Models
**Decision**: Use Pydantic for all response models
**Reasoning**:
- Type safety and validation
- Automatic OpenAPI schema generation
- Consistent response format
- Easy serialization/deserialization
- Documentation integration

## Scalability Considerations

### Current Architecture Benefits
1. **Stateless Design**: No session state, easy to scale horizontally
2. **Fast Response Times**: In-memory data access
3. **Low Resource Usage**: Minimal memory and CPU requirements
4. **Simple Deployment**: Single binary with no external dependencies

### Scaling Strategies

#### Horizontal Scaling
- **Load Balancer**: Distribute requests across multiple instances
- **Container Orchestration**: Use Docker/Kubernetes for scaling
- **CDN Integration**: Cache responses at edge locations

#### Data Scaling
- **Database Migration**: Move to PostgreSQL/MongoDB for larger datasets
- **Caching Layer**: Add Redis for distributed caching
- **Data Partitioning**: Split data by categories/difficulties

#### Performance Optimization
- **Response Caching**: Cache responses with TTL
- **Compression**: Enable gzip compression
- **Connection Pooling**: For database connections (future)

## Security Architecture

### Current Security Measures
1. **Input Validation**: Pydantic models validate all inputs
2. **Path Parameter Validation**: Regex validation for categories/difficulties
3. **CORS Configuration**: Controlled cross-origin access
4. **Exception Handling**: No sensitive data in error responses
5. **No SQL Injection**: No database queries (JSON file based)

### Future Security Enhancements
1. **Rate Limiting**: Implement per-client rate limits
2. **Authentication**: Add API key or JWT authentication
3. **Request Logging**: Comprehensive access logging
4. **Input Sanitization**: Additional input cleaning
5. **Security Headers**: Add security-related HTTP headers

## Testing Architecture

### Testing Strategy
1. **Unit Tests**: Individual service and utility testing
2. **Integration Tests**: API endpoint testing
3. **Load Tests**: Performance and concurrency testing
4. **Security Tests**: Input validation and error handling

### Test Structure
```
tests/
├── test_truth_service.py    # Truth service unit tests
├── test_dare_service.py     # Dare service unit tests
├── test_game_service.py     # Game service unit tests
├── test_data_loader.py      # Data loading tests
├── test_routes_truth.py     # Truth endpoints tests
├── test_routes_dare.py      # Dare endpoints tests
├── test_routes_game.py      # Game endpoints tests
└── conftest.py              # Test configuration
```

### Coverage Metrics
- **Overall Coverage**: 84.49%
- **Tests Count**: 71 passing tests
- **Critical Paths**: 100% coverage on core business logic
- **Error Scenarios**: Comprehensive error handling tests

## Monitoring and Observability

### Logging Strategy
- **Structured Logging**: JSON-formatted logs with contextual information
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Request Tracing**: Unique request IDs for tracking
- **Error Tracking**: Detailed error logs with stack traces

### Health Monitoring
- **Health Endpoint**: `/api/v1/health` for system status
- **Statistics Endpoint**: `/api/v1/stats` for data insights
- **Startup Validation**: Data integrity checks at startup
- **Resource Monitoring**: Memory and CPU usage tracking

### Metrics Collection
- **Response Times**: Track endpoint performance
- **Error Rates**: Monitor error frequency
- **Usage Patterns**: Track endpoint usage
- **Data Statistics**: Monitor data availability

## Deployment Architecture

### Container Strategy
```dockerfile
# Lightweight Python container
FROM python:3.11-slim
# Application code and dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ app/
# Run with Gunicorn for production
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker"]
```

### Environment Configuration
- **Development**: Local development with hot-reload
- **Testing**: Isolated testing environment
- **Staging**: Production-like environment for testing
- **Production**: Optimized for performance and reliability

### Infrastructure Components
1. **Application Server**: FastAPI with Uvicorn/Gunicorn
2. **Load Balancer**: Nginx or cloud load balancer
3. **Monitoring**: Prometheus/Grafana for metrics
4. **Logging**: Centralized logging with ELK stack
5. **Container Orchestration**: Docker/Kubernetes

## Technology Stack Summary

### Backend Framework
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

### Development Tools
- **Black**: Code formatting
- **Ruff**: Linting and code analysis
- **MyPy**: Static type checking
- **Pytest**: Testing framework

### Data and Storage
- **JSON Files**: Simple data storage
- **In-Memory Cache**: Fast data access
- **Pydantic Models**: Type-safe data handling

### Deployment and Operations
- **Docker**: Containerization
- **Gunicorn**: Production WSGI server
- **Environment Variables**: Configuration management
- **Logging**: Structured application logging

This architecture provides a solid foundation for a high-performance, maintainable, and scalable API while keeping complexity minimal for the current requirements.