"""Base test case for all tests"""
import unittest
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


class BaseTestCase(unittest.TestCase):
    """Base test case that all test classes should inherit from"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client once for all tests in the class"""
        # Create the Connexion app
        connexion_app = create_app()
        
        # Get the underlying Flask app
        cls.app = connexion_app.app
        cls.app.config['TESTING'] = True
        
        # Create test client
        cls.client = cls.app.test_client()
    
    def setUp(self):
        """Runs before each test method"""
        pass
    
    def tearDown(self):
        """Runs after each test method"""
        pass
