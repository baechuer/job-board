"""
Test cases for CORS configuration and security headers.
"""
import pytest

from app import create_app
from app.extensions import db
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import TestConfig


class TestCORSAndSecurityHeaders:
    """Test CORS configuration and security headers"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        config = TestConfig()
        config.CORS_ORIGINS = ['http://localhost:3000', 'https://example.com']
        config.CORS_SUPPORTS_CREDENTIALS = True
        config.CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Custom-Header']
        config.CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
        
        app = create_app(config)
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_cors_preflight_request(self, client):
        """Test CORS preflight request handling"""
        # Test preflight request
        response = client.options('/api/auth/login',
                                headers={
                                    'Origin': 'http://localhost:3000',
                                    'Access-Control-Request-Method': 'POST',
                                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                                })
        
        assert response.status_code == 200
        
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
        assert 'Access-Control-Allow-Credentials' in response.headers

    def test_cors_allowed_origin(self, client):
        """Test CORS with allowed origin"""
        response = client.post('/api/auth/register',
                             json={
                                 'email': 'test@example.com',
                                 'password': 'TestPassword123!',
                                 'username': 'testuser'
                             },
                             headers={'Origin': 'http://localhost:3000'})
        
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == 'http://localhost:3000'

    def test_cors_disallowed_origin(self, client):
        """Test CORS with disallowed origin"""
        response = client.post('/api/auth/register',
                             json={
                                 'email': 'test@example.com',
                                 'password': 'TestPassword123!',
                                 'username': 'testuser'
                             },
                             headers={'Origin': 'http://malicious-site.com'})
        
        # Should not include CORS headers for disallowed origin
        assert 'Access-Control-Allow-Origin' not in response.headers

    def test_cors_credentials_support(self, client):
        """Test CORS credentials support"""
        response = client.post('/api/auth/register',
                             json={
                                 'email': 'test@example.com',
                                 'password': 'TestPassword123!',
                                 'username': 'testuser'
                             },
                             headers={'Origin': 'http://localhost:3000'})
        
        assert 'Access-Control-Allow-Credentials' in response.headers
        assert response.headers['Access-Control-Allow-Credentials'] == 'true'

    def test_cors_exposed_headers(self, client):
        """Test CORS exposed headers"""
        response = client.post('/api/auth/register',
                             json={
                                 'email': 'test@example.com',
                                 'password': 'TestPassword123!',
                                 'username': 'testuser'
                             },
                             headers={'Origin': 'http://localhost:3000'})
        
        assert 'Access-Control-Expose-Headers' in response.headers
        exposed_headers = response.headers['Access-Control-Expose-Headers']
        assert 'Content-Type' in exposed_headers
        assert 'Authorization' in exposed_headers

    def test_security_headers_present(self, client):
        """Test that security headers are present in responses"""
        response = client.get('/api/auth/me')
        
        # Check for security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'Referrer-Policy'
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Missing security header: {header}"

    def test_x_content_type_options_header(self, client):
        """Test X-Content-Type-Options header"""
        response = client.get('/api/auth/me')
        
        assert response.headers['X-Content-Type-Options'] == 'nosniff'

    def test_x_frame_options_header(self, client):
        """Test X-Frame-Options header"""
        response = client.get('/api/auth/me')
        
        assert response.headers['X-Frame-Options'] == 'DENY'

    def test_x_xss_protection_header(self, client):
        """Test X-XSS-Protection header"""
        response = client.get('/api/auth/me')
        
        assert response.headers['X-XSS-Protection'] == '1; mode=block'

    def test_strict_transport_security_header(self, client):
        """Test Strict-Transport-Security header"""
        response = client.get('/api/auth/me')
        
        assert 'Strict-Transport-Security' in response.headers
        hsts_value = response.headers['Strict-Transport-Security']
        assert 'max-age=31536000' in hsts_value
        assert 'includeSubDomains' in hsts_value

    def test_content_security_policy_header(self, client):
        """Test Content-Security-Policy header"""
        response = client.get('/api/auth/me')
        
        assert 'Content-Security-Policy' in response.headers
        csp_value = response.headers['Content-Security-Policy']
        assert "default-src 'self'" in csp_value

    def test_referrer_policy_header(self, client):
        """Test Referrer-Policy header"""
        response = client.get('/api/auth/me')
        
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'

    def test_security_headers_on_all_endpoints(self, client):
        """Test that security headers are present on all endpoints"""
        endpoints = [
            '/api/auth/register',
            '/api/auth/login',
            '/api/auth/me',
            '/api/applications/my-applications',
            '/api/recruiter/jobs'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            
            # Check for key security headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-XSS-Protection' in response.headers

    def test_cors_headers_on_all_endpoints(self, client):
        """Test that CORS headers are present on all API endpoints"""
        endpoints = [
            '/api/auth/register',
            '/api/auth/login',
            '/api/auth/me',
            '/api/applications/my-applications',
            '/api/recruiter/jobs'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint,
                               headers={'Origin': 'http://localhost:3000'})
            
            # Check for CORS headers
            assert 'Access-Control-Allow-Origin' in response.headers
            assert 'Access-Control-Allow-Credentials' in response.headers

    def test_cors_preflight_all_methods(self, client):
        """Test CORS preflight for different HTTP methods"""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        
        for method in methods:
            response = client.options('/api/auth/login',
                                    headers={
                                        'Origin': 'http://localhost:3000',
                                        'Access-Control-Request-Method': method,
                                        'Access-Control-Request-Headers': 'Content-Type,Authorization'
                                    })
            
            assert response.status_code == 200
            assert 'Access-Control-Allow-Methods' in response.headers

    def test_cors_preflight_custom_headers(self, client):
        """Test CORS preflight with custom headers"""
        response = client.options('/api/auth/login',
                                headers={
                                    'Origin': 'http://localhost:3000',
                                    'Access-Control-Request-Method': 'POST',
                                    'Access-Control-Request-Headers': 'X-Custom-Header'
                                })
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Headers' in response.headers
        allowed_headers = response.headers['Access-Control-Allow-Headers']
        assert 'X-Custom-Header' in allowed_headers

    def test_cors_multiple_origins(self, client):
        """Test CORS with multiple allowed origins"""
        allowed_origins = ['http://localhost:3000', 'https://example.com']
        
        for origin in allowed_origins:
            response = client.post('/api/auth/register',
                                 json={
                                     'email': f'test@{origin.replace("://", "").replace(".", "")}.com',
                                     'password': 'TestPassword123!',
                                     'username': f'testuser{origin.replace("://", "").replace(".", "")}'
                                 },
                                 headers={'Origin': origin})
            
            assert 'Access-Control-Allow-Origin' in response.headers
            assert response.headers['Access-Control-Allow-Origin'] == origin

    def test_cors_no_origin_header(self, client):
        """Test CORS when no Origin header is present"""
        response = client.post('/api/auth/register',
                             json={
                                 'email': 'test@example.com',
                                 'password': 'TestPassword123!',
                                 'username': 'testuser'
                             })
        
        # Flask-CORS adds headers even without Origin header for preflight support
        # This is correct behavior for CORS
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_security_headers_production_config(self):
        """Test security headers with production configuration"""
        from app.config.production import ProductionConfig
        
        app = create_app(ProductionConfig)
        client = app.test_client()
        
        response = client.get('/api/auth/me')
        
        # Check for enhanced security headers in production
        assert 'Permissions-Policy' in response.headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers

    def test_cors_configuration_environment_variables(self):
        """Test CORS configuration via environment variables"""
        import os
        from unittest.mock import patch
        
        with patch.dict(os.environ, {
            'CORS_ORIGINS': 'https://app.example.com,https://admin.example.com',
            'CORS_SUPPORTS_CREDENTIALS': 'true'
        }):
            config = TestConfig()
            config.CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
            config.CORS_SUPPORTS_CREDENTIALS = os.getenv('CORS_SUPPORTS_CREDENTIALS', 'false').lower() == 'true'
            
            app = create_app(config)
            client = app.test_client()
            
            response = client.post('/api/auth/register',
                                 json={
                                     'email': 'test@example.com',
                                     'password': 'TestPassword123!',
                                     'username': 'testuser'
                                 },
                                 headers={'Origin': 'https://app.example.com'})
            
            assert 'Access-Control-Allow-Origin' in response.headers
            assert response.headers['Access-Control-Allow-Origin'] == 'https://app.example.com'
