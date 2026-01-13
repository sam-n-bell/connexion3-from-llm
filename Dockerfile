# Dockerfile for Connexion ASGI app with Python 3.14
FROM python:3.14-slim

# Install uv (pinned version for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Create non-root user with home directory
RUN groupadd -r appuser && \
    useradd -r -g appuser -m -d /home/appuser appuser && \
    mkdir -p /home/appuser/.cache && \
    chown -R appuser:appuser /home/appuser

# Copy dependency files and install with cache mount
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen

# Copy entrypoint script (changes less frequently than app code)
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Copy application code (most frequently changing)
COPY app.py ./
COPY api/ ./api/
COPY workers/ ./workers/
COPY db/ ./db/
COPY specs/ ./specs/

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 7878

# Use entrypoint script to determine what to run
ENTRYPOINT ["./entrypoint.sh"]
