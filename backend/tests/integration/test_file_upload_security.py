"""
Test cases for file upload security including type validation, virus scanning, and content validation.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO

from app import create_app
from app.extensions import db
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from conftest import TestConfig


class TestFileUploadSecurity:
    """Test file upload security features"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        config = TestConfig()
        config.UPLOAD_FOLDER = tempfile.mkdtemp()
        config.ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']
        config.MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
        
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

    @pytest.fixture
    def job_id(self, client, auth_headers):
        """Create a test job and return its ID"""
        response = client.post('/api/recruiter/jobs', 
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
        return response.get_json()['id']

    def test_valid_pdf_upload(self, client, auth_headers, job_id):
        """Test uploading a valid PDF file"""
        # Create valid PDF content
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj'
        
        files = {
            'resume': ('test.pdf', BytesIO(pdf_content), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890',
            'current_company': 'Test Company',
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
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")  # No virus detected
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 201
            assert 'application_id' in response.get_json()

    def test_dangerous_file_extension_rejected(self, client, auth_headers, job_id):
        """Test that dangerous file extensions are rejected"""
        files = {
            'resume': ('malware.exe', BytesIO(b'executable content'), 'application/octet-stream'),
            'coverLetter': ('script.js', BytesIO(b'javascript code'), 'application/javascript')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        response = client.post(f'/api/applications/jobs/{job_id}/apply',
                             data=data,
                             files=files,
                             headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Dangerous file type' in response.get_json()['error']

    def test_file_size_limit_enforced(self, client, auth_headers, job_id):
        """Test that file size limits are enforced"""
        # Create large file content (6MB)
        large_content = b'x' * (6 * 1024 * 1024)
        
        files = {
            'resume': ('large.pdf', BytesIO(large_content), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(b'small content'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        response = client.post(f'/api/applications/jobs/{job_id}/apply',
                             data=data,
                             files=files,
                             headers=auth_headers)
        
        assert response.status_code == 400
        assert 'exceeds maximum allowed size' in response.get_json()['error']

    def test_virus_scanning_integration(self, client, auth_headers, job_id):
        """Test virus scanning integration"""
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        
        files = {
            'resume': ('test.pdf', BytesIO(pdf_content), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (False, "Virus detected: EICAR-Test-File")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'Virus scan failed' in response.get_json()['error']

    def test_malicious_pdf_content_rejected(self, client, auth_headers, job_id):
        """Test that PDFs with malicious content are rejected"""
        # PDF with JavaScript
        malicious_pdf = b'%PDF-1.4\n/JavaScript\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        
        files = {
            'resume': ('malicious.pdf', BytesIO(malicious_pdf), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'File validation failed' in response.get_json()['error']

    def test_document_with_macros_rejected(self, client, auth_headers, job_id):
        """Test that documents with macros are rejected"""
        # Document with VBA macros
        doc_with_macros = b'Microsoft Word Document with VBA macros'
        
        files = {
            'resume': ('document.doc', BytesIO(doc_with_macros), 'application/msword'),
            'coverLetter': ('cover.pdf', BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'File validation failed' in response.get_json()['error']

    def test_text_file_with_suspicious_content(self, client, auth_headers, job_id):
        """Test that text files with suspicious content are rejected"""
        # Text file with suspicious URLs
        suspicious_text = b'Check out this link: https://bit.ly/suspicious'
        
        files = {
            'resume': ('resume.txt', BytesIO(suspicious_text), 'text/plain'),
            'coverLetter': ('cover.pdf', BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'File validation failed' in response.get_json()['error']

    def test_missing_required_files(self, client, auth_headers, job_id):
        """Test that missing required files are handled"""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        # No files provided
        response = client.post(f'/api/applications/jobs/{job_id}/apply',
                             data=data,
                             headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Resume is required' in response.get_json()['error']

    def test_empty_filename_rejected(self, client, auth_headers, job_id):
        """Test that files with empty filenames are rejected"""
        files = {
            'resume': ('', BytesIO(b'content'), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        response = client.post(f'/api/applications/jobs/{job_id}/apply',
                             data=data,
                             files=files,
                             headers=auth_headers)
        
        assert response.status_code == 400
        assert 'Resume is required' in response.get_json()['error']

    def test_file_type_mismatch(self, client, auth_headers, job_id):
        """Test that file type mismatches are detected"""
        # File with .pdf extension but wrong MIME type
        files = {
            'resume': ('test.pdf', BytesIO(b'not a pdf'), 'text/plain'),
            'coverLetter': ('cover.pdf', BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'File validation failed' in response.get_json()['error']

    def test_multiple_file_validation(self, client, auth_headers, job_id):
        """Test validation of multiple files in one request"""
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        
        files = {
            'resume': ('resume.pdf', BytesIO(pdf_content), 'application/pdf'),
            'coverLetter': ('cover.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '1234567890'
        }
        
        with patch('app.common.security_utils.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, "")
            
            response = client.post(f'/api/applications/jobs/{job_id}/apply',
                                 data=data,
                                 files=files,
                                 headers=auth_headers)
            
            assert response.status_code == 201
            # Verify both files were processed
            assert mock_scan.call_count == 2  # Called twice for both files
