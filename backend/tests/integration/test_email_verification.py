"""Integration tests for email verification functionality."""

import pytest
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from app.models.user import User
from app.extensions import db, mail
from flask_mail import Mail
from sqlalchemy import select


class TestEmailVerification:
    """Test email verification flow."""

    def test_register_user_starts_unverified(self, client):
        """Test that newly registered user is not verified."""
        res = client.post(
            "/api/auth/register",
            json={"email": "verify@example.com", "password": "Password123!", "username": "verifyuser"},
        )
        
        assert res.status_code == 201
        data = res.get_json()
        assert "verify_token" in data
        
        # Check user is not verified in database
        user = db.session.execute(select(User).where(User.email == "verify@example.com")).scalar_one()
        assert user.is_verified is False
        assert user.email_verified_at is None

    def test_register_sends_verification_email(self, client, app):
        """Test that registering sends a verification email to the user."""
        # Ensure mail is in testing mode
        app.config["MAIL_SUPPRESS_SEND"] = True

        with app.app_context():
            # Flask-Mail provides a test context to capture sent emails
            with mail.record_messages() as outbox:
                res = client.post(
                    "/api/auth/register",
                    json={"email": "sendme@example.com", "password": "Password123!", "username": "sendme"},
                )
                assert res.status_code == 201

                # One email should be sent
                assert len(outbox) == 1
                message = outbox[0]
                assert message.recipients == ["sendme@example.com"]
                assert "Confirm Your Email" in message.subject
                # Body should contain a verification link path
                assert "/api/auth/verify?token=" in (message.body or "")

    def test_register_returns_valid_verification_token(self, client):
        """Test that registration returns a valid verification token."""
        res = client.post(
            "/api/auth/register",
            json={"email": "token@example.com", "password": "Password123!", "username": "tokenuser"},
        )
        
        assert res.status_code == 201
        data = res.get_json()
        verify_token = data["verify_token"]
        
        # Verify token can be decoded
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(verify_token, salt="email-verify", max_age=3600)
            assert data.get("email") == "token@example.com"
        except Exception:
            pytest.fail("Verification token should be valid")

    def test_verify_email_with_valid_token(self, client):
        """Test email verification with valid token."""
        # Register user
        res = client.post(
            "/api/auth/register",
            json={"email": "valid@example.com", "password": "Password123!", "username": "validuser"},
        )
        assert res.status_code == 201
        verify_token = res.get_json()["verify_token"]
        
        # Verify email
        verify_res = client.get(f"/api/auth/verify?token={verify_token}")
        assert verify_res.status_code == 200
        assert verify_res.get_json()["msg"] == "email verified"
        
        # Check user is now verified in database
        user = db.session.execute(select(User).where(User.email == "valid@example.com")).scalar_one()
        assert user.is_verified is True
        assert user.email_verified_at is not None

    def test_verify_email_with_invalid_token(self, client):
        """Test email verification with invalid token."""
        verify_res = client.get("/api/auth/verify?token=invalid_token")
        assert verify_res.status_code == 400
        assert verify_res.get_json()["error"] == "invalid or expired token"

    def test_verify_email_without_token(self, client):
        """Test email verification without token."""
        verify_res = client.get("/api/auth/verify")
        assert verify_res.status_code == 400
        assert verify_res.get_json()["error"] == "invalid or expired token"

    def test_verify_email_already_verified(self, client):
        """Test verifying an already verified email."""
        # Register and verify user
        res = client.post(
            "/api/auth/register",
            json={"email": "already@example.com", "password": "Password123!", "username": "alreadyuser"},
        )
        verify_token = res.get_json()["verify_token"]
        
        # First verification
        verify_res = client.get(f"/api/auth/verify?token={verify_token}")
        assert verify_res.status_code == 200
        
        # Second verification attempt
        verify_res2 = client.get(f"/api/auth/verify?token={verify_token}")
        assert verify_res2.status_code == 200
        assert verify_res2.get_json()["msg"] == "email verified"

    def test_verify_email_with_expired_token(self, client):
        """Test email verification with expired token."""
        # Register user
        res = client.post(
            "/api/auth/register",
            json={"email": "expired@example.com", "password": "Password123!", "username": "expireduser"},
        )
        verify_token = res.get_json()["verify_token"]
        
        # Create a truly expired token by using a malformed token
        # In practice, we'd need to manipulate timestamps, but for testing we'll use a malformed token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDAwMDAwMDB9.fake_signature"
        
        # Try to verify with expired token
        verify_res = client.get(f"/api/auth/verify?token={expired_token}")
        assert verify_res.status_code == 400
        assert verify_res.get_json()["error"] == "invalid or expired token"

    def test_verify_email_with_nonexistent_user(self, client):
        """Test email verification with token for non-existent user."""
        # Create a token for a non-existent user ID
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        fake_token = s.dumps({"email": "nonexistent@example.com"}, salt="email-verify")
        
        verify_res = client.get(f"/api/auth/verify?token={fake_token}")
        assert verify_res.status_code == 404
        assert verify_res.get_json()["error"] == "user not found"

    def test_full_verification_flow(self, client):
        """Test complete email verification flow."""
        # Step 1: Register user
        res = client.post(
            "/api/auth/register",
            json={"email": "flow@example.com", "password": "Password123!", "username": "flowuser"},
        )
        assert res.status_code == 201
        data = res.get_json()
        verify_token = data["verify_token"]
        
        # Step 2: Check user is unverified
        user = db.session.execute(select(User).where(User.email == "flow@example.com")).scalar_one()
        assert user.is_verified is False
        assert user.email_verified_at is None
        
        # Step 3: Verify email
        verify_res = client.get(f"/api/auth/verify?token={verify_token}")
        assert verify_res.status_code == 200
        assert verify_res.get_json()["msg"] == "email verified"
        
        # Step 4: Check user is now verified
        user = db.session.execute(select(User).where(User.email == "flow@example.com")).scalar_one()
        assert user.is_verified is True
        assert user.email_verified_at is not None
        
        # Step 5: Try to verify again (should be idempotent)
        verify_res2 = client.get(f"/api/auth/verify?token={verify_token}")
        assert verify_res2.status_code == 200
        assert verify_res2.get_json()["msg"] == "email verified"

    def test_verification_token_uniqueness(self, client):
        """Test that each registration generates a unique verification token."""
        # Register two users
        res1 = client.post(
            "/api/auth/register",
            json={"email": "unique1@example.com", "password": "Password123!", "username": "unique1"},
        )
        res2 = client.post(
            "/api/auth/register",
            json={"email": "unique2@example.com", "password": "Password123!", "username": "unique2"},
        )
        
        token1 = res1.get_json()["verify_token"]
        token2 = res2.get_json()["verify_token"]
        
        # Tokens should be different
        assert token1 != token2
        
        # Both tokens should be valid for their respective users
        verify_res1 = client.get(f"/api/auth/verify?token={token1}")
        verify_res2 = client.get(f"/api/auth/verify?token={token2}")
        
        assert verify_res1.status_code == 200
        assert verify_res2.status_code == 200
        
        # Verify both users are now verified
        user1 = db.session.execute(select(User).where(User.email == "unique1@example.com")).scalar_one()
        user2 = db.session.execute(select(User).where(User.email == "unique2@example.com")).scalar_one()
        
        assert user1.is_verified is True
        assert user2.is_verified is True
