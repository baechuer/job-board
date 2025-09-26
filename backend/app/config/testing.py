import os
from pathlib import Path

class TestConfig:
    """Test configuration"""
    TESTING = True
    SECRET_KEY = "test-secret"
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"
    # Token lifetimes
    JWT_ACCESS_TOKEN_EXPIRES = 900  # seconds
    JWT_REFRESH_TOKEN_EXPIRES = 1209600  # 14 days
    # Mail
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "test@example.com"
    FRONTEND_URL = "http://localhost:5173"
    JSON_SORT_KEYS = False
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
