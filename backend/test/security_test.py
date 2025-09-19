import unittest
from app.security import *

class SecurityTestCase(unittest.TestCase):
    def test_get_hash(self):
        hash = get_salt()
        self.assertEqual(len(hash), 4)