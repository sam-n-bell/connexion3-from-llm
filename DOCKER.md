# Docker Deployment

## Quick Start

### Build and run with docker-compose:
```bash
docker-compose up --build
```

The application will be available at:
- API: http://localhost:7878/api/v1/
- Swagger UI: http://localhost:7878/api/v1/ui/
- Health: http://localhost:7878/api/v1/health

### Test the SVG endpoint:

**With cache (default):**
```bash
curl -I http://localhost:7878/api/v1/svg
# Check X-Cache-Hit header (first request: false, subsequent: true)
```

**Without cache:**
```bash
curl -I "http://localhost:7878/api/v1/svg?useCache=false"
# X-Cache-Hit header will always be: false
```

**View the SVG:**
```bash
open http://localhost:7878/api/v1/svg
# Or visit in browser
```

## Services

### App Container
- **Image**: Custom Python 3.13 with uv
- **Port**: 7878
- **Workers**: 4 uvicorn workers
- **Dependencies**: Redis

### Redis Container
- **Image**: redis:7-alpine
- **Port**: 6379
- **Persistence**: Volume mounted at `/data`

## Useful Commands

### Stop services:
```bash
docker-compose down
```

### Stop and remove volumes:
```bash
docker-compose down -v
```

### View logs:
```bash
docker-compose logs -f app
docker-compose logs -f redis
```

### Rebuild without cache:
```bash
docker-compose build --no-cache
docker-compose up
```

### Check health:
```bash
docker-compose ps
```

### Execute command in running container:
```bash
docker-compose exec app python -c "from api.svg import generate_svg_content; print(len(generate_svg_content()))"
```

### Connect to Redis CLI:
```bash
docker-compose exec redis redis-cli
# Then check cache:
KEYS *
GET svg:complex:v1
```

## Environment Variables

You can override these in `docker-compose.yml` or via `.env` file:

- `REDIS_HOST` - Redis hostname (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)

## Production Deployment

For production, consider:

1. **Worker count**: Adjust based on CPU cores
   ```yaml
   command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7878", "--workers", "8"]
   ```

2. **Resource limits**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 1G
       reservations:
         cpus: '1'
         memory: 512M
   ```

3. **Redis persistence**: Already configured with volume

4. **Secrets**: Use Docker secrets or environment variables

5. **Reverse proxy**: Add nginx/traefik for SSL/load balancing

## Troubleshooting

### Redis connection errors:
```bash
# Check if Redis is healthy
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test connection from app
docker-compose exec app python -c "from redis.asyncio import Redis; import asyncio; asyncio.run(Redis(host='redis').ping())"
```

### App not starting:
```bash
# Check logs
docker-compose logs app

# Check health endpoint
curl http://localhost:7878/api/v1/health
```
