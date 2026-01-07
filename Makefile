.PHONY: build up down logs test clean

# Build Docker images
build:
	docker-compose build

# Start services in detached mode
up:
	docker-compose up -d

# Start services in foreground
run:
	docker-compose up

# Stop and remove containers
down:
	docker-compose down

# Stop and remove containers with volumes
clean:
	docker-compose down -v

# View logs
logs:
	docker-compose logs -f

# View worker logs only
logs-worker:
	docker-compose logs -f worker

# View app logs only
logs-app:
	docker-compose logs -f app

# Run tests (using docker-compose run with test dependencies)
test:
	docker-compose run --rm app sh -c "uv sync --dev && uv run pytest tests/ -v"

# Rebuild and restart
restart: down build up

# Local development with uv (without Docker)
dev:
	uv run uvicorn app:app --host 0.0.0.0 --port 7878 --reload

# Local worker development
dev-worker:
	uv run taskiq worker workers.tasks:broker --reload

test-local:
	uv run pytest tests/ -v

install:
	uv sync --dev
