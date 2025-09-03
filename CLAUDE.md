# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent Configuration for Claude Code

### Primary Agent for ALL Development Tasks
**ALWAYS USE: master-developer-orchestrator**

The master-developer-orchestrator MUST be used for ALL development tasks because it:
- Coordinates all specialized agents automatically
- Maintains context across the entire project
- Ensures security scanning and documentation
- Manages the complete development lifecycle

### Available Agent System (15 Orchestrators + 75+ Power Agents)

**🎯 Planning & Coordination:**
- `spec-planner` - Project specification generation (ALWAYS FIRST for new features)
- `claude-md-manager` - CLAUDE.md management (MANDATORY AFTER EVERY AGENT)
- `context-manager` - Context management (AT PHASE TRANSITIONS)
- `git-manager` - Git operations, GitHub management (AFTER EVERY TASK)

**🎯 Core Orchestrators:**
- `mcp-orchestrator` - Web research, external APIs, documentation
- `quality-security-orchestrator` - Security scans, code review (MANDATORY PHASE 3)
- `docs-orchestrator` - Documentation generation (MANDATORY PHASE 4)

**🎯 Domain Orchestrators:**
- `dev-architecture-orchestrator` - General development, architecture
- `infrastructure-ops-orchestrator` - Docker, cloud, CI/CD, deployment
- `data-ai-orchestrator` - ML, data processing, AI development
- `language-specialist-orchestrator` - Language-specific coordination
- `business-marketing-orchestrator` - Business, marketing, sales
- `seo-content-orchestrator` - SEO optimization, content strategy
- `specialized-domains-orchestrator` - Finance, legal, specialized domains

**🎯 Power Agents (75+ Specialists):**
Available through orchestrators for specific tasks:
- **Languages**: typescript-pro, javascript-pro, python-pro, golang-pro, java-pro, csharp-pro, rust-pro, cpp-pro, c-pro, php-pro, ruby-pro, elixir-pro, scala-pro, sql-pro, flutter-expert, ios-developer, unity-developer, minecraft-bukkit-pro
- **Architecture**: backend-architect, frontend-developer, mobile-developer, ui-ux-designer, graphql-architect, architect-review
- **Data & AI**: ai-engineer, ml-engineer, mlops-engineer, data-scientist, data-engineer, prompt-engineer
- **Infrastructure**: cloud-architect, kubernetes-architect, terraform-specialist, hybrid-cloud-architect, database-admin, database-optimizer, deployment-engineer, dx-optimizer, network-engineer, devops-troubleshooter, incident-responder
- **Quality**: security-auditor, code-reviewer, test-automator, performance-engineer, debugger, error-detective, search-specialist
- **Documentation**: docs-architect, api-documenter, tutorial-engineer, reference-builder, mermaid-expert
- **Business**: business-analyst, customer-support, sales-automator, legal-advisor, content-marketer, hr-pro
- **SEO**: seo-authority-builder, seo-structure-architect, seo-meta-optimizer, seo-cannibalization-detector, seo-content-refresher, seo-keyword-strategist, seo-content-planner, seo-content-writer, seo-content-auditor, seo-snippet-hunter
- **Specialized**: quant-analyst, risk-manager, payment-integration, legacy-modernizer

### Agent Delegation Rules
1. **NEVER** call power agents directly - use orchestrators
2. **ALWAYS** use master-developer-orchestrator as entry point
3. Orchestrators delegate to appropriate power agents automatically
4. Context is preserved through context-manager
5. Progress tracked through claude-md-manager
6. All changes committed through git-manager

### DO NOT USE Individual Agents Directly
Never bypass the master-developer-orchestrator to use individual agents.
Always let the orchestrator handle delegation to power agents.

## Project Overview

