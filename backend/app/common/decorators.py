from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.user_role import UserRole
from sqlalchemy import select


def admin_required(f):
    """Decorator to require admin role for access to protected endpoints."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(error="User not found"), 404
        
        # Check if user has admin role
        admin_role = user.roles.filter(UserRole.role == 'admin').first()
        if not admin_role:
            return jsonify(error="Admin access required"), 403
        
        return f(*args, **kwargs)
    return decorated_function
