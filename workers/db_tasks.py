"""Database tasks for TaskIQ"""
from workers.tasks import broker
from db.session import get_session
from db.repositories import OrderRepository


@broker.task(retry_on_error=True, max_retries=3, retry_delay=2.0)
async def create_order_with_children(
    customer_name: str,
    items: list[dict],
    payments: list[dict]
) -> dict:
    """Create order with items and payments in a background task
    
    This demonstrates:
    - Creating parent record (Order)
    - Creating multiple child records (OrderItems, Payments)
    - All in a single transaction with proper relationship handling
    
    Args:
        customer_name: Customer name
        items: List of items [{"product_name": "...", "quantity": 1, "price": 9.99}, ...]
        payments: List of payments [{"amount": 9.99, "payment_method": "card", "transaction_id": "..."}, ...]
    
    Returns:
        Dict with order_id and status
    """
    print(f"[DB_TASK] Creating order for {customer_name}")
    print(f"[DB_TASK] Items: {len(items)}, Payments: {len(payments)}")
    
    async with get_session() as session:
        # Create order with all children in one transaction
        order = await OrderRepository.create_order(
            session=session,
            customer_name=customer_name,
            items=items,
            payments=payments
        )
        
        # Session commits on context manager exit
        order_id = order.id
        total_amount = order.total_amount
    
    print(f"[DB_TASK] Order {order_id} created successfully (${total_amount})")
    
    return {
        "order_id": order_id,
        "customer_name": customer_name,
        "total_amount": total_amount,
        "items_count": len(items),
        "payments_count": len(payments),
        "status": "completed"
    }


@broker.task(retry_on_error=True, max_retries=3, retry_delay=2.0)
async def process_order(order_id: int) -> dict:
    """Example task showing different loading strategies
    
    This demonstrates:
    - Lazy loading (when you don't need children)
    - Eager loading (when you do need children)
    - Updating records
    """
    print(f"[DB_TASK] Processing order {order_id}")
    
    # Scenario 1: Check order exists (don't need children = lazy load)
    async with get_session() as session:
        order = await OrderRepository.get_order_lazy(session, order_id)
        if not order:
            return {"error": "Order not found", "order_id": order_id}
        
        print(f"[DB_TASK] Order {order_id} status: {order.status}")
    
    # Scenario 2: Process order (need all children = eager load)
    async with get_session() as session:
        # Use selectinload for hundreds of children
        order = await OrderRepository.get_order_eager_selectin(session, order_id)
        
        # Now you can access children without additional queries
        total_items = len(order.items)
        total_paid = sum(p.amount for p in order.payments)
        
        print(f"[DB_TASK] Order {order_id}: {total_items} items, ${total_paid} paid")
        
        # Update order status
        order.status = "processed"
        # Commits on exit
    
    print(f"[DB_TASK] Order {order_id} processed successfully")
    
    return {
        "order_id": order_id,
        "items_count": total_items,
        "total_paid": total_paid,
        "status": "processed"
    }
