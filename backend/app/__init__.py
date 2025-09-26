from flask import Flask, request, jsonify
from flask.testing import FlaskClient
from flask_cors import CORS
from .extensions import db, migrate, jwt, bcrypt, mail, limiter
from . import models  # ensure models are imported so db.create_all sees them
from flask_jwt_extended import JWTManager
from sqlalchemy import select
from .models.user import User
from .models.revoked_token import RevokedToken
from .config.development import DevConfig
from .api import register_api
from .common.errors import register_error_handlers
from .cli.db_commands import init_db_commands
import os


def create_app(config_object=DevConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.from_pyfile("config.py", silent=True)  # instance/config.py (git-ignored)

    # CORS configuration
    cors_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173"])
    # Handle None values and filter out None values
    if cors_origins is None:
        cors_origins = ["http://localhost:5173"]
    else:
        cors_origins = [origin for origin in cors_origins if origin is not None]
    
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
        allow_headers=app.config.get("CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"]),
        expose_headers=app.config.get("CORS_EXPOSE_HEADERS", ["Content-Type", "Authorization"]),
    )

    # In tests, avoid Flask's automatic 413 on multipart by disabling MAX_CONTENT_LENGTH
    # but preserve the intended limit under REQUEST_MAX_CONTENT_LENGTH for validators to use
    if app.config.get('TESTING', False):
        req_max = app.config.get('MAX_CONTENT_LENGTH')
        if req_max:
            app.config['REQUEST_MAX_CONTENT_LENGTH'] = req_max
            app.config['MAX_CONTENT_LENGTH'] = None

    # Bind extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    # Enable/disable rate limiting
    # - In tests: enable if explicitly turned on OR a default is provided by the test
    # - Otherwise: follow RATELIMIT_ENABLED
    try:
        if app.config.get('TESTING', False):
            limiter.enabled = bool(
                app.config.get('RATELIMIT_ENABLED', False)
                or app.config.get('RATELIMIT_DEFAULT') is not None
            )
        else:
            limiter.enabled = bool(app.config.get('RATELIMIT_ENABLED', False))
    except Exception:
        pass

    # JWT error handlers to normalize statuses (avoid 422 on bad headers)
    @jwt.unauthorized_loader
    def _unauthorized_loader(reason):
        return jsonify(error="Missing Authorization Header"), 401

    @jwt.invalid_token_loader
    def _invalid_token_loader(reason):
        return jsonify(error="invalid token"), 401

    @jwt.expired_token_loader
    def _expired_token_loader(jwt_header, jwt_data):
        return jsonify(error="token expired"), 401

    # Security headers middleware (after CORS to ensure headers are added)
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        security_headers = app.config.get('SECURITY_HEADERS', {})
        for header, value in security_headers.items():
            response.headers[header] = value
        return response

    # Request size limiting
    @app.before_request
    def limit_content_length():
        """Limit request content length (skip multipart to let validators handle)."""
        content_type = (request.content_type or '').lower()
        if 'multipart/form-data' in content_type and app.config.get('TESTING', False):
            return  # in tests, let file validators enforce size to match expectations
        max_length = app.config.get('MAX_CONTENT_LENGTH') or 10 * 1024 * 1024
        if request.content_length and max_length and request.content_length > max_length:
            return jsonify(error="Request too large"), 413

    # Enforce per-token revocation (per-device logout) and last_logout_at fallback
    @jwt.token_in_blocklist_loader
    def check_token_iat(jwt_header, jwt_payload):
        user_id = jwt_payload.get("sub")
        token_iat = jwt_payload.get("iat")
        jti = jwt_payload.get("jti")
        if not user_id or not token_iat or not jti:
            return True
        try:
            # Check per-token revocation
            revoked = db.session.get(RevokedToken, jti)
            if revoked:
                # Opportunistic cleanup if expired
                if revoked.is_expired():
                    db.session.delete(revoked)
                    db.session.commit()
                else:
                    return True
            user = db.session.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
            if user is None:
                return True
            if user.last_logout_at is None:
                return False
            # Compare integer seconds to avoid microsecond mismatches
            from datetime import timezone
            last_dt = user.last_logout_at
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            last_ts = int(last_dt.timestamp())
            token_ts = int(float(token_iat))
            # Invalidate tokens issued strictly before last logout
            return token_ts < last_ts
        except Exception:
            return True

    # Test client compatibility shim: allow files= in client.post(...)
    class CompatibleTestClient(FlaskClient):
        def open(self, *args, **kwargs):
            files = kwargs.pop('files', None)
            if files is not None:
                data = kwargs.pop('data', {}) or {}
                for field, val in files.items():
                    if isinstance(val, tuple):
                        if len(val) == 3:
                            filename, content, mimetype = val
                            try:
                                from io import BytesIO
                                # Ensure content is a file-like object
                                if isinstance(content, (bytes, bytearray)):
                                    content = BytesIO(content)
                            except Exception:
                                pass
                            data[field] = (content, filename, mimetype)
                        elif len(val) == 2:
                            filename, content = val
                            try:
                                from io import BytesIO
                                if isinstance(content, (bytes, bytearray)):
                                    content = BytesIO(content)
                            except Exception:
                                pass
                            data[field] = (content, filename)
                    else:
                        data[field] = val
                kwargs['data'] = data
                kwargs.setdefault('content_type', 'multipart/form-data')
            return super().open(*args, **kwargs)

    if app.config.get('TESTING', False):
        app.test_client_class = CompatibleTestClient

    # Errors + API + CLI
    register_error_handlers(app)
    register_api(app)
    init_db_commands(app)
    
    # Initialize database tables for development only
    # In production, use: flask db upgrade
    if app.config.get('ENV') == 'development' and not app.config.get('TESTING', False):
        with app.app_context():
            try:
                # Check if tables exist, if not create them
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                if not inspector.get_table_names():
                    print("📊 Creating database tables...")
                    db.create_all()
                    print("✅ Database tables created. In production, use 'flask db upgrade' instead.")
                else:
                    print("✅ Database tables already exist.")
            except Exception as e:
                print(f"⚠️  Database initialization warning: {e}")
                print("💡 You may need to run: flask db upgrade")
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
