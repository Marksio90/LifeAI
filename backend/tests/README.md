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
├── conftest.py              # Shared fixtures (db, client, test_user, auth_headers)
├── test_auth.py             # Authentication endpoint tests
├── test_rate_limiting.py    # Rate limiting tests
└── README.md                # This file
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
- Authentication: ✅ Registration, Login, Profile, Password Change
- Rate Limiting: ✅ Login limits, Redis integration
- Chat: ⏸️ TODO
- Timeline: ⏸️ TODO
- Multimodal: ⏸️ TODO

## CI/CD

Tests run automatically on:
- Pull requests
- Push to main branch

## Notes

- Tests use in-memory SQLite (no need for PostgreSQL)
- Redis is mocked for rate limiting tests
- OpenAI API calls should be mocked in tests (not yet implemented)
