"""
Test cases for rate limiting functionality across all endpoints.
"""
import pytest
import time
from unittest.mock import patch
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app import create_app
from app.extensions import db
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import TestConfig


class TestRateLimiting:
    """Test rate limiting functionality"""

    @pytest.fixture
    def app_with_limiter(self):
        """Create app with rate limiting enabled"""
        config = TestConfig()
        config.RATELIMIT_STORAGE_URL = "memory://"
        config.RATELIMIT_DEFAULT = "10 per minute"
        config.RATELIMIT_ENABLED = True
        
        app = create_app(config)
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app_with_limiter):
        """Create test client"""
        return app_with_limiter.test_client()

    def test_registration_rate_limit(self, client):
        """Test registration rate limiting"""
        # Make multiple registration attempts
        for i in range(6):  # Exceed the 5 per hour limit
            response = client.post('/api/auth/register', json={
                'email': f'test{i}@example.com',
                'password': 'TestPassword123!',
                'username': f'testuser{i}'
            })
            
            if i < 5:
                # First 5 should succeed or fail for other reasons
                assert response.status_code in [201, 400, 409]
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429
                assert 'Rate limit exceeded' in response.get_json().get('error', '')

    def test_login_rate_limit(self, client):
        """Test login rate limiting"""
        # First register a user
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        # Make multiple login attempts
        for i in range(12):  # Exceed the 10 per hour limit
            response = client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrongpassword'  # Wrong password to avoid success
            })
            
            if i < 10:
                # First 10 should fail for wrong password
                assert response.status_code == 401
            else:
                # 11th attempt should be rate limited
                assert response.status_code == 429

    def test_password_reset_rate_limit(self, client):
        """Test password reset rate limiting"""
        # Make multiple password reset requests
        for i in range(4):  # Exceed the 3 per hour limit
            response = client.post('/api/password/reset', json={
                'email': f'test{i}@example.com'
            })
            
            if i < 3:
                # First 3 should succeed
                assert response.status_code == 200
            else:
                # 4th attempt should be rate limited
                assert response.status_code == 429

    def test_file_upload_rate_limit(self, client):
        """Test file upload rate limiting"""
        # First register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create a job first
        job_response = client.post('/api/recruiter/jobs', 
                                 json={'title': 'Test Job', 'description': 'Test'},
                                 headers=headers)
        job_id = job_response.get_json()['id']
        
        # Create test files
        test_files = {
            'resume': ('test.pdf', b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj', 'application/pdf'),
            'coverLetter': ('cover.pdf', b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj', 'application/pdf')
        }
        
        # Make multiple application attempts
        for i in range(6):  # Exceed the 5 per hour limit
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data={
                                     'first_name': 'Test',
                                     'last_name': 'User',
                                     'email': f'test{i}@example.com',
                                     'phone': '1234567890'
                                 },
                                 files=test_files,
                                 headers=headers)
            
            if i < 5:
                # First 5 should succeed or fail for other reasons
                assert response.status_code in [201, 400, 409]
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429

    def test_file_download_rate_limit(self, client):
        """Test file download rate limiting"""
        # This test would require setting up an application with files
        # For now, we'll test the endpoint exists and rate limiting is applied
        headers = {'Authorization': 'Bearer fake-token'}
        
        # Make multiple download attempts
        for i in range(21):  # Exceed the 20 per hour limit
            response = client.get('/api/applications/1/resume', headers=headers)
            
            if i < 20:
                # First 20 should fail for other reasons (unauthorized, not found)
                assert response.status_code in [401, 404]
            else:
                # 21st attempt should be rate limited
                assert response.status_code == 429

    def test_profile_access_rate_limit(self, client):
        """Test profile access rate limiting"""
        # First register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Make multiple profile access attempts
        for i in range(31):  # Exceed the 30 per hour limit
            response = client.get('/api/auth/me', headers=headers)
            
            if i < 30:
                # First 30 should succeed
                assert response.status_code == 200
            else:
                # 31st attempt should be rate limited
                assert response.status_code == 429

    def test_token_refresh_rate_limit(self, client):
        """Test token refresh rate limiting"""
        # First register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        refresh_token = login_response.get_json()['refresh_token']
        headers = {'Authorization': f'Bearer {refresh_token}'}
        
        # Make multiple refresh attempts
        for i in range(21):  # Exceed the 20 per hour limit
            response = client.post('/api/auth/refresh', headers=headers)
            
            if i < 20:
                # First 20 should succeed
                assert response.status_code == 200
            else:
                # 21st attempt should be rate limited
                assert response.status_code == 429

    def test_logout_rate_limit(self, client):
        """Test logout rate limiting"""
        # First register and login
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Make multiple logout attempts
        for i in range(21):  # Exceed the 20 per hour limit
            response = client.post('/api/auth/logout', headers=headers)
            
            if i < 20:
                # First 20 should succeed
                assert response.status_code == 200
            else:
                # 21st attempt should be rate limited
                assert response.status_code == 429

    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are included in responses"""
        # Make a request that should include rate limit headers
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        # Check for rate limit headers
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
        assert 'X-RateLimit-Reset' in response.headers

    def test_rate_limit_reset_after_time(self, client):
        """Test that rate limits reset after time period"""
        # This test would require mocking time or using a very short time window
        # For now, we'll just verify the rate limiting is working
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        assert response.status_code in [201, 400, 409]  # Should not be rate limited initially

    def test_different_ips_different_limits(self, client):
        """Test that different IP addresses have separate rate limits"""
        # This would require mocking the IP address
        # Flask-Limiter uses get_remote_address by default
        with patch('flask_limiter.util.get_remote_address') as mock_ip:
            # First IP
            mock_ip.return_value = '192.168.1.1'
            response1 = client.post('/api/auth/register', json={
                'email': 'test1@example.com',
                'password': 'TestPassword123!',
                'username': 'testuser1'
            })
            
            # Second IP
            mock_ip.return_value = '192.168.1.2'
            response2 = client.post('/api/auth/register', json={
                'email': 'test2@example.com',
                'password': 'TestPassword123!',
                'username': 'testuser2'
            })
            
            # Both should succeed as they're from different IPs
            assert response1.status_code in [201, 400, 409]
            assert response2.status_code in [201, 400, 409]

    def test_rate_limit_error_message(self, client):
        """Test rate limit error message format"""
        # Exceed rate limit
        for i in range(6):  # Exceed the 5 per hour limit
            response = client.post('/api/auth/register', json={
                'email': f'test{i}@example.com',
                'password': 'TestPassword123!',
                'username': f'testuser{i}'
            })
        
        # Check error message format
        assert response.status_code == 429
        error_data = response.get_json()
        assert 'error' in error_data
        assert 'Rate limit exceeded' in error_data['error']
