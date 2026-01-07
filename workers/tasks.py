"""TaskIQ tasks and broker configuration"""
import asyncio
from taskiq import TaskiqDepends, TaskiqResult
from taskiq_redis import ListQueueBroker


# Create broker (Redis-based)
broker = ListQueueBroker(
    url="redis://redis:6379",
    queue_name="connexion_tasks"
)


@broker.task(retry_on_error=True, max_retries=3, retry_delay=2.0)
async def step_one(order_id: int, user_name: str) -> dict:
    """First task in the chain - simulates order processing
    
    Args:
        order_id: Order ID to process
        user_name: User who created the order
        
    Returns:
        Dictionary with processing result
    """
    print(f"[STEP 1] Processing order {order_id} for user {user_name}")
    
    # Simulate some async work (DB query, API call, etc.)
    await asyncio.sleep(2)
    
    result = {
        "order_id": order_id,
        "user_name": user_name,
        "status": "validated",
        "total_amount": 99.99
    }
    
    print(f"[STEP 1] Order {order_id} validated: ${result['total_amount']}")
    
    # Chain to the next task - this is how you replicate Celery's chain
    print(f"[STEP 1] Kicking off step_two for order {order_id}")
    await step_two.kiq(
        order_id=result["order_id"],
        amount=result["total_amount"],
        validated=True
    )
    
    return result


@broker.task(retry_on_error=True, max_retries=3, retry_delay=2.0)
async def step_two(order_id: int, amount: float, validated: bool) -> dict:
    """Second task in the chain - simulates payment processing
    
    Args:
        order_id: Order ID from previous task
        amount: Amount to charge
        validated: Whether order was validated
        
    Returns:
        Dictionary with payment result
    """
    print(f"[STEP 2] Processing payment for order {order_id}: ${amount}")
    
    if not validated:
        print(f"[STEP 2] Order {order_id} not validated, skipping payment")
        return {"error": "Order not validated"}
    
    # Simulate payment processing
    await asyncio.sleep(1.5)
    
    result = {
        "order_id": order_id,
        "amount_charged": amount,
        "payment_status": "completed",
        "transaction_id": f"txn_{order_id}_abc123"
    }
    
    print(f"[STEP 2] Payment completed for order {order_id}: {result['transaction_id']}")
    
    # Could chain to a third task here if needed
    # await step_three.kiq(transaction_id=result["transaction_id"])
    
    return result


@broker.task(retry_on_error=True, max_retries=3, retry_delay=1.0)
async def independent_task(message: str, repeat: int = 1) -> list:
    """Independent task (not part of chain) for comparison
    
    Args:
        message: Message to process
        repeat: How many times to repeat
        
    Returns:
        List of processed messages
    """
    print(f"[INDEPENDENT] Processing: {message} (repeat={repeat})")
    
    await asyncio.sleep(0.5)
    
    results = [f"{message}_{i}" for i in range(repeat)]
    print(f"[INDEPENDENT] Completed: {results}")
    
    return results
