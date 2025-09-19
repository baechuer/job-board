from flask import Flask
from .extensions import db, migrate, jwt, bcrypt
from flask_jwt_extended import JWTManager
from sqlalchemy import select
from .models.user import User
from .config.development import DevConfig
from .api import register_api
from .common.errors import register_error_handlers
from . import models


def create_app(config_object=DevConfig) -> Flask:
    """Application factory."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.from_pyfile("config.py", silent=True)  # instance/config.py (git-ignored)

    # Bind extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Enforce per-user token_version without external storage
    @jwt.token_in_blocklist_loader
    def check_token_iat(jwt_header, jwt_payload):
        user_id = jwt_payload.get("sub")
        token_iat = jwt_payload.get("iat")
        if not user_id or not token_iat:
            return True
        try:
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

    # Errors + API
    register_error_handlers(app)
    register_api(app)
    # Create tables if they don’t exist (quick dev hack, not for prod)
    with app.app_context():
        db.create_all()
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
