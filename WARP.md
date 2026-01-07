# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Docker (Recommended)
- **Start services (detached)**: `make up`
- **Start services (foreground)**: `make run`
- **Stop services**: `make down`
- **View logs**: `make logs`
- **Rebuild**: `make build`
- **Run tests**: `make test`
- **Clean (remove volumes)**: `make clean`

### Local Development (without Docker)
- **Install dependencies**: `make install` or `uv sync --dev`
- **Run server with reload**: `make dev`
- **Run tests**: `make test-local` or `uv run pytest tests/ -v`
- **Run single test**: `uv run pytest tests/test_api.py::TestClassName::test_method_name -v`

### API Access
- Base URL: http://localhost:7878/api/v1
- Swagger UI: http://localhost:7878/api/v1/ui/

## Architecture

### Tech Stack
This is a **Connexion 3.x** pure **ASGI** API using **Python 3.13+** with Starlette backend (no Flask). All endpoints are async. The project uses **uv** for package management.

### Production Server
Run with uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4
```

### Worker Sizing for Production

**How many workers?**
- **Rule of thumb**: 1-2x CPU cores
- 2 vCPUs → 2-4 workers
- 4 vCPUs → 4-8 workers
- 8 vCPUs → 8-16 workers

**Why not more?**
- Each worker is a separate Python process with its own:
  - GIL (Global Interpreter Lock)
  - Event loop (handles many concurrent requests)
  - Memory footprint (~50-100MB per worker)
- One async worker can handle hundreds of concurrent connections

**Migrating from gunicorn with threads?**
- Old: 2 workers × 20 threads = 40 thread-based handlers
- New: 4 uvicorn workers = 4 event loops (each handles 100s of concurrent requests)
- Start with **workers = 2x your old worker count**
- Monitor CPU (target 70-80% under load) and tune

**Important**: Workers share nothing in memory. Use external state (Redis, database) for shared data.

### OpenAPI-First Design
All endpoints are defined in `specs/swagger.yaml` using OpenAPI 3.0 specification. Connexion automatically routes requests to Python functions based on the `operationId` field in the spec (e.g., `operationId: api.users.get_users` routes to the `get_users()` function in `api/users.py`).

### Application Setup (app.py)
The app uses `connexion.AsyncApp` (pure ASGI):
1. Creates a `connexion.AsyncApp` instance with `specification_dir` pointing to specs/
2. Adds API spec via `add_api('swagger.yaml', base_path='/api/v1')`
3. Uses Starlette as the ASGI backend (no Flask)
4. All API handlers in `api/` are async functions

### Testing Architecture
All test classes **must inherit from `BaseTestCase`** in `tests/base_test.py`. This base class:
- Extends `unittest.IsolatedAsyncioTestCase` for async test support
- Provides `self.client` (httpx AsyncClient) to all tests
- All test methods must be async and use `await` for client calls

When adding new tests, always extend `BaseTestCase` and make test methods async:
```python
async def test_example(self):
    response = await self.client.get('/api/v1/endpoint')
    self.assertEqual(response.status_code, 200)
```

### API Handler Pattern
API handlers in the `api/` directory are **async functions** that return a tuple of `(data, status_code)`:
```python
async def get_user(user_id):
    user = USERS_DB.get(user_id)
    if user:
        return user, 200
    return {"error": "User not found"}, 404
```

### State Management
This example uses in-memory storage (`USERS_DB` dictionary in `api/users.py`) for demonstration. In production, replace with a proper database.