A Python-based Truth and Dare API that provides questions and challenges for the classic party game.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI 0.116.1 (latest stable)
- **Web Server**: Uvicorn (ASGI server)
- **Validation**: Pydantic v2 (included in FastAPI)
- **Testing**: pytest, httpx
- **Code Quality**: Black, Ruff, MyPy
- **Data Storage**: JSON files (in-memory caching)
- **Type**: REST API
- **Key Dependencies**:
  - `fastapi[standard]` - Full FastAPI with all standard dependencies
  - `uvicorn[standard]` - Production ASGI server
  - `pytest` - Testing framework
  - `httpx` - Async HTTP client for testing

## Current Sprint

- **Goal**: Complete Truth and Dare API development (18 tasks across 6 phases)
- **Progress**: 0%
- **Status**: Ready to Start
- **Current Phase**: Phase 1 - Project Setup
- **Tasks**:
  
### Phase 1: Project Setup (0/3 completed)
- [ ] **TASK-001**: Project Initialization (P0, 2 points)
  - Create virtual environment with Python 3.11+
  - Initialize project directory structure
  - Create basic `__init__.py` files
  - Set up `.gitignore` for Python projects
  - Create `.env.example` with configuration templates
- [ ] **TASK-002**: Dependencies Installation and Configuration (P0, 1 point)  
  - Create `requirements.txt` with production dependencies
  - Create `requirements-dev.txt` with development dependencies
  - Install FastAPI, Uvicorn, Pydantic, and testing frameworks
  - Verify all dependencies install correctly
- [ ] **TASK-003**: Core Configuration Setup (P0, 2 points)
  - Implement `app/core/config.py` with Pydantic Settings
  - Create custom exception classes
  - Set up basic logging configuration
  - Create environment variable templates

### Phase 2: Data Layer Implementation (0/2 completed)
- [ ] **TASK-004**: JSON Data Files Creation (P0, 2 points)
  - Create `app/data/truths.json` with 50+ truth questions
  - Create `app/data/dares.json` with 50+ dare challenges
  - Implement proper JSON structure according to data model
  - Include all required categories and difficulty levels
- [ ] **TASK-005**: Data Loading and Caching System (P0, 3 points)
  - Implement `app/utils/data_loader.py` with caching functionality
  - Create `DataCache` class for managing loaded data
  - Implement data filtering methods
  - Add error handling for file loading failures

### Phase 3: Business Logic Implementation (0/3 completed)
- [ ] **TASK-006**: Truth Service Implementation (P1, 2 points)
  - Create `app/services/truth_service.py`
  - Implement `get_random_truth()` and `get_truth_by_category()` methods
  - Add input validation for categories
- [ ] **TASK-007**: Dare Service Implementation (P1, 2 points)
  - Create `app/services/dare_service.py`
  - Implement `get_random_dare()` and `get_dare_by_difficulty()` methods
  - Add input validation for difficulty levels
- [ ] **TASK-008**: Game Service Implementation (P1, 1 point)
  - Create game service for random truth/dare selection
  - Implement 50/50 random selection logic

### Phase 4: API Layer Implementation (0/3 completed)
- [ ] **TASK-009**: Pydantic Response Models (P1, 2 points)
  - Implement `app/models/responses.py` with all response models
  - Create `TruthResponse`, `DareResponse`, `GameResponse` models
  - Implement enum classes for categories and difficulties
- [ ] **TASK-010**: API Route Handlers (P1, 3 points)
  - Create route handlers for all endpoints
  - Implement proper HTTP status codes
  - Add OpenAPI documentation tags
- [ ] **TASK-011**: FastAPI Application Setup (P1, 2 points)
  - Implement `app/main.py` as application entry point
  - Register all routers with proper prefixes
  - Configure CORS middleware and exception handlers

### Phase 5: Testing Implementation (0/4 completed)
- [ ] **TASK-012**: Unit Tests for Services (P1, 3 points)
  - Create unit tests for all service layer functions
  - Test edge cases and error conditions
  - Achieve 95%+ coverage for service layer
- [ ] **TASK-013**: Integration Tests for API Endpoints (P1, 3 points)
  - Create integration tests for all API endpoints
  - Test error scenarios and response formats
  - Achieve 90%+ coverage for route handlers
