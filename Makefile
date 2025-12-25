.PHONY: run test install

run:
	uv run uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4

test:
	uv run pytest tests/ -v

install:
	uv sync --dev
