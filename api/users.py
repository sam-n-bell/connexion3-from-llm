"""User management endpoints"""

# In-memory database (for demo purposes)
USERS_DB = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"},
}
NEXT_ID = 3


def get_users():
    """Get all users"""
    return list(USERS_DB.values()), 200


def get_user(user_id):
    """Get a specific user by ID"""
    user = USERS_DB.get(user_id)
    if user:
        return user, 200
    return {"error": "User not found"}, 404


def create_user(body):
    """Create a new user"""
    global NEXT_ID
    
    new_user = {
        "id": NEXT_ID,
        "name": body["name"],
        "email": body["email"]
    }
    USERS_DB[NEXT_ID] = new_user
    NEXT_ID += 1
    
    return new_user, 201
