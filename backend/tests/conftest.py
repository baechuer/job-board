import os
import sys
import tempfile
import pytest
import shutil
import glob
from pathlib import Path

# Ensure the backend directory is on sys.path so 'app' can be imported
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app
from app.extensions import db as _db
from app.services.auth_service import register_user, authenticate
from flask_jwt_extended import create_access_token
from datetime import timedelta


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"
    BCRYPT_LOG_ROUNDS = 4
    SECRET_KEY = "test-secret"
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_DEFAULT_SENDER = "test@example.com"
    
    # Security Settings for Testing
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_HEADERS_ENABLED = True
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER = "/tmp/test_uploads"
    ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "txt", "rtf", "odt"]
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    CORS_EXPOSE_HEADERS = ["Content-Type", "Authorization"]
    CORS_SUPPORTS_CREDENTIALS = True
    ENABLE_VIRUS_SCAN = False  # Disable for testing
    MAX_STRING_LENGTH = 1000
    MAX_EMAIL_LENGTH = 254
    MAX_PASSWORD_LENGTH = 128
    
    # Security Headers for Testing
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }


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


@pytest.fixture(autouse=True)
def db(app):
    # Ensure a clean database for each test
    _db.session.remove()
    _db.drop_all()
    _db.create_all()
    yield _db
    _db.session.remove()


@pytest.fixture
def make_user(app):
    def _mk(is_verified=True):
        email = f"user{os.urandom(4).hex()}@example.com"
        user = register_user(email=email, password="Password123!", username=email.split('@')[0])
        if is_verified:
            user.is_verified = True
            _db.session.commit()
        return user
    return _mk


@pytest.fixture
def auth_headers(app):
    def _hdr(user):
        access = create_access_token(identity=str(user.id), expires_delta=timedelta(minutes=15))
        return {"Authorization": f"Bearer {access}"}
    return _hdr


@pytest.fixture
def make_job(app):
    from app.services.job_service import JobService
    def _mk(user_id):
        payload = {
            "title": f"Job {os.urandom(2).hex()}",
            "description": "desc long enough",
            "salary_min": 1,
            "salary_max": 2,
            "location": "Remote",
            "requirements": ["req"],
            "responsibilities": "resp",
            "skills": ["skill"],
            "application_deadline": "2099-01-01",
        }
        JobService().create_job(user_id=user_id, job_data=payload)
        # Fetch minimal info
        from sqlalchemy import select
        from app.models.job import Job
        return _db.session.execute(select(Job).where(Job.user_id==user_id).limit(1)).scalar_one()
    return _mk


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_files():
    """Automatically clean up test files before and after test session"""
    static_dir = Path(BACKEND_DIR) / "static"
    reports_dir = Path(BACKEND_DIR) / "reports"
    coverage_dir = Path(BACKEND_DIR) / "htmlcov"
    junit_file = Path(BACKEND_DIR) / "junit.xml"
    coverage_file = Path(BACKEND_DIR) / ".coverage"
    
    # Clean up before tests start
    _cleanup_directories(static_dir, reports_dir, coverage_dir, junit_file, coverage_file)
    
    yield
    
    # Clean up after tests complete
    _cleanup_directories(static_dir, reports_dir, coverage_dir, junit_file, coverage_file)


@pytest.fixture(autouse=True)
def cleanup_test_files_per_test():
    """Clean up test files after each test"""
    static_dir = Path(BACKEND_DIR) / "static"
    
    yield
    
    # Clean up test files created during this test
    _cleanup_test_files_in_static(static_dir)
    _cleanup_root_test_files()


def _cleanup_directories(static_dir, reports_dir, coverage_dir, junit_file, coverage_file):
    """Clean up test directories and files"""
    # Clean up test reports and coverage files
    for cleanup_path in [reports_dir, coverage_dir]:
        if cleanup_path.exists():
            try:
                shutil.rmtree(cleanup_path)
            except Exception:
                pass  # Ignore cleanup errors
    
    # Clean up individual files
    for cleanup_file in [junit_file, coverage_file]:
        if cleanup_file.exists():
            try:
                cleanup_file.unlink()
            except Exception:
                pass  # Ignore cleanup errors
    
    # Clean up static test files
    _cleanup_test_files_in_static(static_dir)
    
    # Clean up any other test files in root directory
    _cleanup_root_test_files()


def _cleanup_test_files_in_static(static_dir):
    """Clean up test files in static directory"""
    if not static_dir.exists():
        return
    
    # Patterns for test files and directories
    test_patterns = [
        "users/*/applications/*",  # Application files
        "test_*",                  # Test files
        "temp_*",                  # Temporary files
        "tmp_*",                   # Temporary files
        "*_test.*",                # Test files
    ]
    
    for pattern in test_patterns:
        for file_path in static_dir.glob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception:
                pass  # Ignore cleanup errors


def _cleanup_root_test_files():
    """Clean up test files in root directory"""
    root_patterns = [
        "test_*.pdf",           # Test PDF files
        "test_*.txt",           # Test text files
        "test_*.doc",           # Test document files
        "test_*.docx",          # Test document files
        "*.log",                # Log files
        ".coverage.*",          # Coverage files
        "coverage.xml",         # Coverage XML
        "pytest.ini.bak",       # Backup config files
        "*.tmp",                # Temporary files
        "*.temp",               # Temporary files
    ]
    
    for pattern in root_patterns:
        for file_path in Path(BACKEND_DIR).glob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
            except Exception:
                pass  # Ignore cleanup errors


@pytest.fixture(autouse=True)
def clear_rate_limiter(app):
    """Clear rate limiter storage before each test"""
    from app.extensions import limiter
    try:
        storage = getattr(limiter, 'storage', None)
        if storage:
            try:
                storage.clear()
            except Exception:
                pass
    except Exception:
        # Limiter might be disabled or uninitialized in tests
        pass
    yield
    # Ensure limiter is disabled after each test unless explicitly enabled by a test app
    try:
        limiter.enabled = bool(app.config.get('RATELIMIT_ENABLED', False))
    except Exception:
        pass


