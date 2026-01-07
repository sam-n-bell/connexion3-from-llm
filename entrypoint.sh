#!/bin/sh
set -e

# Check SERVICE_TYPE environment variable to determine what to run
if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting TaskIQ worker..."
    exec uv run taskiq worker workers.tasks:broker
else
    echo "Starting API server..."
    exec uvicorn app:app --host 0.0.0.0 --port 7878 --workers 4
fi
