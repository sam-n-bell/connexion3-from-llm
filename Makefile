.PHONY: run test install

run:
	uv run gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --timeout 120 -b 0.0.0.0:7878 app:app

test:
	uv run pytest tests/ -v

install:
	uv sync --dev
