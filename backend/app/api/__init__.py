from flask import Blueprint
from .auth import auth_bp
from .recruiter_requests import recruiter_requests_bp
from .admin import admin_bp

def register_api(app):
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(recruiter_requests_bp)
    api_bp.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)