# Dynamic SQLAlchemy Relationship Loading Guide

> How to handle selective eager loading with many child relationships (without a repository class)

## The Problem

You have a parent table with 10+ child relationships. Different endpoints need different combinations:
- Some need most relationships
- Some need just a handful
- Some need only 1-2

Loading all 10 by default is wasteful. Loading none causes N+1 queries.

## Solution: Dynamic Selective Loading

Use SQLAlchemy's `selectinload()` dynamically based on what each endpoint needs.

---

## Pattern 1: Directly in Your Handler/Endpoint

```python
# api/orders.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def get_order(order_id: int, fields: str = None):
    """Get order with dynamic loading - no repository needed"""
    async with get_session() as session:
        # Start with base query
        query = select(Order).where(Order.id == order_id)
        
        # Parse which fields to load
        if fields:
            load_these = set(fields.split(","))
            
            # Dynamically add selectinload for each requested field
            if "items" in load_these:
                query = query.options(selectinload(Order.items))
            if "payments" in load_these:
                query = query.options(selectinload(Order.payments))
            if "shipments" in load_these:
                query = query.options(selectinload(Order.shipments))
            if "refunds" in load_these:
                query = query.options(selectinload(Order.refunds))
            # ... repeat for all 10 child tables
        
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return {"error": "Not found"}, 404
        
        return serialize_order(order), 200
```

**Usage:**
```bash
# Load only items and payments
GET /orders/123?fields=items,payments

# Load everything needed for fulfillment
GET /orders/123?fields=items,shipments,inventory
```

---

## Pattern 2: Reusable Helper Function

Create a simple helper function (no class needed):

```python
# db/utils.py
from sqlalchemy.orm import selectinload

def add_eager_loading(query, model, fields_to_load):
    """Add selectinload for specified fields
    
    Args:
        query: SQLAlchemy query object
        model: Model class (e.g., Order)
        fields_to_load: Set of relationship names to load
    
    Returns:
        Query with selectinload options applied
    
    Usage:
        query = select(Order).where(Order.id == 1)
        query = add_eager_loading(query, Order, {"items", "payments"})
        result = await session.execute(query)
    """
    for field in fields_to_load:
        if hasattr(model, field):
            query = query.options(selectinload(getattr(model, field)))
    return query
```

**Use it anywhere:**

```python
async def get_order(order_id: int, fields: str = None):
    async with get_session() as session:
        query = select(Order).where(Order.id == order_id)
        
        if fields:
            fields_set = set(fields.split(","))
            query = add_eager_loading(query, Order, fields_set)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
```

---

## Pattern 3: Inline Pattern (Simplest)

Just add `.options(selectinload(...))` directly in each endpoint based on what it needs:

```python
async def process_refund(order_id: int):
    """Example: Only need payments and refunds for this operation"""
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.payments))
            .options(selectinload(Order.refunds))
        )
        order = result.scalar_one_or_none()
        # Process refund...


async def generate_invoice(order_id: int):
    """Example: Need different fields for invoice"""
    async with get_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .options(selectinload(Order.payments))
            .options(selectinload(Order.taxes))
            .options(selectinload(Order.discounts))
        )
        order = result.scalar_one_or_none()
        # Generate invoice...


async def get_order_summary(order_id: int):
    """Example: Don't need any children for summary"""
    async with get_session() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
            # No selectinload - lazy loading
        )
        order = result.scalar_one_or_none()
        # Just return order summary without children
```

---

## Pattern 4: Loading Profiles (Most Flexible)

Define common loading patterns as profiles:

```python
# db/loading_profiles.py or at top of your module

# Define loading profiles without classes
LOAD_PROFILES = {
    "minimal": [],
    "summary": ["items", "payments"],
    "full": ["items", "payments", "shipments", "refunds", "notes", 
             "taxes", "discounts", "invoices", "inventory", "audit_logs"],
    "billing": ["payments", "refunds", "invoices", "taxes", "discounts"],
    "fulfillment": ["items", "shipments", "inventory"],
    "customer_view": ["items", "payments", "shipments"],
}


def get_fields_to_load(profile=None, extra_fields=None):
    """Combine profile + extra fields
    
    Args:
        profile: Name of preset profile
        extra_fields: Set/list of additional fields to load
    
    Returns:
        Set of all fields to load
    """
    fields = set(LOAD_PROFILES.get(profile, []))
    if extra_fields:
        fields.update(extra_fields)
    return fields
```

