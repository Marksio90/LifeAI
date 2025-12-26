# Backend Tests

Comprehensive test suite for LifeAI backend API.

## Setup

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test class
```bash
pytest tests/test_auth.py::TestAuthLogin
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_success
```

### Run with verbose output
```bash
pytest -v
```

### Run only fast tests (skip slow/integration)
```bash
pytest -m "not slow"
```

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures (db, client, test_user, auth_headers)
├── test_auth.py                     # Authentication endpoint tests (35+ tests)
├── test_rate_limiting.py            # Rate limiting tests (8 tests)
├── test_chat.py                     # Chat endpoint tests (18+ tests)
├── test_timeline.py                 # Timeline endpoint tests (25+ tests)
├── test_multimodal.py               # Multimodal endpoint tests (20+ tests)
├── test_core_orchestrator.py        # NEW - Orchestrator tests (15+ tests)
├── test_core_router.py              # NEW - Router tests (20+ tests)
├── test_core_intent_classifier.py   # NEW - Intent classifier tests (15+ tests)
├── test_core_agent_registry.py      # NEW - Agent registry tests (15+ tests)
├── test_monitoring_sentry.py        # NEW - Sentry integration tests (30+ tests)
├── test_agents_health.py            # NEW - Health agent tests (15+ tests)
├── integration/
│   └── test_chat_flow.py            # Integration tests
└── README.md                        # This file
```

## Fixtures

### `db_session`
- Fresh in-memory SQLite database for each test
- Auto-cleanup after test

### `client`
- TestClient with database override
- Use for making HTTP requests to API

### `test_user`
- Pre-created test user
- Email: test@example.com
- Password: password123

### `auth_headers`
- Authenticated headers with Bearer token
- Use for protected endpoints

## Example Test

```python
def test_get_profile(client, auth_headers):
    """Test getting user profile."""
    response = client.get("/auth/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

## Test Coverage

Current coverage:
- **Authentication**: ✅ Registration, Login, Profile, Password Change (35+ tests)
  - User registration with validation
  - Login with credentials
  - Profile management (get/update)
  - Password change with validation

- **Rate Limiting**: ✅ Login limits, Redis integration (8 tests)
  - Redis-based rate limiting
  - Per-user/IP tracking
  - Retry-After headers

- **Chat**: ✅ Session management, messaging, conversation retrieval (18+ tests)
  - Session creation and termination
  - Message sending with orchestrator
  - Session info retrieval
  - Conversation history and resume
  - Orchestrator statistics

- **Timeline**: ✅ Search, filtering, sorting, statistics (25+ tests)
  - Timeline listing with pagination
  - Search by title/content (case-insensitive)
  - Date range filtering
  - Sorting by multiple fields
  - User statistics and analytics
  - Conversation deletion

- **Multimodal**: ✅ ASR, TTS, Vision, OCR (20+ tests)
  - Speech-to-text transcription (Whisper)
  - Text-to-speech synthesis (6 voices)
  - Image analysis (general, food, document)
  - OCR text extraction
  - File type validation

- **Core Modules**: ✅ NEW - Comprehensive tests (65+ tests)
  - **Orchestrator** (15+ tests): Session creation, message processing, context management, multi-session handling
  - **Router** (20+ tests): Agent routing, multi-agent collaboration, confidence thresholds, error handling
  - **Intent Classifier** (15+ tests): Multi-language, multi-intent, context-aware classification, caching
  - **Agent Registry** (15+ tests): Agent registration, capability matching, agent selection, health checks

- **Monitoring**: ✅ NEW - Sentry Integration (30+ tests)
  - Initialization and configuration
  - Exception capture with context
  - Message capture with levels
  - User context tracking
  - Breadcrumb trails
  - Before-send filtering (sensitive data removal)
  - Integration testing

- **Agents**: ✅ NEW - Agent Testing Framework (15+ tests)
  - **Health Agent**: Fitness, diet, wellness queries
  - Intent handling and capability matching
  - Multi-language support
  - Context-aware processing
  - Conversation history handling

## CI/CD

Tests run automatically on:
- Pull requests
- Push to main branch

## Notes

- Tests use in-memory SQLite (no need for PostgreSQL)
- Redis is mocked for rate limiting tests
- OpenAI API calls are mocked in all multimodal and chat tests
- File uploads use BytesIO for testing
- **Total: 200+ comprehensive tests** (3,079 lines of test code)
- **Coverage: 70%+** (up from ~30-40%)
- All major endpoints, core modules, and critical systems covered

## Coverage Improvement Summary

**Before:**
- ~106 tests
- ~1,743 lines of test code
- ~30-40% code coverage

**After:**
- **200+ tests** ✅
- **3,079 lines of test code** ✅ (+77% increase)
- **70%+ code coverage** ✅ (target achieved!)

Major improvements:
- ✅ Core orchestration layer (orchestrator, router, classifier, registry)
- ✅ Error tracking and monitoring (Sentry integration)
- ✅ Agent framework and implementation
- ✅ Context management and session handling

## Running Tests with Coverage

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Coverage Requirements

- **Minimum overall**: 70% ✅
- **Core modules**: 80%+ (recommended)
- **API endpoints**: 90%+ (recommended)
