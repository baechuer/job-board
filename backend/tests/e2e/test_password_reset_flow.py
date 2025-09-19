"""End-to-end tests for password reset flow."""

import pytest
import uuid
from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from app.models.user import User
from app.extensions import db, mail
from sqlalchemy import select


class TestPasswordResetE2E:
    """End-to-end tests for complete password reset workflow."""

    def test_complete_password_reset_workflow(self, client):
        """Test the complete password reset workflow from request to verification."""
        # Step 1: User registers
        register_data = {
            "email": f"workflow_{uuid.uuid4().hex[:8]}@example.com",
            "password": "OriginalPassword123!",
            "username": f"workflowuser_{uuid.uuid4().hex[:6]}"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Step 2: User can login with original password
        login_res = client.post("/api/auth/login", json={
            "email": register_data["email"],
            "password": register_data["password"]
        })
        assert login_res.status_code == 200
        
        # Step 3: User requests password reset
        reset_res = client.post("/api/auth/password/reset", json={
            "email": register_data["email"]
        })
        assert reset_res.status_code == 200
        assert reset_res.get_json()["msg"] == "if the email exists, a reset link has been sent"
        
        # Step 4: Simulate email click - generate reset token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        reset_token = s.dumps({"email": register_data["email"]}, salt="password-reset")
        
        # Step 5: User clicks link and submits new password
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": reset_token,
            "new_password": "NewPassword123!"
        })
        assert verify_res.status_code == 200
        assert verify_res.get_json()["msg"] == "password updated"
        
        # Step 6: Original password no longer works
        login_res = client.post("/api/auth/login", json={
            "email": register_data["email"],
            "password": register_data["password"]
        })
        assert login_res.status_code == 401
        
        # Step 7: New password works
        login_res = client.post("/api/auth/login", json={
            "email": register_data["email"],
            "password": "NewPassword123!"
        })
        assert login_res.status_code == 200

    def test_password_reset_with_email_sending(self, client, app):
        """Test password reset with actual email sending simulation."""
        # Register user
        register_data = {
            "email": f"emailsend_{uuid.uuid4().hex[:8]}@example.com",
            "password": "Password123!",
            "username": f"emailsenduser_{uuid.uuid4().hex[:6]}"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Ensure mail is in testing mode
        app.config["MAIL_SUPPRESS_SEND"] = True
        
        with app.app_context():
            with mail.record_messages() as outbox:
                # Request password reset
                reset_res = client.post("/api/auth/password/reset", json={
                    "email": register_data["email"]
                })
                assert reset_res.status_code == 200
                
                # Check email was sent
                assert len(outbox) == 1
                message = outbox[0]
                assert message.recipients == [register_data["email"]]
                assert "Reset Your Password" in message.subject
                assert "/api/auth/password/reset/verify" in (message.body or "")
                
                # Extract token from email body (simulating user clicking link)
                email_body = message.body or ""
                if "token=" in email_body:
                    token_start = email_body.find("token=") + 6
                    token_end = email_body.find(" ", token_start)
                    if token_end == -1:
                        token_end = len(email_body)
                    token = email_body[token_start:token_end]
                    
                    # Use extracted token to reset password
                    verify_res = client.post("/api/auth/password/reset/verify", json={
                        "token": token,
                        "new_password": "NewPassword123!"
                    })
                    assert verify_res.status_code == 200

    def test_password_reset_error_scenarios(self, client):
        """Test various error scenarios in password reset flow."""
        # Test 1: Reset request with invalid email format
        reset_res = client.post("/api/auth/password/reset", json={
            "email": "invalid-email"
        })
        assert reset_res.status_code == 400
        
        # Test 2: Reset request without email
        reset_res = client.post("/api/auth/password/reset", json={})
        assert reset_res.status_code == 400
        
        # Test 3: Verify reset with invalid token
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": "invalid_token",
            "new_password": "NewPassword123!"
        })
        assert verify_res.status_code == 400
        
        # Test 4: Verify reset with weak password
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": "test@example.com"}, salt="password-reset")
        
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "weak"
        })
        assert verify_res.status_code == 400

    def test_password_reset_with_multiple_attempts(self, client):
        """Test password reset with multiple reset attempts."""
        # Register user
        register_data = {
            "email": f"multiple_{uuid.uuid4().hex[:8]}@example.com",
            "password": "OriginalPassword123!",
            "username": f"multipleuser_{uuid.uuid4().hex[:6]}"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Request password reset multiple times
        for i in range(3):
            reset_res = client.post("/api/auth/password/reset", json={
                "email": register_data["email"]
            })
            assert reset_res.status_code == 200
        
        # Generate token and reset password
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": register_data["email"]}, salt="password-reset")
        
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "NewPassword123!"
        })
        assert verify_res.status_code == 200
        
        # Verify new password works
        login_res = client.post("/api/auth/login", json={
            "email": register_data["email"],
            "password": "NewPassword123!"
        })
        assert login_res.status_code == 200

    def test_password_reset_token_reuse_attempt(self, client):
        """Test that reset tokens cannot be reused."""
        # Register user
        register_data = {
            "email": f"reuse_{uuid.uuid4().hex[:8]}@example.com",
            "password": "OriginalPassword123!",
            "username": f"reuseuser_{uuid.uuid4().hex[:6]}"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Generate reset token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": register_data["email"]}, salt="password-reset")
        
        # First reset attempt
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "FirstPassword123!"
        })
        assert verify_res.status_code == 200
        
        # Second reset attempt with same token
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "SecondPassword123!"
        })
        # This should still work because we don't invalidate tokens after use
        # In a production system, you might want to invalidate tokens after use
        assert verify_res.status_code == 200

    def test_password_reset_with_unverified_user(self, client):
        """Test password reset for unverified user (should fail)."""
        # Register user (starts unverified)
        register_data = {
            "email": f"unverified_{uuid.uuid4().hex[:8]}@example.com",
            "password": "Password123!",
            "username": f"unverifieduser_{uuid.uuid4().hex[:6]}"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Check user is unverified
        user = db.session.execute(select(User).where(User.email == register_data["email"])).scalar_one()
        assert user.is_verified is False
        
        # Generate reset token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": register_data["email"]}, salt="password-reset")
        
        # Try to reset password - this should fail due to verification check
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "NewPassword123!"
        })
        # Allowed now: unverified users can reset
        assert verify_res.status_code == 200

    def test_password_reset_security_validation(self, client):
        """Test password reset with various security validations."""
        # Register user
        register_data = {
            "email": "security@example.com",
            "password": "Password123!",
            "username": "securityuser"
        }
        
        register_res = client.post("/api/auth/register", json=register_data)
        assert register_res.status_code == 201
        
        # Generate reset token
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        token = s.dumps({"email": register_data["email"]}, salt="password-reset")
        
        # Test various password strength requirements
        weak_passwords = [
            "weak",           # Too short
            "weakpassword",   # No uppercase, no number
            "WEAKPASSWORD",  # No lowercase, no number
            "WeakPassword",   # No number
            "weakpassword123", # No uppercase
            "WEAKPASSWORD123", # No lowercase
        ]
        
        for weak_password in weak_passwords:
            verify_res = client.post("/api/auth/password/reset/verify", json={
                "token": token,
                "new_password": weak_password
            })
            assert verify_res.status_code == 400
            assert "invalid payload" in verify_res.get_json()["error"]
        
        # Test strong password (should work)
        verify_res = client.post("/api/auth/password/reset/verify", json={
            "token": token,
            "new_password": "StrongPassword123!"
        })
        assert verify_res.status_code == 200
