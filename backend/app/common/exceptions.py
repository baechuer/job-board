class BusinessLogicError(Exception):
    """Custom exception for business logic errors that should be shown to the frontend"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        self.description = message  # This will be picked up by the error handler
        super().__init__(self.message)

class ValidationError(BusinessLogicError):
    """Custom validation error"""
    def __init__(self, message: str):
        super().__init__(message, 400)

class AuthenticationError(BusinessLogicError):
    """Custom authentication error"""
    def __init__(self, message: str):
        super().__init__(message, 401)

class AuthorizationError(BusinessLogicError):
    """Custom authorization error"""
    def __init__(self, message: str):
        super().__init__(message, 403)

class ResourceNotFoundError(BusinessLogicError):
    """Custom resource not found error"""
    def __init__(self, message: str):
        super().__init__(message, 404)

class ConflictError(BusinessLogicError):
    """Custom conflict error (e.g., email already exists)"""
    def __init__(self, message: str):
        super().__init__(message, 409)
