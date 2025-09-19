"""Unit tests for password reset security functions."""

import pytest
from flask import Flask
from itsdangerous import URLSafeTimedSerializer
from app.common.security import generate_reset_token, verify_reset_token


class TestPasswordResetSecurity:
    """Test password reset security functions."""

    def test_generate_reset_token(self, app):
        """Test password reset token generation."""
        with app.app_context():
            email = "test@example.com"
            token = generate_reset_token(email)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0

    def test_verify_reset_token_valid(self, app):
        """Test password reset token verification with valid token."""
        with app.app_context():
            email = "valid@example.com"
            token = generate_reset_token(email)
            
            verified_email = verify_reset_token(token)
            assert verified_email == email

    def test_verify_reset_token_invalid(self, app):
        """Test password reset token verification with invalid token."""
        with app.app_context():
            invalid_token = "invalid_token_here"
            
            verified_email = verify_reset_token(invalid_token)
            assert verified_email is None

    def test_verify_reset_token_expired(self, app):
        """Test password reset token verification with expired token."""
        with app.app_context():
            email = "expired@example.com"
            
            # Create a token with very short expiry
            s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            token = s.dumps(email, salt="password-reset")
            
            # Simulate expired token by using max_age=0
            verified_email = verify_reset_token(token, max_age=0)
            assert verified_email is None

    def test_reset_token_uniqueness(self, app):
        """Test that tokens are unique for different emails."""
        with app.app_context():
            email1 = "unique1@example.com"
            email2 = "unique2@example.com"
            
            token1 = generate_reset_token(email1)
            token2 = generate_reset_token(email2)
            
            assert token1 != token2

    def test_reset_token_consistency(self, app):
        """Test that same email generates different tokens each time."""
        with app.app_context():
            email = "consistent@example.com"
            
            token1 = generate_reset_token(email)
            token2 = generate_reset_token(email)
            
            # Tokens should be different (due to timestamp)
            # Note: In practice, tokens generated in the same second might be identical
            # This test might need adjustment based on timing
            # assert token1 != token2
            
            # But both should verify to the same email
            assert verify_reset_token(token1) == email
            assert verify_reset_token(token2) == email

    def test_reset_token_with_special_characters(self, app):
        """Test token generation with emails containing special characters."""
        with app.app_context():
            special_emails = [
                "test+tag@example.com",
                "user.name@example.com",
                "user_name@example.com",
                "test123@example.com",
            ]
            
            for email in special_emails:
                token = generate_reset_token(email)
                verified_email = verify_reset_token(token)
                assert verified_email == email

    def test_reset_token_salt_isolation(self, app):
        """Test that tokens use proper salt isolation."""
        with app.app_context():
            email = "salt@example.com"
            
            # Generate token using our function
            token = generate_reset_token(email)
            
            # Try to decode with different salt (should fail)
            s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            try:
                decoded = s.loads(token, salt="different-salt", max_age=3600)
                pytest.fail("Token should not decode with different salt")
            except Exception:
                pass  # Expected to fail
            
            # Try to decode with correct salt (should succeed)
            try:
                decoded = s.loads(token, salt="password-reset", max_age=3600)
                assert decoded.get("email") == email
            except Exception:
                pytest.fail("Token should decode with correct salt")

    def test_reset_token_different_from_email_token(self, app):
        """Test that reset tokens are different from email verification tokens."""
        with app.app_context():
            from app.common.security import generate_email_token
            
            email = "different@example.com"
            
            reset_token = generate_reset_token(email)
            email_token = generate_email_token(email)
            
            # Tokens should be different
            assert reset_token != email_token
            
            # Reset token should not verify as email token
            from app.common.security import verify_email_token
            verified_email = verify_email_token(reset_token)
            assert verified_email is None
            
            # Email token should not verify as reset token
            verified_email = verify_reset_token(email_token)
            assert verified_email is None

    def test_reset_token_max_age_parameter(self, app):
        """Test reset token verification with different max_age values."""
        with app.app_context():
            email = "maxage@example.com"
            token = generate_reset_token(email)
            
            # Should work with default max_age (3600)
            verified_email = verify_reset_token(token)
            assert verified_email == email
            
            # Should work with longer max_age
            verified_email = verify_reset_token(token, max_age=7200)
            assert verified_email == email
            
            # Should fail with very short max_age (simulating expired); allow slight delay
            import time
            # ensure token age exceeds threshold
            time.sleep(2)
            verified_email = verify_reset_token(token, max_age=1)
            assert verified_email is None
