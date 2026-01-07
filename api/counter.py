"""Counter endpoint demonstrating async handler calling sync Redis function"""
import asyncio
import redis


# Sync Redis client (not async!)
_sync_redis_client = None


def get_sync_redis():
    """Get or create sync Redis client"""
    global _sync_redis_client
    if _sync_redis_client is None:
        _sync_redis_client = redis.Redis(
            host='redis',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
    return _sync_redis_client


def increment_counter_sync():
    """Sync function that does Redis I/O
    
    This is a SYNC function that performs blocking I/O with Redis.
    It can be called from async code using asyncio.to_thread().
    """
    client = get_sync_redis()
    
    # This is blocking I/O in a sync function
    counter = client.incr('counter:demo')
    
    return counter


async def get_counter():
    """Async handler that awaits a sync function doing Redis I/O
    
    This demonstrates running sync I/O code in a thread pool so it can
    be awaited from async code without blocking the event loop.
    
    Returns:
        Tuple of (response data, status code)
    """
    # Run the sync function in a thread pool and await it
    counter_value = await asyncio.to_thread(increment_counter_sync)
    
    return {
        "counter": counter_value,
        "method": "async handler -> sync function (via asyncio.to_thread)"
    }, 200
