"""
Test cases for security utilities including file validation, input sanitization, and virus scanning.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage
from io import BytesIO

from app.common.security_utils import (
    validate_file_type,
    validate_file_content,
    validate_pdf_content,
    validate_document_content,
    validate_text_content,
    scan_file_for_viruses,
    calculate_file_hash,
    sanitize_filename,
    validate_and_process_upload,
    cleanup_temp_file,
    sanitize_string_input,
    validate_email_format,
    validate_password_strength,
    FileValidationError,
    VirusScanError,
    ALLOWED_FILE_TYPES,
    DANGEROUS_EXTENSIONS,
    SUSPICIOUS_PATTERNS
)


class TestFileValidation:
    """Test file type and content validation"""

    def test_validate_file_type_pdf_valid(self):
        """Test valid PDF file validation"""
        # Create a mock PDF file
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj'
        file_storage = FileStorage(
            stream=BytesIO(pdf_content),
            filename='test.pdf',
            content_type='application/pdf'
        )
        
        is_valid, error_msg = validate_file_type(file_storage, ['pdf'])
        assert is_valid is True
        assert error_msg == ""

    def test_validate_file_type_dangerous_extension(self):
        """Test validation rejects dangerous file extensions"""
        file_storage = FileStorage(
            stream=BytesIO(b'fake executable content'),
            filename='malware.exe',
            content_type='application/octet-stream'
        )
        
        is_valid, error_msg = validate_file_type(file_storage, ['pdf'])
        assert is_valid is False
        assert "Dangerous file type" in error_msg

    def test_validate_file_type_size_limit(self):
        """Test file size validation"""
        # Create a custom file-like object with content_length property
        class MockFileStorage:
            def __init__(self, content, filename, content_type, content_length):
                self.stream = BytesIO(content)
                self.filename = filename
                self.content_type = content_type
                self._content_length = content_length
            
            @property
            def content_length(self):
                return self._content_length
            
            def seek(self, pos):
                self.stream.seek(pos)
            
            def read(self, size=-1):
                return self.stream.read(size)
        
        # Create a large file (simulate)
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        file_storage = MockFileStorage(
            content=large_content,
            filename='large.pdf',
            content_type='application/pdf',
            content_length=11 * 1024 * 1024
        )
        
        is_valid, error_msg = validate_file_type(file_storage, ['pdf'])
        assert is_valid is False
        assert "exceeds maximum allowed size" in error_msg

    def test_validate_file_type_wrong_mime(self):
        """Test MIME type validation"""
        file_storage = FileStorage(
            stream=BytesIO(b'fake pdf content'),
            filename='test.pdf',
            content_type='text/plain'  # Wrong MIME type
        )
        
        is_valid, error_msg = validate_file_type(file_storage, ['pdf'])
        assert is_valid is False
        assert "File content validation failed" in error_msg

    def test_validate_pdf_content_valid(self):
        """Test valid PDF content validation"""
        valid_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj'
        assert validate_pdf_content(valid_pdf) is True

    def test_validate_pdf_content_invalid_header(self):
        """Test invalid PDF header"""
        invalid_pdf = b'Not a PDF file'
        assert validate_pdf_content(invalid_pdf) is False

    def test_validate_pdf_content_javascript(self):
        """Test PDF with JavaScript is rejected"""
        malicious_pdf = b'%PDF-1.4\n/JavaScript\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        assert validate_pdf_content(malicious_pdf) is False

    def test_validate_document_content_macros(self):
        """Test document with macros is rejected"""
        doc_with_macros = b'Microsoft Word Document with VBA macros'
        assert validate_document_content(doc_with_macros) is False

    def test_validate_text_content_suspicious_urls(self):
        """Test text content with suspicious URLs"""
        suspicious_text = b'Check out this link: https://bit.ly/suspicious'
        assert validate_text_content(suspicious_text) is False

    def test_validate_text_content_valid(self):
        """Test valid text content"""
        valid_text = b'This is a normal text document with no suspicious content.'
        assert validate_text_content(valid_text) is True


class TestFileSecurity:
    """Test file security features"""

    @patch('subprocess.run')
    def test_scan_file_for_viruses_clean(self, mock_run):
        """Test virus scanning with clean file"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b'clean content')
            temp_file.flush()
            
            is_clean, error_msg = scan_file_for_viruses(temp_file.name)
            assert is_clean is True
            assert error_msg == ""

    @patch('subprocess.run')
    def test_scan_file_for_viruses_infected(self, mock_run):
        """Test virus scanning with infected file"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "Virus detected: EICAR-Test-File"
        
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b'infected content')
            temp_file.flush()
            
            is_clean, error_msg = scan_file_for_viruses(temp_file.name)
            assert is_clean is False
            assert "Virus detected" in error_msg

    @patch('subprocess.run', side_effect=FileNotFoundError)
    def test_scan_file_for_viruses_no_clamav(self, mock_run):
        """Test virus scanning when ClamAV is not available"""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b'content')
            temp_file.flush()
            
            is_clean, error_msg = scan_file_for_viruses(temp_file.name)
            assert is_clean is True  # Should skip scan if ClamAV not available
            assert error_msg == ""

    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        with tempfile.NamedTemporaryFile() as temp_file:
            content = b'Test content for hashing'
            temp_file.write(content)
            temp_file.flush()
            
            file_hash = calculate_file_hash(temp_file.name)
            assert len(file_hash) == 64  # SHA-256 hash length
            assert isinstance(file_hash, str)

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test dangerous characters
        dangerous_name = "../../../etc/passwd"
        sanitized = sanitize_filename(dangerous_name)
        assert ".." not in sanitized
        assert "/" not in sanitized
        
        # Test empty filename
        empty_name = ""
        sanitized = sanitize_filename(empty_name)
        assert sanitized == "unnamed_file"
        
        # Test long filename
        long_name = "a" * 300 + ".pdf"
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) <= 255


class TestInputValidation:
    """Test input validation and sanitization"""

    def test_sanitize_string_input(self):
        """Test string input sanitization"""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = sanitize_string_input(malicious_input)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        
        # Test length limit
        long_input = "x" * 2000
        sanitized = sanitize_string_input(long_input, max_length=100)
        assert len(sanitized) <= 100

    def test_validate_email_format(self):
        """Test email format validation"""
        # Valid emails
        assert validate_email_format("user@example.com") is True
        assert validate_email_format("test.user+tag@domain.co.uk") is True
        
        # Invalid emails
        assert validate_email_format("invalid-email") is False
        assert validate_email_format("@domain.com") is False
        assert validate_email_format("user@") is False
        assert validate_email_format("") is False

    def test_validate_password_strength(self):
        """Test password strength validation"""
        # Strong password
        strong_password = "StrongPass123!"
        is_strong, issues = validate_password_strength(strong_password)
        assert is_strong is True
        assert len(issues) == 0
        
        # Weak passwords
        weak_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123"  # No special chars
        ]
        
        for weak_password in weak_passwords:
            is_strong, issues = validate_password_strength(weak_password)
            assert is_strong is False
            assert len(issues) > 0


class TestFileUploadSecurity:
    """Test comprehensive file upload security"""

    @patch('app.common.security_utils.scan_file_for_viruses')
    def test_validate_and_process_upload_success(self, mock_scan):
        """Test successful file upload validation"""
        mock_scan.return_value = (True, "")
        
        file_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        file_storage = FileStorage(
            stream=BytesIO(file_content),
            filename='test.pdf',
            content_type='application/pdf'
        )
        
        result = validate_and_process_upload(file_storage, ['pdf'])
        
        assert result['is_valid'] is True
        assert result['filename'] == 'test.pdf'
        assert 'file_hash' in result
        assert 'temp_path' in result
        
        # Clean up
        cleanup_temp_file(result['temp_path'])

    def test_validate_and_process_upload_no_file(self):
        """Test validation with no file"""
        with pytest.raises(FileValidationError) as exc_info:
            validate_and_process_upload(None, ['pdf'])
        assert "No file provided" in str(exc_info.value)

    def test_validate_and_process_upload_invalid_type(self):
        """Test validation with invalid file type"""
        file_storage = FileStorage(
            stream=BytesIO(b'executable content'),
            filename='malware.exe',
            content_type='application/octet-stream'
        )
        
        with pytest.raises(FileValidationError) as exc_info:
            validate_and_process_upload(file_storage, ['pdf'])
        assert "Dangerous file type" in str(exc_info.value)

    @patch('app.common.security_utils.scan_file_for_viruses')
    def test_validate_and_process_upload_virus_detected(self, mock_scan):
        """Test validation with virus detected"""
        mock_scan.return_value = (False, "Virus detected: EICAR-Test-File")
        
        file_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj'
        file_storage = FileStorage(
            stream=BytesIO(file_content),
            filename='test.pdf',
            content_type='application/pdf'
        )
        
        with pytest.raises(VirusScanError) as exc_info:
            validate_and_process_upload(file_storage, ['pdf'])
        assert "Virus detected" in str(exc_info.value)


class TestSecurityConstants:
    """Test security constants and configurations"""

    def test_allowed_file_types(self):
        """Test allowed file types configuration"""
        assert 'pdf' in ALLOWED_FILE_TYPES
        assert 'doc' in ALLOWED_FILE_TYPES
        assert 'docx' in ALLOWED_FILE_TYPES
        assert 'txt' in ALLOWED_FILE_TYPES
        
        # Check MIME types
        assert 'application/pdf' in ALLOWED_FILE_TYPES['pdf']
        assert 'application/msword' in ALLOWED_FILE_TYPES['doc']

    def test_dangerous_extensions(self):
        """Test dangerous file extensions"""
        assert '.exe' in DANGEROUS_EXTENSIONS
        assert '.bat' in DANGEROUS_EXTENSIONS
        assert '.js' in DANGEROUS_EXTENSIONS
        assert '.php' in DANGEROUS_EXTENSIONS
        assert '.py' in DANGEROUS_EXTENSIONS

    def test_suspicious_patterns(self):
        """Test suspicious content patterns"""
        assert b'<script' in SUSPICIOUS_PATTERNS
        assert b'javascript:' in SUSPICIOUS_PATTERNS
        assert b'eval(' in SUSPICIOUS_PATTERNS
        assert b'exec(' in SUSPICIOUS_PATTERNS
        assert b'include(' in SUSPICIOUS_PATTERNS
