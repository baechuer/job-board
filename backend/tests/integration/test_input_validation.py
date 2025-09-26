"""
Test cases for input validation and sanitization across all endpoints.
"""
import pytest
from unittest.mock import patch

from app import create_app
from app.extensions import db
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import TestConfig


class TestInputValidation:
    """Test input validation and sanitization"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        config = TestConfig()
        app = create_app(config)
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    @pytest.fixture
    def auth_headers(self, client):
        """Create authenticated user and return headers"""
        # Register user
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        
        token = login_response.get_json()['access_token']
        return {'Authorization': f'Bearer {token}'}

    def test_registration_input_validation(self, client):
        """Test registration input validation"""
        # Test XSS in username
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': '<script>alert("xss")</script>'
        })
        
        # Should succeed but username should be sanitized
        assert response.status_code in [201, 400, 409]

    def test_registration_email_validation(self, client):
        """Test email format validation in registration"""
        # Invalid email formats
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user@domain',
            '',
            'user..name@domain.com',
            'user@domain..com'
        ]
        
        for email in invalid_emails:
            response = client.post('/api/auth/register', json={
                'email': email,
                'password': 'TestPassword123!',
                'username': 'testuser'
            })
            
            assert response.status_code == 400
            assert 'Invalid email format' in response.get_json()['error']

    def test_registration_password_strength(self, client):
        """Test password strength validation"""
        weak_passwords = [
            'short',           # Too short
            'nouppercase123!', # No uppercase
            'NOLOWERCASE123!', # No lowercase
            'NoNumbers!',      # No numbers
            'NoSpecialChars123' # No special chars
        ]
        
        for password in weak_passwords:
            response = client.post('/api/auth/register', json={
                'email': f'test{password}@example.com',
                'password': password,
                'username': f'testuser{password}'
            })
            
            assert response.status_code == 400
            error_data = response.get_json()
            assert 'Password does not meet security requirements' in error_data['error']
            assert 'details' in error_data

    def test_login_input_validation(self, client):
        """Test login input validation"""
        # Register a user first
        client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': 'testuser'
        })
        
        # Test invalid email format
        response = client.post('/api/auth/login', json={
            'email': 'invalid-email',
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 400
        assert 'Invalid email format' in response.get_json()['error']

    def test_password_reset_email_validation(self, client):
        """Test password reset email validation"""
        # Test invalid email format
        response = client.post('/api/password/reset', json={
            'email': 'invalid-email'
        })
        
        assert response.status_code == 400
        assert 'Invalid email format' in response.get_json()['error']

    def test_password_reset_verification_validation(self, client):
        """Test password reset verification validation"""
        # Test weak password
        response = client.post('/api/password/reset/verify', json={
            'token': 'fake-token',
            'new_password': 'weak'
        })
        
        assert response.status_code == 400
        error_data = response.get_json()
        assert 'Password does not meet security requirements' in error_data['error']

    def test_job_application_input_validation(self, client, auth_headers):
        """Test job application input validation"""
        # Create a job first
        job_response = client.post('/api/recruiter/jobs', 
                                 json={
                                     'title': 'Test Job',
                                     'description': 'Test job description',
                                     'location': 'Test City',
                                     'employment_type': 'full-time',
                                     'seniority': 'mid',
                                     'work_mode': 'remote',
                                     'salary_min': 50000,
                                     'salary_max': 70000
                                 },
                                 headers=auth_headers)
        job_id = job_response.get_json()['id']
        
        # Test XSS in application data
        malicious_data = {
            'first_name': '<script>alert("xss")</script>',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'current_company': '<img src=x onerror=alert("xss")>',
            'current_position': 'Developer',
            'experience': '5 years',
            'education': 'Bachelor Degree',
            'skills': 'Python, Flask',
            'availability': 'Immediate',
            'salary_expectation': '60000',
            'notice_period': '2 weeks',
            'work_authorization': 'Yes',
            'relocation': 'No',
            'additional_info': 'Additional information'
        }
        
        # Create valid files
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        files = {
            'resume': ('test.pdf', pdf_content, 'application/pdf'),
            'coverLetter': ('cover.pdf', pdf_content, 'application/pdf')
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=malicious_data,
                                 files=files,
                                 headers=auth_headers)
            
            # Should succeed but input should be sanitized
            assert response.status_code in [201, 400]

    def test_job_application_email_validation(self, client, auth_headers):
        """Test email validation in job applications"""
        # Create a job first
        job_response = client.post('/api/recruiter/jobs', 
                                 json={
                                     'title': 'Test Job',
                                     'description': 'Test job description',
                                     'location': 'Test City',
                                     'employment_type': 'full-time',
                                     'seniority': 'mid',
                                     'work_mode': 'remote',
                                     'salary_min': 50000,
                                     'salary_max': 70000
                                 },
                                 headers=auth_headers)
        job_id = job_response.get_json()['id']
        
        # Test invalid email in application
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'phone': '1234567890'
        }
        
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        files = {
            'resume': ('test.pdf', pdf_content, 'application/pdf'),
            'coverLetter': ('cover.pdf', pdf_content, 'application/pdf')
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'Invalid form data' in response.get_json()['error']

    def test_application_status_update_validation(self, client, auth_headers):
        """Test input validation in application status updates"""
        # Create a job and application first
        job_response = client.post('/api/recruiter/jobs', 
                                 json={
                                     'title': 'Test Job',
                                     'description': 'Test job description',
                                     'location': 'Test City',
                                     'employment_type': 'full-time',
                                     'seniority': 'mid',
                                     'work_mode': 'remote',
                                     'salary_min': 50000,
                                     'salary_max': 70000
                                 },
                                 headers=auth_headers)
        job_id = job_response.get_json()['id']
        
        # Create application
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        files = {
            'resume': ('test.pdf', pdf_content, 'application/pdf'),
            'coverLetter': ('cover.pdf', pdf_content, 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            app_response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                     data=data,
                                     files=files,
                                     headers=auth_headers)
            application_id = app_response.get_json()['application_id']
        
        # Test XSS in status update
        malicious_data = {
            'status': 'reviewed',
            'notes': '<script>alert("xss")</script>',
            'feedback': '<img src=x onerror=alert("xss")>'
        }
        
        response = client.patch(f'/api/applications/{application_id}/status',
                              json=malicious_data,
                              headers=auth_headers)
        
        # Should succeed but input should be sanitized
        assert response.status_code in [200, 400]

    def test_query_parameter_validation(self, client, auth_headers):
        """Test query parameter validation"""
        # Test invalid page parameter
        response = client.get('/api/applications/my-applications?page=-1',
                            headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Invalid query parameters' in response.get_json()['error']

    def test_route_parameter_validation(self, client, auth_headers):
        """Test route parameter validation"""
        # Test invalid job ID
        response = client.get('/api/applications/jobs/invalid-id/applications',
                            headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Invalid job ID' in response.get_json()['error']

    def test_string_length_limits(self, client):
        """Test string length limits"""
        # Test very long username
        long_username = 'x' * 1000
        
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'username': long_username
        })
        
        # Should succeed but username should be truncated
        assert response.status_code in [201, 400, 409]

    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        # Test SQL injection attempts in registration
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for attempt in sql_injection_attempts:
            response = client.post('/api/auth/register', json={
                'email': f'test{attempt}@example.com',
                'password': 'TestPassword123!',
                'username': f'testuser{attempt}'
            })
            
            # Should not cause SQL errors
            assert response.status_code in [201, 400, 409]

    def test_path_traversal_prevention(self, client, auth_headers):
        """Test path traversal prevention"""
        # Test path traversal in file download
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\config\\sam',
            '....//....//....//etc/passwd'
        ]
        
        for path in malicious_paths:
            response = client.get(f'/api/applications/{path}/resume',
                                headers=auth_headers)
            
            # Should not allow path traversal
            assert response.status_code in [400, 404]

    def test_content_type_validation(self, client):
        """Test content type validation"""
        # Test with wrong content type
        response = client.post('/api/auth/register',
                             data='{"email":"test@example.com","password":"TestPassword123!","username":"testuser"}',
                             content_type='text/plain')
        
        assert response.status_code == 400

    def test_empty_request_body(self, client):
        """Test handling of empty request body"""
        response = client.post('/api/auth/register',
                             json={})
        
        assert response.status_code == 400
        assert 'Invalid registration data' in response.get_json()['error']

    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post('/api/auth/register',
                             data='{"email":"test@example.com","password":"TestPassword123!","username":"testuser"',
                             content_type='application/json')
        
        assert response.status_code == 400
