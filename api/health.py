"""Health check endpoints"""


def get_health():
    """Return health status of the service"""
    return {
        "status": "healthy",
        "message": "Service is running"
    }, 200
