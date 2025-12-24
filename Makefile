.PHONY: run test install

run:
	uv run python app.py

test:
	uv run pytest tests/ -v

install:
	uv sync --dev
