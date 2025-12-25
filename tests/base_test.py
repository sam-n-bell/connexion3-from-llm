"""Base test case for all tests"""
import unittest
import sys
import os
from httpx import AsyncClient, ASGITransport
import asyncio

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as asgi_app


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    """Base test case that all test classes should inherit from
    
    Uses IsolatedAsyncioTestCase for async test support.
    """
    
    async def asyncSetUp(self):
        """Set up async test client for each test"""
        # Create async HTTP client with ASGI transport
        self.client = AsyncClient(
            transport=ASGITransport(app=asgi_app),
            base_url="http://test"
        )
    
    async def asyncTearDown(self):
        """Clean up async client"""
        await self.client.aclose()
    
    def setUp(self):
        """Runs before each test method"""
        pass
    
    def tearDown(self):
        """Runs after each test method"""
        pass
