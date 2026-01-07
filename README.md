# Connexion 3.x Pure ASGI Example

This is a complete example of a pure ASGI API using Connexion 3.x with Python 3.13+, including a full async test suite with a base test class that all tests inherit from.

## Project Structure

```
connexion-flask-example/
├── app.py              # Main ASGI application
├── api/                # API endpoint handlers
│   ├── __init__.py
│   ├── health.py       # Health check endpoint
│   ├── users.py        # User management endpoints
│   ├── counter.py      # Counter endpoint (async->sync demo)
│   └── jobs.py         # Background job endpoints (TaskIQ)
├── workers/            # TaskIQ background workers
│   ├── __init__.py
│   └── tasks.py        # Task definitions and broker
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

### Using Docker (Recommended)
Start all services (API + Worker + Redis) in detached mode:
```bash
make up
```

Start services in foreground (with logs):
```bash
make run
```

View logs:
```bash
make logs          # All services
make logs-app      # API only
make logs-worker   # Worker only
```

Stop services:
```bash
make down
```

### Local Development (without Docker)
For local development with hot reload:
```bash
make dev         # Start API server
make dev-worker  # Start TaskIQ worker (in separate terminal)
```

**Note:** You'll need Redis running locally for the worker:
```bash
redis-server
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

### Core
- `GET /api/v1/health` - Health check
- `GET /api/v1/users` - Get all users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user

### Background Jobs (TaskIQ)
- `POST /api/v1/jobs/order` - Start order processing job chain (step_one → step_two)
- `POST /api/v1/jobs/simple` - Start simple independent job

### Demo/Testing
- `GET /api/v1/counter` - Counter with async→sync pattern demo
- `GET /api/v1/svg` - SVG generation with Redis caching

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
- **TaskIQ Workers**: Fully async background job processing with job chaining
- **Redis Integration**: Caching and task queue backend
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

### Start Job Chain (TaskIQ)
```bash
curl -X POST http://localhost:7878/api/v1/jobs/order \
  -H "Content-Type: application/json" \
  -d '{"order_id": 12345, "user_name": "john_doe"}'
```

Response:
```json
{
  "message": "Order processing job chain started",
  "task_id": "abc123...",
  "order_id": 12345,
  "chain": ["step_one (validate)", "step_two (payment)"]
}
```

Watch the worker logs to see the chain execute:
```bash
make logs-worker
```

You'll see:
1. `[STEP 1]` - Order validation (2 second delay)
2. `[STEP 1]` - Kicks off step_two
3. `[STEP 2]` - Payment processing (1.5 second delay)
4. `[STEP 2]` - Completion

### Start Simple Job
```bash
curl -X POST http://localhost:7878/api/v1/jobs/simple \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "repeat": 5}'
```
