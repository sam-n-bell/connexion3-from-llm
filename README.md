# Connexion 3.x Flask ASGI Example

This is a complete example of a Flask API using Connexion 3.x (ASGI-first), including a full test suite with a base test class that all tests inherit from.

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

### Development
To launch the development server:

```bash
make run
```

### Production
Run with gunicorn + uvicorn workers:

```bash
gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --timeout 120 -b 0.0.0.0:7878 app:app
```

Or with uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4
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
- Gets the underlying Flask app from the Connexion App
- Provides a test client (`self.client`) to all test classes
- Uses Flask's test client for synchronous testing

Example test class:

```python
from tests.base_test import BaseTestCase

class TestMyEndpoint(BaseTestCase):
    def test_something(self):
        response = self.client.get('/api/v1/endpoint')
        self.assertEqual(response.status_code, 200)
```

## Key Features

- **Connexion 3.x with ASGI**: Uses `connexion.App` (ASGI-first) with Flask backend
- **OpenAPI Specification**: All endpoints defined in `specs/swagger.yaml`
- **Production Ready**: Works with gunicorn + uvicorn workers for production deployment
- **Base Test Class**: All tests inherit from `BaseTestCase` for consistent test client setup
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
