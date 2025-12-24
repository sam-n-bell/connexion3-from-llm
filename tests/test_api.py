"""API endpoint tests"""
import json
from tests.base_test import BaseTestCase


class TestHealthEndpoint(BaseTestCase):
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns 200"""
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('message', data)


class TestUsersEndpoint(BaseTestCase):
    """Tests for user endpoints"""
    
    def test_get_users(self):
        """Test getting all users"""
        response = self.client.get('/api/v1/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_get_user_by_id(self):
        """Test getting a specific user"""
        response = self.client.get('/api/v1/users/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertIn('name', data)
        self.assertIn('email', data)
    
    def test_get_user_not_found(self):
        """Test getting a non-existent user"""
        response = self.client.get('/api/v1/users/9999')
        self.assertEqual(response.status_code, 404)
    
    def test_create_user(self):
        """Test creating a new user"""
        new_user = {
            "name": "Charlie",
            "email": "charlie@example.com"
        }
        
        response = self.client.post(
            '/api/v1/users',
            data=json.dumps(new_user),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Charlie')
        self.assertEqual(data['email'], 'charlie@example.com')
    
    def test_create_user_missing_fields(self):
        """Test creating a user with missing required fields"""
        incomplete_user = {
            "name": "Dave"
            # Missing email field
        }
        
        response = self.client.post(
            '/api/v1/users',
            data=json.dumps(incomplete_user),
            content_type='application/json'
        )
        
        # Should fail validation
        self.assertEqual(response.status_code, 400)
