from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from . import auth_bp
from ...services.auth_service import register_user, authenticate
from ...extensions import db
from ...models.user import User
from sqlalchemy import select
from ...schemas.auth_schema import RegisterSchema, LoginSchema

_register = RegisterSchema()
_login = LoginSchema()

@auth_bp.post("/register")
def register():
    data = _register.load(request.get_json() or {})
    user = register_user(data["email"], data["password"], data["username"])
    return jsonify(id=user.id, email=user.email), 201

@auth_bp.post("/login")
def login():
    data = _login.load(request.get_json() or {})
    user = authenticate(data["email"], data["password"])
    if not user:
        return jsonify(error="invalid credentials"), 401
    # Use user id as identity (subject) and put email in additional claims
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"email": user.email},
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify(msg="Logged out successfully"), 200

@auth_bp.get("/me")
@jwt_required()
def me():
    claims = get_jwt()
    user = {"id": get_jwt_identity(), "email": claims.get("email")}
    return jsonify(user=user)

@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    # Read fresh email from DB to ensure claim presence
    user = db.session.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
    email = user.email if user else None
    new_access = create_access_token(
        identity=str(user_id),
        additional_claims={"email": email} if email else None,
    )
    return jsonify(access_token=new_access), 200

@auth_bp.post("/logout_all")
@jwt_required()
def logout_all():
    user_id = get_jwt_identity()
    user = db.session.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
    if not user:
        return jsonify(error="user not found"), 404
    from datetime import datetime, UTC
    # Set to current time; blocklist loader will treat tokens with iat <= this as invalid
    user.last_logout_at = datetime.now(UTC)
    db.session.commit()
    return jsonify(msg="logged out from all devices"), 200