- [ ] **TASK-014**: Edge Case and Error Handling Tests (P1, 2 points)
  - Test file loading failures and edge cases
  - Test concurrent request handling
- [ ] **TASK-015**: Performance and Load Testing (P2, 2 points)
  - Create performance test suite
  - Test response time requirements (< 200ms)
  - Test concurrent request handling (1000 requests)

### Phase 6: Documentation and Quality (0/3 completed)
- [ ] **TASK-016**: API Documentation Enhancement (P2, 2 points)
  - Add comprehensive endpoint descriptions
  - Include request/response examples
  - Document all error codes and responses
- [ ] **TASK-017**: Code Quality and Linting Setup (P2, 1 point)
  - Configure Black, Ruff, and MyPy
  - Create pre-commit hooks
  - Document code quality standards
- [ ] **TASK-018**: README and Development Documentation (P2, 2 points)
  - Create detailed README.md with setup instructions
  - Document API endpoints with examples
  - Add development setup guide

### Recent Updates
- **2025-09-03T01:00:00Z**: claude-md-manager - Updated technology stack with FastAPI 0.116.1 research findings from mcp-orchestrator
- **2025-09-03T00:00:00Z**: claude-md-manager - Imported 18 tasks from .claude/specs/truth-dare-api/tasks.md and created comprehensive sprint plan

## Progress Tracking

### Completed Features
- [x] Project specification generation (2025-09-03, spec-planner)

### In Progress
- [ ] Project setup and initialization (0% complete)

### Next Actions
1. Start with TASK-001: Project Initialization
2. Use master-developer-orchestrator for all implementation tasks
3. Follow sequential task order through the 6 phases

## Getting Started

This is a new Python project implementing the Truth and Dare API based on the generated specifications.

## Development Setup

### Prerequisites
- Python 3.11 or higher (recommended: Python 3.12)
- pip (Python package manager)
- Virtual environment support

### Installation
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies (after requirements.txt is created)
pip install -r requirements.txt

# For development dependencies
pip install -r requirements-dev.txt
```

### Python Environment Details
- **Minimum Python Version**: 3.11 (for modern type hints and performance)
- **Recommended Python Version**: 3.12 (latest stable with performance improvements)
- **Virtual Environment**: Required to isolate project dependencies
- **Package Manager**: pip with requirements.txt for dependency management

## Project Structure

Based on the specifications, the final project structure will be:

```
truth-dare-api/
├── app/                    # Main application directory
│   ├── __init__.py
│   ├── main.py            # Entry point for the API
│   ├── models/            # Pydantic response models
│   │   └── responses.py   # API response models
│   ├── routes/            # API endpoints
│   │   ├── truth.py       # Truth endpoints
│   │   ├── dare.py        # Dare endpoints
│   │   └── game.py        # Game and health endpoints
│   ├── services/          # Business logic
│   │   ├── truth_service.py
│   │   ├── dare_service.py
│   │   └── game_service.py
│   ├── data/              # Static data (truths and dares)
│   │   ├── truths.json
│   │   └── dares.json
│   ├── core/              # Core configuration
│   │   ├── config.py      # Pydantic Settings
│   │   └── exceptions.py  # Custom exceptions
│   └── utils/             # Utilities
│       └── data_loader.py # Data loading and caching
├── tests/                  # Test files
│   ├── test_truth_service.py
│   ├── test_dare_service.py
│   ├── test_data_loader.py
│   └── test_api_endpoints.py
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

## Architecture Decisions

### Framework Selection
- **FastAPI**: Chosen for modern async support, automatic OpenAPI documentation, and excellent performance
- **Pydantic v2**: Used for data validation and serialization with type hints
- **Uvicorn**: ASGI server for production-ready performance

### Data Storage Strategy
- **JSON Files**: Static files for truth and dare content (50+ items each)
- **In-Memory Caching**: Python dictionaries for fast access and filtering
- **Categories**: general, relationships, funny, deep, embarrassing (for truths)
- **Difficulty Levels**: easy, medium, hard (for dares)

