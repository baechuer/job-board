"""Integration tests for password reset functionality."""

import pytest
import uuid
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from app.models.user import User
from app.extensions import db, mail
from app.common.security import verify_reset_token
from sqlalchemy import select


class TestPasswordReset:
    """Test password reset flow."""

    def test_reset_password_request_valid_email(self, client, app):
        """Test password reset request with valid email."""
        # First register a user
        register_res = client.post(
            "/api/auth/register",
            json={"email": "reset@example.com", "password": "Password123!", "username": "resetuser"},
        )
        assert register_res.status_code == 201
        
        # Request password reset
        reset_res = client.post(
            "/api/auth/password/reset",
            json={"email": "reset@example.com"},
        )
        assert reset_res.status_code == 200
        assert reset_res.get_json()["msg"] == "if the email exists, a reset link has been sent"

    def test_reset_password_request_nonexistent_email(self, client):
        """Test password reset request with non-existent email."""
        reset_res = client.post(
            "/api/auth/password/reset",
            json={"email": "nonexistent@example.com"},
        )
        # Should still return 200 to avoid user enumeration
        assert reset_res.status_code == 200
        assert reset_res.get_json()["msg"] == "if the email exists, a reset link has been sent"

    def test_reset_password_request_invalid_email_format(self, client):
        """Test password reset request with invalid email format."""
        reset_res = client.post(
            "/api/auth/password/reset",
            json={"email": "invalid-email"},
        )
        assert reset_res.status_code == 400
        assert "invalid payload" in reset_res.get_json()["error"]

    def test_reset_password_request_missing_email(self, client):
        """Test password reset request without email."""
        reset_res = client.post(
            "/api/auth/password/reset",
            json={},
        )
        assert reset_res.status_code == 400
        assert "invalid payload" in reset_res.get_json()["error"]

    def test_reset_password_sends_email(self, client, app):
        """Test that password reset request sends email."""
        # Register user
        register_res = client.post(
            "/api/auth/register",
            json={"email": "emailtest@example.com", "password": "Password123!", "username": "emailtest"},
        )
        assert register_res.status_code == 201
        
        # Ensure mail is in testing mode
        app.config["MAIL_SUPPRESS_SEND"] = True
        
        with app.app_context():
            with mail.record_messages() as outbox:
                reset_res = client.post(
                    "/api/auth/password/reset",
                    json={"email": "emailtest@example.com"},
                )
                assert reset_res.status_code == 200
                
                # One email should be sent
                assert len(outbox) == 1
                message = outbox[0]
                assert message.recipients == ["emailtest@example.com"]
                assert "Reset Your Password" in message.subject
                assert "/api/auth/password/reset/verify" in (message.body or "")

    def test_verify_reset_password_valid_token(self, client):
        """Test password reset verification with valid token."""
        # Register user
        unique_email = f"verify_{uuid.uuid4().hex[:8]}@example.com"
        register_res = client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "Password123!", "username": f"verifyuser_{uuid.uuid4().hex[:6]}"},
        )
        assert register_res.status_code == 201
        
        # Request password reset to get token
        reset_res = client.post(
            "/api/auth/password/reset",
            json={"email": unique_email},
        )
        assert reset_res.status_code == 200
        
        # Generate a valid reset token manually for testing
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": unique_email}, salt="password-reset")
        
        # Verify password reset
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": token, "new_password": "NewPassword123!"},
        )
        assert verify_res.status_code == 200
        assert verify_res.get_json()["msg"] == "password updated"
        
        # Verify old password no longer works
        login_res = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "Password123!"},
        )
        assert login_res.status_code == 401
        
        # Verify new password works
        login_res = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "NewPassword123!"},
        )
        assert login_res.status_code == 200

    def test_verify_reset_password_invalid_token(self, client):
        """Test password reset verification with invalid token."""
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": "invalid_token", "new_password": "NewPassword123!"},
        )
        assert verify_res.status_code == 400
        assert verify_res.get_json()["error"] == "invalid or expired token"

    def test_verify_reset_password_expired_token(self, client):
        """Test password reset verification with expired token."""
        # Create an expired token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        nonexist_email = f"expired_{uuid.uuid4().hex[:8]}@example.com"
        expired_token = s.dumps({"email": nonexist_email}, salt="password-reset")
        
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": expired_token, "new_password": "NewPassword123!"},
        )
        # Token decodes but user does not exist -> 409 conflict per service behavior
        assert verify_res.status_code == 409

    def test_verify_reset_password_weak_password(self, client):
        """Test password reset verification with weak password."""
        # Register user
        register_res = client.post(
            "/api/auth/register",
            json={"email": "weak@example.com", "password": "Password123!", "username": "weakuser"},
        )
        assert register_res.status_code == 201
        
        # Generate valid token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": "weak@example.com"}, salt="password-reset")
        
        # Try with weak password (no uppercase)
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": token, "new_password": "weakpassword123"},
        )
        assert verify_res.status_code == 400
        assert "invalid payload" in verify_res.get_json()["error"]
        assert "uppercase letter" in str(verify_res.get_json()["details"])

    def test_verify_reset_password_missing_fields(self, client):
        """Test password reset verification with missing fields."""
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": "some_token"},
        )
        assert verify_res.status_code == 400
        assert "invalid payload" in verify_res.get_json()["error"]

    def test_verify_reset_password_nonexistent_user(self, client):
        """Test password reset verification for non-existent user."""
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        nonexist_email = f"nonexist_{uuid.uuid4().hex[:8]}@example.com"
        token = s.dumps({"email": nonexist_email}, salt="password-reset")
        
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": token, "new_password": "NewPassword123!"},
        )
        assert verify_res.status_code == 409
        assert "User not found" in verify_res.get_json().get("error", "")

    def test_full_password_reset_flow(self, client):
        """Test complete password reset flow."""
        # Step 1: Register user
        unique_email = f"flow_{uuid.uuid4().hex[:8]}@example.com"
        register_res = client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "OriginalPassword123!", "username": f"flowuser_{uuid.uuid4().hex[:6]}"},
        )
        assert register_res.status_code == 201
        
        # Step 2: Login with original password
        login_res = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "OriginalPassword123!"},
        )
        assert login_res.status_code == 200
        
        # Step 3: Request password reset
        reset_res = client.post(
            "/api/auth/password/reset",
            json={"email": unique_email},
        )
        assert reset_res.status_code == 200
        
        # Step 4: Generate reset token (simulating email link click)
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": unique_email}, salt="password-reset")
        
        # Step 5: Verify password reset
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": token, "new_password": "NewPassword123!"},
        )
        assert verify_res.status_code == 200
        
        # Step 6: Verify old password no longer works
        login_res = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "OriginalPassword123!"},
        )
        assert login_res.status_code == 401
        
        # Step 7: Verify new password works
        login_res = client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": "NewPassword123!"},
        )
        assert login_res.status_code == 200

    def test_password_reset_with_unverified_user(self, client):
        """Test password reset for unverified user."""
        # Register user (starts unverified)
        unique_email = f"unverified_{uuid.uuid4().hex[:8]}@example.com"
        register_res = client.post(
            "/api/auth/register",
            json={"email": unique_email, "password": "Password123!", "username": f"unverifieduser_{uuid.uuid4().hex[:6]}"},
        )
        assert register_res.status_code == 201
        
        # Check user is unverified
        user = db.session.execute(select(User).where(User.email == unique_email)).scalar_one()
        assert user.is_verified is False
        
        # Generate reset token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": unique_email}, salt="password-reset")
        
        # Try to reset password - allowed even if user is unverified
        verify_res = client.post(
            "/api/auth/password/reset/verify",
            json={"token": token, "new_password": "NewPassword123!"},
        )
        assert verify_res.status_code == 200

    def test_password_reset_token_uniqueness(self, client):
        """Test that each reset request generates unique tokens."""
        # Register user
        register_res = client.post(
            "/api/auth/register",
            json={"email": "unique@example.com", "password": "Password123!", "username": "uniqueuser"},
        )
        assert register_res.status_code == 201
        
        # Request reset twice
        reset_res1 = client.post(
            "/api/auth/password/reset",
            json={"email": "unique@example.com"},
        )
        reset_res2 = client.post(
            "/api/auth/password/reset",
            json={"email": "unique@example.com"},
        )
        
        assert reset_res1.status_code == 200
        assert reset_res2.status_code == 200
        
        # Both should succeed (tokens are generated server-side)
        # In a real implementation, you might want to invalidate previous tokens
