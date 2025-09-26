# Security Implementation Guide

This document outlines the comprehensive security features implemented in the Flask job board application.

## Overview

The application now includes multiple layers of security to protect against common web vulnerabilities and attacks.

## Implemented Security Features

### 1. Input Validation

**Location**: All API endpoints
**Implementation**: 
- Marshmallow schemas for structured data validation
- Custom input sanitization functions
- Parameter validation for all route parameters
- Email format validation
- Password strength validation

**Key Functions**:
- `sanitize_string_input()`: Prevents XSS attacks by escaping dangerous characters
- `validate_email_format()`: Ensures proper email format
- `validate_password_strength()`: Enforces strong password requirements

**Example**:
```python
# Input sanitization
data["username"] = sanitize_string_input(username, max_length=50)

# Password strength validation
is_strong, password_issues = validate_password_strength(password)
if not is_strong:
    return jsonify(error="Password does not meet security requirements", details=password_issues), 400
```

### 2. File Type Validation and Virus Scanning

**Location**: `app/common/security_utils.py`
**Implementation**:
- MIME type detection using python-magic
- File extension validation
- Content-based validation for different file types
- Virus scanning integration with ClamAV
- File size limits
- Suspicious pattern detection

**Supported File Types**:
- PDF documents
- Microsoft Word documents (.doc, .docx)
- Text files (.txt)
- Rich Text Format (.rtf)
- OpenDocument Text (.odt)

**Security Checks**:
- Dangerous file extension blocking
- JavaScript detection in PDFs
- Macro detection in documents
- Suspicious URL detection
- File content pattern analysis

**Example**:
```python
# Comprehensive file validation
resume_info = validate_and_process_upload(resume_file, allowed_types)
```

### 3. Rate Limiting

**Location**: All API endpoints
**Implementation**: Flask-Limiter with Redis/memory backend

**Rate Limits Applied**:
- Registration: 5 per hour
- Login: 10 per hour
- Password reset: 3 per hour
- Password reset verification: 5 per hour
- Job applications: 5 per hour
- File downloads: 20 per hour
- File viewing: 30 per hour
- Profile access: 30 per hour
- Token refresh: 20 per hour
- Logout: 20 per hour

**Example**:
```python
@limiter.limit("5 per hour")  # Rate limit job applications
def apply_for_job(job_id):
    # Endpoint implementation
```

### 4. CORS Configuration

**Location**: `app/__init__.py` and `app/config/`
**Implementation**: Environment-specific CORS settings

**Development Configuration**:
```python
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
)
```

**Production Configuration**:
- Strict origin validation
- Credential support
- Limited header exposure
- Environment variable configuration

### 5. Security Headers

**Location**: `app/__init__.py`
**Implementation**: Middleware that adds security headers to all responses

**Headers Applied**:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy`: Restricts resource loading
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy`: Restricts browser features

**Example**:
```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    security_headers = app.config.get('SECURITY_HEADERS', {})
    for header, value in security_headers.items():
        response.headers[header] = value
    return response
```

### 6. Request Size Limiting

**Location**: `app/__init__.py`
**Implementation**: Global request size limits

**Configuration**:
- Maximum content length: 10MB (development), 5MB (production)
- File upload limits enforced
- Request body size validation

### 7. Enhanced Authentication Security

**Location**: `app/api/auth/routes.py`
**Implementation**:
- JWT token management
- Token revocation on logout
- Per-device logout support
- Email verification requirements
- Secure password reset flow

## Configuration

### Environment Variables

**Security Configuration**:
```bash
# Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/0
RATELIMIT_DEFAULT="200 per day, 50 per hour"

# File Upload Security
MAX_CONTENT_LENGTH=10485760  # 10MB
UPLOAD_FOLDER=/path/to/uploads
ALLOWED_EXTENSIONS="pdf,doc,docx,txt,rtf,odt"

# CORS Settings
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Virus Scanning
ENABLE_VIRUS_SCAN=true
CLAMSCAN_PATH=/usr/bin/clamscan

# Input Validation
MAX_STRING_LENGTH=1000
MAX_EMAIL_LENGTH=254
MAX_PASSWORD_LENGTH=128
```

### Production Deployment

**Required Environment Variables**:
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
CORS_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@host:port/db
RATELIMIT_STORAGE_URL=redis://redis-host:6379/0
```

## Security Best Practices Implemented

### 1. Defense in Depth
- Multiple layers of security controls
- Input validation at multiple points
- File validation before and after upload

### 2. Principle of Least Privilege
- Minimal CORS configuration
- Restricted file type access
- Limited API endpoint exposure

### 3. Fail Secure
- Default deny policies
- Secure error handling
- Graceful degradation

### 4. Input Validation
- Whitelist approach for file types
- Comprehensive input sanitization
- Parameter validation

### 5. Rate Limiting
- Prevents brute force attacks
- Protects against DoS
- Resource consumption control

## Monitoring and Logging

**Security Events Logged**:
- Failed authentication attempts
- File validation failures
- Rate limit violations
- Suspicious file uploads
- Input validation errors

**Log Levels**:
- ERROR: Security violations and failures
- WARNING: Suspicious activities
- INFO: Security events and validations

## Testing Security Features

### Manual Testing
1. **File Upload Security**:
   - Upload malicious files
   - Test file type validation
   - Verify virus scanning

2. **Rate Limiting**:
   - Exceed rate limits
   - Verify blocking behavior
   - Test different endpoints

3. **Input Validation**:
   - Submit malicious input
   - Test XSS prevention
   - Verify SQL injection protection

4. **CORS Configuration**:
   - Test cross-origin requests
   - Verify credential handling
   - Test header restrictions

### Automated Testing
- Unit tests for security utilities
- Integration tests for endpoints
- Security-focused test cases

## Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Update virus definitions
- Review rate limits

### Monitoring
- Monitor failed authentication attempts
- Track file upload patterns
- Watch for unusual traffic patterns
- Review security logs regularly

## Troubleshooting

### Common Issues

1. **Rate Limiting Too Strict**:
   - Adjust limits in configuration
   - Check Redis connectivity
   - Verify client IP detection

2. **File Upload Failures**:
   - Check file type configuration
   - Verify virus scanner availability
   - Review file size limits

3. **CORS Issues**:
   - Verify origin configuration
   - Check header settings
   - Review credential handling

4. **Security Headers**:
   - Verify header configuration
   - Check CSP policy
   - Review browser compatibility

## Security Checklist

- [ ] All endpoints have rate limiting
- [ ] Input validation implemented
- [ ] File upload security enabled
- [ ] CORS properly configured
- [ ] Security headers applied
- [ ] Authentication secured
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Environment variables set
- [ ] Dependencies updated
- [ ] Security tests passing
- [ ] Monitoring in place

## Conclusion

This comprehensive security implementation provides multiple layers of protection against common web vulnerabilities. Regular maintenance, monitoring, and updates are essential to maintain security effectiveness.