### API Design Patterns
- **RESTful Endpoints**: Standard HTTP methods and resource-based URLs
- **Consistent Response Format**: Standardized JSON structure across all endpoints
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Documentation**: Auto-generated OpenAPI/Swagger documentation

### Security Considerations
- **Input Validation**: Pydantic models for request/response validation
- **CORS Configuration**: Proper cross-origin resource sharing setup
- **Error Handling**: Secure error messages without sensitive information exposure
- **Type Safety**: MyPy type checking for runtime safety

## Security Scan Results
- **Last Scan**: 2025-09-03T17:30:00Z
- **Status**: PASSED ✅
- **Critical Issues**: 0 (Fixed: 0)
- **High Issues**: 0 (Fixed: 0)
- **Medium Issues**: 0 (Fixed: 0)
- **Low Issues**: 0 (Fixed: 0)
- **Files Scanned**: 7 application files
- **Test Coverage**: 84.49% (71 tests passing)
- **Security Tools**: Semgrep, Manual FastAPI security review
- **Vulnerabilities Fixed**: None found

### Security Assessment Summary
- **Input Validation**: ✅ Secure (Pydantic models with comprehensive validation)
- **Path Parameters**: ✅ Secure (Regex validation prevents injection)
- **CORS Configuration**: ✅ Secure (Properly configured origins)
- **Error Handling**: ✅ Secure (No stack traces exposed)
- **Data Sanitization**: ✅ Secure (UTF-8 encoding, path validation)
- **HTTP Status Codes**: ✅ Secure (Proper status codes used)
- **Logging**: ✅ Secure (No sensitive data exposed)

### Production Recommendations
- Add rate limiting for production deployment
- Implement security headers middleware (HSTS, CSP)
- Update Pydantic validators to V2 style
- Consider API authentication for production use

## External Research Findings

### FastAPI 0.116.1 Documentation Research
- **Source**: Official FastAPI documentation and release notes
- **Latest Version**: FastAPI 0.116.1 (current stable release)
- **Key Features**:
  - New FastAPI CLI (`fastapi dev`, `fastapi run`) for simplified development
  - Enhanced performance with Pydantic v2 integration
  - Built-in support for modern Python type hints
  - Automatic OpenAPI/Swagger documentation generation
  - Native async/await support for high performance

### Recommended Dependencies and Versions
- **FastAPI**: `fastapi[standard]>=0.116.1` - Includes all standard dependencies
- **Uvicorn**: `uvicorn[standard]>=0.30.0` - Production ASGI server
- **Pytest**: `pytest>=8.0.0` - Modern testing framework
- **HTTPX**: `httpx>=0.27.0` - Async HTTP client for testing
- **Pydantic**: Included with FastAPI (v2 compatibility)

### Modern Project Structure Recommendations
- **FastAPI CLI**: Use new `fastapi dev` and `fastapi run` commands
- **Dependency Management**: Use `fastapi[standard]` to get all standard dependencies
- **Type Safety**: Leverage Python 3.11+ type hints with FastAPI's automatic validation
- **Documentation**: FastAPI automatically generates OpenAPI/Swagger docs at `/docs` and `/redoc`
- **Performance**: FastAPI with Uvicorn provides excellent async performance for API responses

## API Design Considerations

### Planned Endpoints
- `GET /api/v1/truth` - Get a random truth question
- `GET /api/v1/truth/{category}` - Get truth by category
- `GET /api/v1/dare` - Get a random dare challenge
- `GET /api/v1/dare/{difficulty}` - Get dare by difficulty level
- `GET /api/v1/game/random` - Get random truth or dare
- `GET /api/v1/health` - Health check endpoint

### Response Format
Consistent JSON response structure:
```json
{
  "type": "truth|dare",
  "content": "Question or challenge text",
  "category": "optional category",
  "difficulty": "easy|medium|hard",
  "id": "unique identifier"
}
```

