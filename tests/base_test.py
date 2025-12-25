"""Base test case for all tests"""
import unittest
import sys
import os
from flask.testing import FlaskClient
from werkzeug.test import Client

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as connexion_app


class BaseTestCase(unittest.TestCase):
    """Base test case that all test classes should inherit from"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests in the class"""
        # Get the underlying Flask app from Connexion
        cls.app = connexion_app.app
        cls.app.config['TESTING'] = True
        
        # Create test client using the Connexion ASGI app
        # This wraps the ASGI app so Flask test client methods work
        from werkzeug.test import Client as WerkzeugClient
        from werkzeug.wrappers import Response
        
        # Use connexion's test client which properly handles ASGI middleware
        cls.client = connexion_app.test_client()
    
    def setUp(self):
        """Runs before each test method"""
        pass
    
    def tearDown(self):
        """Runs after each test method"""
        pass
