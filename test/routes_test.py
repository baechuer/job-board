import unittest
from app.routes import *
from app.database import *
from app.models import User, Roles
from app.security import *
from unittest.mock import patch

class RoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['SECRET_KEY'] = "testkeySECRET_KEY"
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app.config['MAIL_SUPPRESS_SEND'] = True
        cls.client = cls.app.test_client()
        cls.app.app_context().push()  # ✅ Push app context
    
        
    def test_get_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_login(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        response = self.client.post('/login', data=dict(username='admin', password='admin'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_register(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    @patch('flask_mail.Mail.send')  # Mock the send method from flask_mail.Mail
    def test_register(self, mock_send):
        with self.client as client:
            response = client.post('/register', data=dict(username='testuser',
                            password='testpassword', userrole=2, email='testemail@email.com'),
                            follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            mock_send.assert_called_once()
            user = get_user_by_username('testuser')
            self.assertIsNotNone(user)


    
if __name__ == '__main__':
    unittest.main()