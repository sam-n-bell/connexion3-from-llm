# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Development
- **Install dependencies**: `make install` or `uv sync --dev`
- **Run server**: `make run` (starts on http://localhost:7878)
- **Run tests**: `make test` or `uv run pytest tests/ -v`
- **Run single test**: `uv run pytest tests/test_api.py::TestClassName::test_method_name -v`

### API Access
- Base URL: http://localhost:7878/api/v1
- Swagger UI: http://localhost:7878/api/v1/ui/

## Architecture

### Tech Stack
This is a **Connexion 3.x** API using **ASGI** with Flask backend. Connexion 3.x is ASGI-first and requires an ASGI server. The project uses **uv** for package management.

### Production Server
Run with gunicorn + uvicorn workers:
```bash
gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --timeout 120 -b 0.0.0.0:7878 app:app
```

Or with uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4
```

### OpenAPI-First Design
All endpoints are defined in `specs/swagger.yaml` using OpenAPI 3.0 specification. Connexion automatically routes requests to Python functions based on the `operationId` field in the spec (e.g., `operationId: api.users.get_users` routes to the `get_users()` function in `api/users.py`).

### Application Setup (app.py)
The app uses `connexion.App` (ASGI) with Flask backend:
1. Creates a `connexion.App` instance with `specification_dir` pointing to specs/
2. Adds API spec via `add_api('swagger.yaml', base_path='/api/v1')`
3. The underlying Flask app is accessible via `app.app`
4. ASGI middleware handles routing and request processing

### Testing Architecture
All test classes **must inherit from `BaseTestCase`** in `tests/base_test.py`. This base class:
- Gets the underlying Flask app from the Connexion App in `setUpClass()`
- Provides `self.client` (Flask test client) to all tests
- Uses Flask's test client for synchronous testing

When adding new tests, always extend `BaseTestCase` and use `self.client` for requests.

### API Handler Pattern
API handlers in the `api/` directory return a tuple of `(data, status_code)`:
```python
def get_user(user_id):
    user = USERS_DB.get(user_id)
    if user:
        return user, 200
    return {"error": "User not found"}, 404
```

### State Management
This example uses in-memory storage (`USERS_DB` dictionary in `api/users.py`) for demonstration. In production, replace with a proper database.