## Development Commands

### Modern FastAPI CLI Commands (FastAPI 0.116.1+)
```bash
# Development server (recommended - new FastAPI CLI)
fastapi dev app/main.py

# Production server (new FastAPI CLI)
fastapi run app/main.py

# Traditional uvicorn commands (still supported)
uvicorn app.main:app --reload
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Testing
pytest
pytest --cov=app --cov-report=html

# Code formatting
black .

# Linting
ruff check .
ruff check . --fix

# Type checking
mypy app/
```

## Performance Requirements

Based on specifications:
- **Response Time**: < 200ms for all endpoints
- **Concurrent Requests**: Handle 1000 concurrent requests
- **Memory Usage**: < 50MB
- **Success Rate**: 99.9% under load

## Testing Strategy

### Coverage Targets
- **Service Layer**: 95%+ coverage
- **Route Handlers**: 90%+ coverage
- **Overall Project**: 90%+ coverage

### Testing Frameworks
- **pytest**: Primary testing framework
- **httpx**: Async HTTP client for API testing
- **pytest-asyncio**: Async test support

## Spec Tasks

### Task Status Mapping
All 18 tasks from `.claude/specs/truth-dare-api/tasks.md`:

**Phase 1 - Project Setup (0/3)**:
- [ ] TASK-001: Project Initialization
- [ ] TASK-002: Dependencies Installation
- [ ] TASK-003: Core Configuration Setup

**Phase 2 - Data Layer (0/2)**:
- [ ] TASK-004: JSON Data Files Creation
- [ ] TASK-005: Data Loading and Caching System

**Phase 3 - Business Logic (0/3)**:
- [ ] TASK-006: Truth Service Implementation
- [ ] TASK-007: Dare Service Implementation
- [ ] TASK-008: Game Service Implementation

**Phase 4 - API Layer (0/3)**:
- [ ] TASK-009: Pydantic Response Models
- [ ] TASK-010: API Route Handlers
- [ ] TASK-011: FastAPI Application Setup

**Phase 5 - Testing (0/4)**:
- [ ] TASK-012: Unit Tests for Services
- [ ] TASK-013: Integration Tests for API Endpoints
- [ ] TASK-014: Edge Case and Error Handling Tests
- [ ] TASK-015: Performance and Load Testing

**Phase 6 - Documentation (0/3)**:
- [ ] TASK-016: API Documentation Enhancement
- [ ] TASK-017: Code Quality and Linting Setup
- [ ] TASK-018: README and Development Documentation

## Context Mapping

Integration with context manager files:
- **Current Context**: Will sync with `.claude/context/current-context.json`
- **Agent Memory**: Will sync with `.claude/context/agent-memory.json`  
- **Decisions Log**: Will sync with `.claude/context/decisions-log.md`

## Important Context for AI Assistants

### Critical Information
- **Task Dependencies**: Follow sequential order - each task builds on previous ones
- **Priority Levels**: P0 tasks must be completed before P1 tasks
- **Phase Gates**: Complete all tasks in a phase before moving to next phase
- **Testing Requirements**: High coverage targets must be met (90-95%)

### Code Conventions
- **Naming**: Snake_case for files, PascalCase for classes, camelCase for JSON
- **File Organization**: Separate concerns (models, routes, services, utils)
- **Documentation**: Comprehensive docstrings and type hints
- **Error Handling**: Custom exceptions with proper HTTP status codes

### Known Issues and TODOs

### Known Issues
- [ ] No issues identified yet

### Technical Debt
- [ ] No technical debt identified yet

## Version History

### v0.1.0 - Initial Setup
- **Date**: 2025-09-03
- **Changes**: Project specification generated and imported into CLAUDE.md
- **Agent Used**: spec-planner → claude-md-manager
- **Security Scan**: Not yet performed
- **Tasks Completed**: Specification generation (1/18 total tasks)

---

**Last Updated**: 2025-09-03T00:00:00Z
**Updated By**: claude-md-manager