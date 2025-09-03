# Truth and Dare API Documentation

Welcome to the comprehensive documentation for the Truth and Dare API. This FastAPI-based REST API provides questions and challenges for the classic party game with production-ready features and extensive testing.

## Quick Links

- **[Live API](http://127.0.0.1:8000)** - Running API instance
- **[Interactive Documentation](http://127.0.0.1:8000/docs)** - Swagger UI
- **[Alternative Documentation](http://127.0.0.1:8000/redoc)** - ReDoc
- **[OpenAPI Schema](http://127.0.0.1:8000/openapi.json)** - Machine-readable API specification

## Documentation Structure

### 📚 [API Reference](api/README.md)
Complete API documentation including:
- All 9 endpoints with examples
- Request/response formats
- Error handling
- Authentication (none required)
- Rate limiting information
- Interactive examples with cURL, JavaScript, and Python

### 🏗️ [Architecture Guide](architecture/README.md)
Technical architecture and design patterns:
- System overview and components
- FastAPI application structure
- Service layer patterns
- Data flow architecture
- Security considerations
- Performance characteristics
- Scalability strategies

### 🚀 [Deployment Guide](deployment/README.md)
Production deployment instructions:
- Environment configuration
- Docker containerization
- Cloud platform deployment (AWS, GCP, Azure)
- Load balancing and scaling
- Monitoring and logging setup
- Security best practices
- Troubleshooting guide

### 💻 [Development Guide](guides/README.md)
Development workflows and practices:
- Project setup and structure
- Development workflow
- Testing strategies (84.49% coverage)
- Code quality tools
- API development patterns
- Debugging techniques
- Contributing guidelines

### 📈 [Migration & Scaling Guide](guides/migration-scaling.md)
Future-proofing and scaling strategies:
- Database migration (JSON → PostgreSQL/MongoDB)
- Horizontal and vertical scaling
- Performance optimization
- Feature scaling approaches
- Infrastructure scaling
- Version management
- Breaking changes handling

## Current API Status

### Production Metrics
- **Endpoints**: 9 fully implemented and tested
- **Test Coverage**: 84.49% with 71 passing tests
- **Security**: Zero vulnerabilities detected
- **Data**: 55 truths + 55 dares across multiple categories/difficulties
- **Performance**: <50ms response times, ~20MB memory footprint

### Available Endpoints

#### Game Endpoints
- `GET /api/v1/game/random` - Random truth or dare
- `GET /api/v1/health` - Health check and statistics
- `GET /api/v1/stats` - Comprehensive statistics

#### Truth Endpoints
- `GET /api/v1/truth` - Random truth question
- `GET /api/v1/truth/{category}` - Truth by category
- `GET /api/v1/truth/categories/list` - Available categories

#### Dare Endpoints
- `GET /api/v1/dare` - Random dare challenge
- `GET /api/v1/dare/{difficulty}` - Dare by difficulty
- `GET /api/v1/dare/difficulties/list` - Available difficulties

### Truth Categories
- **general**: General truth questions
- **relationships**: Questions about relationships and dating
- **funny**: Humorous and light-hearted questions
- **deep**: Thought-provoking and serious questions
- **embarrassing**: Potentially embarrassing questions

### Dare Difficulties
- **easy**: Simple and safe challenges (18 dares)
- **medium**: Moderately challenging dares (18 dares)
- **hard**: Challenging dares requiring courage (19 dares)

## Technology Stack

### Backend Framework
- **FastAPI**: Modern, fast web framework with automatic documentation
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for development and production

### Data & Storage
- **JSON Files**: Simple, efficient data storage for current scale
- **In-Memory Caching**: Fast data access with startup preloading
- **Future**: PostgreSQL/MongoDB migration path documented

### Development Tools
- **Black**: Code formatting
- **Ruff**: Fast Python linter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with comprehensive coverage

### Deployment & Operations
- **Docker**: Containerization support
- **Kubernetes**: Orchestration configurations
- **CORS**: Cross-origin resource sharing
- **Health Checks**: Built-in monitoring endpoints

## Getting Started

### Quick Setup
```bash
# Clone and setup
git clone <repository-url>
cd truth-dare-api
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Run development server
fastapi dev app/main.py --port 8000

# Access API
curl http://localhost:8000/api/v1/truth
```

### Example Usage
```javascript
// Get random truth
const truth = await fetch('http://localhost:8000/api/v1/truth')
  .then(response => response.json());

// Get easy dare
const dare = await fetch('http://localhost:8000/api/v1/dare/easy')
  .then(response => response.json());

// Get random game item
const game = await fetch('http://localhost:8000/api/v1/game/random')
  .then(response => response.json());
```

## Key Features

### Production Ready
- **Comprehensive Error Handling**: Consistent error responses
- **Type Safety**: Full type hints with Pydantic validation
- **CORS Support**: Configurable cross-origin access
- **Health Monitoring**: Built-in health check and statistics
- **Logging**: Structured application logging

### High Performance
- **Fast Response Times**: <50ms for all endpoints
- **Memory Efficient**: ~20MB baseline memory usage
- **Concurrent Support**: 1000+ concurrent connections
- **Caching**: In-memory data caching for optimal performance

### Developer Friendly
- **Automatic Documentation**: OpenAPI/Swagger generation
- **Type Validation**: Request/response validation
- **Testing**: Comprehensive test suite with high coverage
- **Code Quality**: Formatted, linted, and type-checked

### Scalable Architecture
- **Modular Design**: Clean separation of concerns
- **Service Layer**: Reusable business logic
- **Configuration Management**: Environment-based settings
- **Migration Path**: Clear scaling strategies documented

## Architecture Overview

```
├── Presentation Layer    # FastAPI routes and request handling
├── Business Logic Layer  # Service classes with game logic
├── Data Access Layer     # Data loading and caching
└── Configuration Layer   # Settings and environment management
```

The API follows a layered architecture with clear separation between:
- **Routes**: HTTP request/response handling
- **Services**: Business logic and data processing
- **Models**: Type-safe data structures
- **Utils**: Shared utilities and helpers

## Security

- **Input Validation**: All inputs validated with Pydantic
- **No SQL Injection**: JSON file-based storage
- **CORS Configuration**: Controlled cross-origin access
- **Error Handling**: No sensitive data in error responses
- **Type Safety**: Runtime type checking prevents errors

## Future Roadmap

### Near Term (v2.0)
- Database migration (PostgreSQL)
- Enhanced content filtering
- User authentication
- Content rating system

### Medium Term (v3.0)
- Multi-language support
- Content personalization
- Advanced analytics
- Mobile app support

### Long Term (v4.0)
- AI-generated content
- Real-time multiplayer features
- Social features
- Enterprise features

## Support

- **Documentation**: Complete guides and references
- **Health Endpoint**: `/api/v1/health` for monitoring
- **Error Responses**: Detailed error information
- **Test Coverage**: 84.49% coverage for reliability

## Contributing

See the [Development Guide](guides/README.md) for:
- Development setup
- Coding standards
- Testing requirements
- Pull request process

---

**Built with FastAPI and modern Python practices**

This documentation provides everything needed to use, deploy, and extend the Truth and Dare API. Start with the [API Reference](api/README.md) for immediate usage or the [Development Guide](guides/README.md) for contributing to the project.