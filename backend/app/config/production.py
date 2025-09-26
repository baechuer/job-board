from .base import BaseConfig

class ProductionConfig(BaseConfig):
    DEBUG = False
    
    # Enhanced security for production
    SECRET_KEY = None  # Must be set via environment variable
    JWT_SECRET_KEY = None  # Must be set via environment variable
    
    # Stricter rate limiting for production
    RATELIMIT_DEFAULT = "100 per day, 20 per hour"
    
    # Enhanced CORS for production
    CORS_ORIGINS = None  # Must be set via environment variable
    
    # Enhanced security headers for production
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    # Enable virus scanning in production
    ENABLE_VIRUS_SCAN = True
    
    # Stricter file upload limits
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ["pdf", "doc", "docx"]  # Only most common types
    
    # Database security
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require'
        }
    }