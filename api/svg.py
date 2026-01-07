"""SVG generation endpoints with Redis caching"""
import random
from redis.asyncio import Redis

# Redis connection pool
_redis_client = None


async def get_redis():
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host='redis',
            port=6379,
            decode_responses=False,  # We're storing bytes
            socket_connect_timeout=5
        )
    return _redis_client


def generate_svg_content():
    """Generate SVG with 1000 mixed elements (polygons and text)"""
    random.seed(42)  # Consistent output for caching demo
    
    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">'
    ]
    
    # Generate 500 polygons
    for i in range(500):
        x = random.randint(0, 950)
        y = random.randint(0, 950)
        points = []
        for _ in range(random.randint(3, 6)):
            px = x + random.randint(-50, 50)
            py = y + random.randint(-50, 50)
            points.append(f"{px},{py}")
        
        color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        opacity = random.uniform(0.3, 0.9)
        
        svg_parts.append(
            f'<polygon points="{" ".join(points)}" '
            f'fill="{color}" opacity="{opacity:.2f}" '
            f'stroke="black" stroke-width="0.5"/>'
        )
    
    # Generate 500 text elements
    words = ["Python", "ASGI", "Redis", "Uvicorn", "Docker", "Cache", "Fast", "Async"]
    for i in range(500):
        x = random.randint(10, 950)
        y = random.randint(20, 980)
        size = random.randint(8, 24)
        color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
        word = random.choice(words)
        
        svg_parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" opacity="0.7">{word}</text>'
        )
    
    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


async def get_svg(useCache: bool = True):
    """Generate or retrieve cached SVG with 1000 elements
    
    Args:
        useCache: Whether to use Redis cache (default: True)
    
    Returns:
        Tuple of (SVG content, status code, headers)
    """
    cache_key = "svg:complex:v1"
    
    svg_content = None
    from_cache = False
    
    # Try to get from cache if enabled
    if useCache:
        try:
            redis = await get_redis()
            cached = await redis.get(cache_key)
            if cached:
                svg_content = cached.decode('utf-8')
                from_cache = True
        except Exception as e:
            # Cache miss or Redis unavailable, continue to generate
            print(f"Redis error: {e}")
    
    # Generate if not cached or cache disabled
    if svg_content is None:
        svg_content = generate_svg_content()
        
        # Store in cache if enabled
        if useCache:
            try:
                redis = await get_redis()
                await redis.setex(cache_key, 3600, svg_content.encode('utf-8'))  # 1 hour TTL
            except Exception as e:
                print(f"Redis cache write error: {e}")
    
    # Return SVG with appropriate headers
    headers = {
        'Content-Type': 'image/svg+xml',
        'X-Cache-Hit': 'true' if from_cache else 'false',
        'Cache-Control': 'public, max-age=3600' if useCache else 'no-cache'
    }
    
    return svg_content, 200, headers
