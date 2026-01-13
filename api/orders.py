"""Order API endpoints"""
from db.session import get_session
from db.repositories import OrderRepository
from workers.db_tasks import create_order_with_children, process_order


async def create_order(body):
    """Create order asynchronously via TaskIQ task
    
    Kicks off a background task to create order with items and payments.
    Returns immediately with task_id for tracking.
    """
    customer_name = body.get("customer_name")
    items = body.get("items", [])
    payments = body.get("payments", [])
    
    # Enqueue async task
    task = await create_order_with_children.kiq(
        customer_name=customer_name,
        items=items,
        payments=payments
    )
    
    return {
        "message": "Order creation started",
        "task_id": task.task_id,
        "customer_name": customer_name,
        "items_count": len(items),
        "payments_count": len(payments)
    }, 202


async def get_order(order_id: int, load_children: bool = False):
    """Get order by ID with optional eager loading
    
    Query params:
        load_children: If true, eagerly load items and payments
    """
    async with get_session() as session:
        if load_children:
            # Eager load with selectinload (efficient for many children)
            order = await OrderRepository.get_order_eager_selectin(session, order_id)
        else:
            # Lazy load (faster when you don't need children)
            order = await OrderRepository.get_order_lazy(session, order_id)
        
        if not order:
            return {"error": "Order not found"}, 404
        
        result = {
            "id": order.id,
            "customer_name": order.customer_name,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at.isoformat()
        }
        
        # Include children if loaded
        if load_children:
            result["items"] = [
                {
                    "id": item.id,
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order.items
            ]
            result["payments"] = [
                {
                    "id": p.id,
                    "amount": p.amount,
                    "payment_method": p.payment_method,
                    "transaction_id": p.transaction_id,
                    "created_at": p.created_at.isoformat()
                }
                for p in order.payments
            ]
        
        return result, 200


async def list_orders(limit: int = 100, offset: int = 0, load_children: bool = False):
    """List orders with pagination and optional eager loading"""
    async with get_session() as session:
        if load_children:
            orders = await OrderRepository.list_orders_with_children(session, limit, offset)
        else:
            # For listing without children, use lazy loading
            from sqlalchemy import select
            from db.models import Order
            result = await session.execute(
                select(Order)
                .limit(limit)
                .offset(offset)
                .order_by(Order.created_at.desc())
            )
            orders = list(result.scalars().all())
        
        orders_data = []
        for order in orders:
            order_dict = {
                "id": order.id,
                "customer_name": order.customer_name,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at.isoformat()
            }
            
            if load_children:
                order_dict["items_count"] = len(order.items)
                order_dict["payments_count"] = len(order.payments)
            
            orders_data.append(order_dict)
        
        return {
            "orders": orders_data,
            "limit": limit,
            "offset": offset,
            "count": len(orders_data)
        }, 200


async def process_order_endpoint(order_id: int):
    """Trigger order processing task"""
    task = await process_order.kiq(order_id=order_id)
    
    return {
        "message": "Order processing started",
        "task_id": task.task_id,
        "order_id": order_id
    }, 202
