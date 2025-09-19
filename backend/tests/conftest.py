import os
import sys
import tempfile
import pytest

# Ensure the backend directory is on sys.path so 'app' can be imported
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app
from app.extensions import db as _db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"
    BCRYPT_LOG_ROUNDS = 4


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


