"""Background job endpoints using TaskIQ"""
from workers.tasks import step_one, independent_task


async def create_order_job(body):
    """Kick off an order processing job chain
    
    This endpoint starts a TaskIQ job chain:
    1. step_one: validates order
    2. step_two: processes payment (automatically kicked off by step_one)
    
    Args:
        body: Request body with order_id and user_name
        
    Returns:
        Tuple of (response data, status code)
    """
    order_id = body.get("order_id")
    user_name = body.get("user_name")
    
    # Kick off the first task in the chain
    # TaskIQ returns a TaskiqResult with a task_id
    task = await step_one.kiq(order_id=order_id, user_name=user_name)
    
    return {
        "message": "Order processing job chain started",
        "task_id": task.task_id,
        "order_id": order_id,
        "chain": ["step_one (validate)", "step_two (payment)"]
    }, 202


async def create_simple_job(body):
    """Kick off a simple independent job (not a chain)
    
    Args:
        body: Request body with message and repeat count
        
    Returns:
        Tuple of (response data, status code)
    """
    message = body.get("message", "test")
    repeat = body.get("repeat", 3)
    
    # Kick off independent task
    task = await independent_task.kiq(message=message, repeat=repeat)
    
    return {
        "message": "Job started",
        "task_id": task.task_id,
        "parameters": {
            "message": message,
            "repeat": repeat
        }
    }, 202
