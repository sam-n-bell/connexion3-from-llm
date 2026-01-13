"""Repository layer for clean data access"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Order, OrderItem, Payment


class OrderRepository:
    """Repository for Order operations with flexible loading strategies"""
    
    @staticmethod
    async def create_order(
        session: AsyncSession,
        customer_name: str,
        items: List[dict],
        payments: List[dict]
    ) -> Order:
        """Create order with items and payments in a single transaction
        
        Args:
            session: Database session
            customer_name: Customer name
            items: List of dicts with product_name, quantity, price
            payments: List of dicts with amount, payment_method, transaction_id
        
        Returns:
            Created Order instance with relationships loaded
        """
        # Calculate total from items
        total = sum(item["price"] * item["quantity"] for item in items)
        
        # Create order
        order = Order(
            customer_name=customer_name,
            total_amount=total,
            status="pending"
        )
        
        # Add items (using append triggers cascade)
        for item_data in items:
            item = OrderItem(
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                price=item_data["price"]
            )
            order.items.append(item)
        
        # Add payments
        for payment_data in payments:
            payment = Payment(
                amount=payment_data["amount"],
                payment_method=payment_data["payment_method"],
                transaction_id=payment_data["transaction_id"]
            )
            order.payments.append(payment)
        
        session.add(order)
        await session.flush()  # Get ID without committing
        await session.refresh(order)  # Refresh to ensure relationships are loaded
        
        return order
    
    @staticmethod
    async def get_order_lazy(session: AsyncSession, order_id: int) -> Optional[Order]:
        """Get order WITHOUT loading children (lazy loading)
        
        Use when: You only need order data, not children
        Performance: 1 query
        """
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_order_eager_selectin(
        session: AsyncSession,
        order_id: int
    ) -> Optional[Order]:
        """Get order WITH children using selectinload (separate queries)
        
        Use when: You have MANY children (100s+) or always need children
        Performance: 1 query for order + 1 for items + 1 for payments = 3 queries
        Benefit: No cartesian product, efficient with large datasets
        """
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .options(selectinload(Order.payments))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_order_eager_joined(
        session: AsyncSession,
        order_id: int
    ) -> Optional[Order]:
        """Get order WITH children using joinedload (single JOIN query)
        
        Use when: You have FEW children (< 50-100) and need them
        Performance: 1 query with JOINs
        Benefit: Single query
        Caution: Can create large result sets with many children (cartesian product)
        """
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(joinedload(Order.items))
            .options(joinedload(Order.payments))
        )
        # unique() is needed with joinedload to deduplicate rows
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def list_orders_with_children(
        session: AsyncSession,
        limit: int = 100,
        offset: int = 0
    ) -> List[Order]:
        """List orders with eager-loaded children (batch loading)
        
        Use when: Listing multiple orders that each have children
        Performance: selectinload is optimal for lists (avoids N+1)
        """
        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .options(selectinload(Order.payments))
            .limit(limit)
            .offset(offset)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_order_status(
        session: AsyncSession,
        order_id: int,
        status: str
    ) -> Optional[Order]:
        """Update order status
        
        Args:
            session: Database session
            order_id: Order ID
            status: New status
            
        Returns:
            Updated Order or None if not found
        """
        order = await OrderRepository.get_order_lazy(session, order_id)
        if order:
            order.status = status
            await session.flush()
        return order
