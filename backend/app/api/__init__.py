from flask import Blueprint
from .auth import auth_bp
from .recruiter_requests import recruiter_requests_bp
from .recruiter import recruiter_bp
from .candidate import candidate_bp
from .admin import admin_bp
from .applications import application_bp
from .monitoring.routes import monitoring_bp

def register_api(app):
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')
    api_bp.register_blueprint(recruiter_requests_bp)
    api_bp.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    api_bp.register_blueprint(candidate_bp, url_prefix='/candidate')
    api_bp.register_blueprint(admin_bp)
    api_bp.register_blueprint(application_bp, url_prefix='/applications')
    api_bp.register_blueprint(monitoring_bp)

    # Aliases to support tests that call /api/password/*
    @api_bp.post('/password/reset')
    def _alias_password_reset():
        from flask import current_app
        return current_app.view_functions['api.auth.reset_password']()

    @api_bp.post('/password/reset/verify')
    def _alias_password_reset_verify():
        from flask import current_app
        return current_app.view_functions['api.auth.verify_reset_password']()
    app.register_blueprint(api_bp)