**Use it:**

```python
async def get_order(order_id: int, profile: str = None, fields: str = None):
    """Get order with profile-based loading
    
    Query params:
        profile: billing, fulfillment, customer_view, etc.
        fields: Additional comma-separated fields to load
    """
    async with get_session() as session:
        query = select(Order).where(Order.id == order_id)
        
        # Get fields to load from profile + extras
        extra = set(fields.split(",")) if fields else None
        fields_to_load = get_fields_to_load(profile, extra)
        
        # Apply loading dynamically
        for field in fields_to_load:
            if hasattr(Order, field):
                query = query.options(selectinload(getattr(Order, field)))
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
```

**API Usage:**
```bash
# Use billing profile
GET /orders/123?profile=billing

# Use fulfillment profile + add notes
GET /orders/123?profile=fulfillment&fields=notes

# Load specific fields only
GET /orders/123?fields=items,payments
```

---

## Performance Comparison

### Scenario: Order with 5 items, 2 payments, 3 shipments

**❌ Lazy Loading (N+1 Problem):**
```python
order = await session.get(Order, 1)
# 1 query for order

for item in order.items:  # 1 query PER item = 5 queries
    print(item.name)

for payment in order.payments:  # 1 query PER payment = 2 queries
    print(payment.amount)

# Total: 1 + 5 + 2 = 8 queries 😱
```

**❌ Load Everything (Wasteful):**
```python
query = (
    select(Order)
    .options(selectinload(Order.items))
    .options(selectinload(Order.payments))
    .options(selectinload(Order.shipments))
    .options(selectinload(Order.refunds))
    .options(selectinload(Order.taxes))
    # ... all 10 relationships
)
# Total: 11 queries (1 for order + 1 per relationship)
# But you only needed items! 😱
```

**✅ Selective Loading (Optimal):**
```python
query = (
    select(Order)
    .options(selectinload(Order.items))
    .options(selectinload(Order.payments))
    # Only load what you need
)
# Total: 3 queries (1 for order + 2 for needed relationships) ✨
```

---

## Best Practices

### 1. Default to Lazy
- Don't eagerly load by default
- Most endpoints don't need all relationships
- Lazy loading is the safest default

### 2. Use Profiles for Common Scenarios
- Create profiles for 80% of your use cases
- `billing`, `fulfillment`, `customer_view`, etc.
- Saves you from repeating the same loading logic

### 3. Allow Field-Level Control
- Let power users/admins specify exactly what they need
- Good for debugging and admin tools
- Use query parameters: `?fields=items,payments`

### 4. Document Your Profiles
```python
# Good: Clear documentation
LOAD_PROFILES = {
    "billing": ["payments", "refunds", "invoices"],  # For accounting/finance
    "fulfillment": ["items", "shipments"],           # For warehouse
    "customer_view": ["items", "payments"],          # For customer portal
}
```

### 5. Use `selectinload` for Many Children
- When you have 100+ children: Use `selectinload`
- It does separate queries: 1 for parent + 1 per relationship
- No cartesian product issues

### 6. Consider `joinedload` for Few Children
- When you have < 50 children AND need them: `joinedload` is faster
- Single query with JOIN
- But be careful with large datasets (cartesian product)

```python
# Few children? Use joinedload
query = query.options(joinedload(Order.items))  # Only 5 items

# Many children? Use selectinload
query = query.options(selectinload(Order.audit_logs))  # 500+ logs
```

---

## OpenAPI Integration

```yaml
/orders/{order_id}:
  get:
    summary: Get order with selective loading
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
      
      - name: profile
        in: query
        schema:
          type: string
          enum: [minimal, summary, billing, fulfillment, customer_view, full]
        description: Predefined loading profile
      
      - name: fields
        in: query
        schema:
          type: string
          example: "items,payments,shipments"
        description: Comma-separated list of additional relationships to load
    
    responses:
      '200':
        description: Order details
```

---

## Key Takeaways

✅ **No repository class needed** - Use helpers or inline patterns  
✅ **Dynamic loading** - Only load what each endpoint needs  
✅ **Profiles** - Define common scenarios (billing, fulfillment, etc.)  
✅ **Flexible** - Allow field-level control via query params  
✅ **Performance** - Avoid N+1 and avoid loading unused data  
✅ **Simple** - Just use `selectinload()` intelligently  

## Further Reading

- [SQLAlchemy Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)
- [N+1 Query Problem](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem)
