from .base import BaseConfig

class DevConfig(BaseConfig):
    DEBUG = True
    # Disable mail sending in development to prevent SMTP timeouts
    MAIL_SUPPRESS_SEND = True
    # Use simpler rate limiting for development
    RATELIMIT_STORAGE_URL = "memory://"
    # Disable virus scanning in development
    ENABLE_VIRUS_SCAN = False
    # Set development environment
    ENV = 'development'
