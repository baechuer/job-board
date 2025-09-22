from flask import request, jsonify, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from . import auth_bp
from ...services.auth_service import register_user, authenticate, reset_password as svc_reset_password
from ...extensions import db, mail
from ...models.user import User
from sqlalchemy import select
from ...schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    ResetPasswordRequestSchema,
    VerifyResetPasswordSchema,
)
from datetime import datetime, UTC
from ...models.revoked_token import RevokedToken
from ...common.security import (
    generate_email_token,
    verify_email_token,
    generate_reset_token,
    verify_reset_token,
)
from flask_mail import Message
from marshmallow import ValidationError

_register = RegisterSchema()
_login = LoginSchema()
_reset_req = ResetPasswordRequestSchema()
_verify_reset = VerifyResetPasswordSchema()


@auth_bp.post("/register")
def register():
    data = _register.load(request.get_json() or {})
    user = register_user(data["email"], data["password"], data["username"])
    # Send verification link token (in real app, send via email)
    token = generate_email_token(user.email)

    # Build verification link (relative URL to avoid SERVER_NAME requirement in tests)
    verify_path = url_for("api.auth.verify_email", token=token, _external=False)

    # Send email (will be suppressed in tests via MAIL_SUPPRESS_SEND)
    try:
        msg = Message(
            subject="Confirm Your Email",
            recipients=[user.email],
            body=f"Your verification link is {verify_path}",
        )
        mail.send(msg)
    except Exception:
        # Do not fail registration if email backend is misconfigured; tests suppress send
        pass

    return jsonify(id=user.id, email=user.email, verify_token=token), 201

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

 

@auth_bp.get("/me")
@jwt_required()
def me():
    claims = get_jwt()
    user_id = int(get_jwt_identity())
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one()
    roles = [{"role": r.role} for r in user.roles.all()]  # dynamic relationship
    return jsonify(user={
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "roles": roles,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    })

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

@auth_bp.get("/verify")
def verify_email():
    token = request.args.get("token", "")
    email = verify_email_token(token)
    if not email:
        return jsonify(error="invalid or expired token"), 400
    user = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if not user:
        return jsonify(error="user not found"), 404
    if not user.is_verified:
        user.is_verified = True
        user.email_verified_at = datetime.now(UTC)
        db.session.commit()
    return jsonify(msg="email verified"), 200

@auth_bp.post("/logout_refresh")
@jwt_required(refresh=True)
def logout_refresh():
    # Revoke this refresh token by its JTI
    payload = get_jwt()
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        expires_at = datetime.fromtimestamp(int(exp), UTC)
        if not db.session.get(RevokedToken, jti):
            db.session.add(RevokedToken(jti=jti, expires_at=expires_at))
            db.session.commit()
    return jsonify(msg="refresh token logged out"), 200

@auth_bp.post("/logout")
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    user = db.session.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()
    if not user:
        return jsonify(error="user not found"), 404
    # Per-device logout: revoke only this token by its JTI with TTL
    jti = get_jwt().get("jti")
    exp = get_jwt().get("exp")
    if jti and exp:
        expires_at = datetime.fromtimestamp(int(exp), UTC)
        if not db.session.get(RevokedToken, jti):
            db.session.add(RevokedToken(jti=jti, expires_at=expires_at))
    db.session.commit()
    return jsonify(msg="logged out"), 200




@auth_bp.post("/password/reset")
def reset_password():
    """Accepts email, sends a password reset link to that email if user exists."""
    try:
        data = _reset_req.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="invalid payload", details=e.messages), 400

    email = data["email"].strip()
    # Always respond 200 to avoid user enumeration, but only send mail if user exists
    user = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user:
        token = generate_reset_token(email)
        reset_path = url_for("api.auth.verify_reset_password", _external=False)
        # Frontend will submit token+new_password to verify_reset_password; include token in link for UX
        link = f"{reset_path}?token={token}"
        try:
            msg = Message(
                subject="Reset Your Password",
                recipients=[email],
                body=f"Reset your password using this link: {link}"
            )
            mail.send(msg)
        except Exception:
            pass
    return jsonify(msg="if the email exists, a reset link has been sent"), 200


@auth_bp.post("/password/reset/verify")
def verify_reset_password():
    """Validates reset token and sets a new password. Expects JSON: { token, new_password }."""
    try:
        data = _verify_reset.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="invalid payload", details=e.messages), 400

    token = (data.get("token") or "").strip()
    new_password = (data.get("new_password") or "").strip()

    email = verify_reset_token(token)
    if not email:
        return jsonify(error="invalid or expired token"), 400

    svc_reset_password(email, new_password)
    return jsonify(msg="password updated"), 200
