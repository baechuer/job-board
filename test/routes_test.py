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
        cls.app.config['SECRET_KEY'] = "testkeySECRET_KEY"
        cls.client = cls.app.test_client()
        cls.app.app_context().push()  # ✅ Push app context
        
    def test_get_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_get_register(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
    

    
if __name__ == '__main__':
    unittest.main()