import unittest
from app.routes import *
from app.database import *
from app.models import User, Roles
from app.security import *
from app import create_app

class RoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        cls.app.app_context().push()  # ✅ Push app context
    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
if __name__ == '__main__':
    unittest.main()