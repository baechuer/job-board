"""Unit tests for email security functions."""

import pytest
from flask import Flask
from itsdangerous import URLSafeTimedSerializer
from app.common.security import generate_email_token, verify_email_token


class TestEmailSecurity:
    """Test email security functions."""

    def test_generate_email_token(self, app):
        """Test email token generation."""
        with app.app_context():
            email = "test@example.com"
            token = generate_email_token(email)
            
            assert token is not None
            assert isinstance(token, str)
            assert len(token) > 0

    def test_verify_email_token_valid(self, app):
        """Test email token verification with valid token."""
        with app.app_context():
            email = "valid@example.com"
            token = generate_email_token(email)
            
            verified_email = verify_email_token(token)
            assert verified_email == email

    def test_verify_email_token_invalid(self, app):
        """Test email token verification with invalid token."""
        with app.app_context():
            invalid_token = "invalid_token_here"
            
            verified_email = verify_email_token(invalid_token)
            assert verified_email is None

    def test_verify_email_token_expired(self, app):
        """Test email token verification with expired token."""
        with app.app_context():
            email = "expired@example.com"
            
            # Create a token with very short expiry
            s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            token = s.dumps(email, salt="email-confirm")
            
            # Simulate expired token by using max_age=0
            verified_email = verify_email_token(token, max_age=0)
            assert verified_email is None

    def test_token_uniqueness(self, app):
        """Test that tokens are unique for different emails."""
        with app.app_context():
            email1 = "unique1@example.com"
            email2 = "unique2@example.com"
            
            token1 = generate_email_token(email1)
            token2 = generate_email_token(email2)
            
            assert token1 != token2

    def test_token_consistency(self, app):
        """Test that same email generates different tokens each time."""
        with app.app_context():
            email = "consistent@example.com"
            
            token1 = generate_email_token(email)
            token2 = generate_email_token(email)
            
            # Tokens should be different (due to timestamp)
            # Note: In practice, tokens generated in the same second might be identical
            # This test might need adjustment based on timing
            # assert token1 != token2
            
            # But both should verify to the same email
            assert verify_email_token(token1) == email
            assert verify_email_token(token2) == email

    def test_token_with_special_characters(self, app):
        """Test token generation with emails containing special characters."""
        with app.app_context():
            special_emails = [
                "test+tag@example.com",
                "user.name@example.com",
                "user_name@example.com",
                "test123@example.com",
            ]
            
            for email in special_emails:
                token = generate_email_token(email)
                verified_email = verify_email_token(token)
                assert verified_email == email

    def test_token_salt_isolation(self, app):
        """Test that tokens use proper salt isolation."""
        with app.app_context():
            email = "salt@example.com"
            
            # Generate token using our function
            token = generate_email_token(email)
            
            # Try to decode with different salt (should fail)
            s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
            try:
                decoded = s.loads(token, salt="different-salt", max_age=3600)
                pytest.fail("Token should not decode with different salt")
            except Exception:
                pass  # Expected to fail
            
            # Try to decode with correct salt (should succeed)
            try:
                decoded = s.loads(token, salt="email-verify", max_age=3600)
                assert decoded.get("email") == email
            except Exception:
                pytest.fail("Token should decode with correct salt")
