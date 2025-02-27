import unittest
from app.routes import *
from app.database import *
from app.models import User, Roles


class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        #setup the test database before each testcase
        with app.app_context():
            db.create_all()

    def tearDown(self):
        #clean up the test database after each testcase
        with app.app_context():
            db.session.remove()
            drop_all(app)

    def test_create_user(self):
        with app.app_context():
            create_user('testuser', 'testpassword', Roles.USER.value, "!@")
            queried_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(queried_user)
            self.assertEqual('testpassword', queried_user.password)
            self.assertEqual(Roles.USER.value, queried_user.userrole)

    def test_get_user_by_username(self):
        with app.app_context():
            create_user('testuser', 'testpassword', Roles.USER.value, "!@")
            queried_user = get_user_by_username('testuser')
            self.assertIsNotNone(queried_user)
            self.assertEqual('testpassword', queried_user.password)

    def test_update_user_password(self):
        with app.app_context():
            create_user('testuser', 'testpassword', Roles.USER.value, "!@")
            update_user_password('testuser', 'testpassword', 'newpassword')
            queried_user = get_user_by_username('testuser')
            self.assertEqual('newpassword', queried_user.password)

    def test_update_userrole(self):
        with app.app_context():
            create_user('testuser', 'testpassword', Roles.USER.value, "!@")
            update_userrole('testuser', Roles.ADMIN.value)
            queried_user = get_user_by_username('testuser')
            self.assertEqual(Roles.ADMIN.value, queried_user.userrole)

    
if __name__ == '__main__':
    unittest.main()