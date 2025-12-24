# Connexion 3.x Flask WSGI Example

This is a complete example of a Flask API using Connexion 3.x with WSGI (not ASGI), including a full test suite with a base test class that all tests inherit from.

## Project Structure

```
connexion-flask-example/
├── app.py              # Main Flask application
├── api/                # API endpoint handlers
│   ├── __init__.py
│   ├── health.py       # Health check endpoint
│   └── users.py        # User management endpoints
├── specs/              # OpenAPI/Swagger specifications
│   └── swagger.yaml    # API specification
├── tests/              # Test suite
│   ├── __init__.py
│   ├── base_test.py    # Base test case (inherited by all tests)
│   └── test_api.py     # API endpoint tests
├── pyproject.toml      # Project dependencies (uv)
├── Makefile            # Make commands
└── README.md           # This file
```

## Setup

Install dependencies using uv:

```bash
make install
```

Or manually:

```bash
uv sync --dev
```

## Running the API

To launch the Flask API server:

```bash
make run
```

The API will be available at:
- Base URL: `http://localhost:7878`
- API endpoints: `http://localhost:7878/api/v1/...`
- Swagger UI: `http://localhost:7878/api/v1/ui/`

## Available Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/users` - Get all users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user

## Running Tests

Run all tests:

```bash
make test
```

Or manually:

```bash
uv run pytest tests/ -v
```

## Test Structure

All test classes inherit from `BaseTestCase` in `tests/base_test.py`, which:
- Creates a Connexion FlaskApp instance
- Registers all endpoints from the Swagger spec
- Provides a test client (`self.client`) to all test classes
- Uses Flask's WSGI test client (not async)

Example test class:

```python
from tests.base_test import BaseTestCase

class TestMyEndpoint(BaseTestCase):
    def test_something(self):
        response = self.client.get('/api/v1/endpoint')
        self.assertEqual(response.status_code, 200)
```

## Key Features

- **Connexion 3.x with Flask/WSGI**: Uses `FlaskApp` for WSGI compatibility (not AsyncApp)
- **OpenAPI Specification**: All endpoints defined in `specs/swagger.yaml`
- **Base Test Class**: All tests inherit from `BaseTestCase` for consistent test client setup
- **Non-async Tests**: All tests use standard unittest and Flask's WSGI test client
- **uv Package Manager**: Fast, modern Python package management

## Example API Usage

### Health Check
```bash
curl http://localhost:7878/api/v1/health
```

### Get All Users
```bash
curl http://localhost:7878/api/v1/users
```

### Create User
```bash
curl -X POST http://localhost:7878/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'
```

### Get Specific User
```bash
curl http://localhost:7878/api/v1/users/1
```
