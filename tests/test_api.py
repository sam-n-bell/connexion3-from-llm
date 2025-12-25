"""API endpoint tests"""
from tests.base_test import BaseTestCase


class TestHealthEndpoint(BaseTestCase):
    """Tests for health check endpoint"""
    
    async def test_health_check(self):
        """Test health endpoint returns 200"""
        response = await self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('message', data)


class TestUsersEndpoint(BaseTestCase):
    """Tests for user endpoints"""
    
    async def test_get_users(self):
        """Test getting all users"""
        response = await self.client.get('/api/v1/users')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    async def test_get_user_by_id(self):
        """Test getting a specific user"""
        response = await self.client.get('/api/v1/users/1')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['id'], 1)
        self.assertIn('name', data)
        self.assertIn('email', data)
    
    async def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        response = await self.client.get('/api/v1/users/9999')
        self.assertEqual(response.status_code, 404)
    
    async def test_create_user(self):
        """Test creating a new user"""
        new_user = {
            "name": "Charlie",
            "email": "charlie@example.com"
        }
        
        response = await self.client.post(
            '/api/v1/users',
            json=new_user
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Charlie')
        self.assertEqual(data['email'], 'charlie@example.com')
    
    async def test_create_user_missing_fields(self):
        """Test creating a user with missing required fields"""
        incomplete_user = {
            "name": "Dave"
            # Missing email field
        }
        
        response = await self.client.post(
            '/api/v1/users',
            json=incomplete_user
        )
        
        # Should fail validation
        self.assertEqual(response.status_code, 400)
