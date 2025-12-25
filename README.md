# Connexion 3.x Pure ASGI Example

This is a complete example of a pure ASGI API using Connexion 3.x with Python 3.13+, including a full async test suite with a base test class that all tests inherit from.

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
Run with uvicorn:

```bash
uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4
```

**Worker Sizing:**
- Use **1-2x CPU cores** as a starting point
- Each worker is a separate process with its own event loop
- One worker can handle hundreds of concurrent async requests
- Monitor CPU usage (target 70-80%) and adjust

**Example:**
- 2 vCPUs → `--workers 2` or `--workers 4`
- 4 vCPUs → `--workers 4` or `--workers 8`

**Important:** Workers don't share memory. Use Redis/database for shared state.

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
- Uses `unittest.IsolatedAsyncioTestCase` for async test support
- Provides an async httpx test client (`self.client`)
- All test methods must be async

Example test class:

```python
from tests.base_test import BaseTestCase

class TestMyEndpoint(BaseTestCase):
    async def test_something(self):
        response = await self.client.get('/api/v1/endpoint')
        self.assertEqual(response.status_code, 200)
```

## Key Features

- **Python 3.13+**: Uses the latest Python version with native async support
- **Pure ASGI**: Uses `connexion.AsyncApp` with Starlette backend (no Flask)
- **Async Handlers**: All API endpoints are async functions
- **OpenAPI Specification**: All endpoints defined in `specs/swagger.yaml`
- **Production Ready**: Uses uvicorn with multiple workers for production deployment
- **Async Tests**: All tests are async using `IsolatedAsyncioTestCase`
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
