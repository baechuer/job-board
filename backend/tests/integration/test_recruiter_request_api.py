"""Integration tests for recruiter request API endpoints."""

import pytest
from sqlalchemy import select
from app.extensions import db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.recruiter_request import RecruiterRequest


class TestRecruiterRequestAPI:
    
    @pytest.fixture
    def test_user_data(self):
        return {
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "username": "testuser"
        }
    
    @pytest.fixture
    def admin_user_data(self):
        return {
            "email": "admin@example.com",
            "password": "AdminPassword123!",
            "username": "admin"
        }
    
    def create_user_and_login(self, client, user_data):
        """Helper to create user and return auth token."""
        # Register user
        res = client.post("/api/auth/register", json=user_data)
        assert res.status_code == 201
        user_id = res.get_json()["id"]
        
        # Login to get token
        res = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert res.status_code == 200
        token = res.get_json()["access_token"]
        
        return user_id, token
    
    def create_admin_user(self, client, admin_data):
        """Helper to create admin user."""
        user_id, token = self.create_user_and_login(client, admin_data)
        
        # Add admin role
        user = db.session.get(User, user_id)
        user.roles.append(UserRole(role="admin"))
        db.session.commit()
        
        return user_id, token
    
    def verify_user_email(self, client, user_id):
        """Helper to verify user email."""
        user = db.session.get(User, user_id)
        user.is_verified = True
        user.email_verified_at = db.func.now()
        db.session.commit()

    def test_submit_request_email_not_verified(self, client, test_user_data):
        """Test that unverified users cannot submit requests."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I want to become a recruiter"},
                         headers=headers)
        
        assert res.status_code == 400
        assert "Email verification required" in res.get_json()["error"]

    def test_submit_request_success(self, client, test_user_data):
        """Test successful request submission."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I want to become a recruiter"},
                         headers=headers)
        
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "pending"
        assert data["reason"] == "I want to become a recruiter"
        assert "id" in data
        assert "submitted_at" in data

    def test_submit_request_duplicate(self, client, test_user_data):
        """Test that users cannot submit duplicate requests."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # First request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "First request"},
                         headers=headers)
        assert res.status_code == 201
        
        # Second request should fail
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Second request"},
                         headers=headers)
        assert res.status_code == 409
        assert "already have a pending recruiter request" in res.get_json()["error"]

    def test_submit_request_no_reason(self, client, test_user_data):
        """Test request submission without reason."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={},
                         headers=headers)
        
        assert res.status_code == 201
        data = res.get_json()
        assert data["status"] == "pending"
        assert data["reason"] is None

    def test_submit_request_invalid_reason_length(self, client, test_user_data):
        """Test request submission with reason too long."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        long_reason = "x" * 1001  # Exceeds 1000 character limit
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": long_reason},
                         headers=headers)
        
        assert res.status_code == 400
        assert "Invalid payload" in res.get_json()["error"]

    def test_get_request_status_no_request(self, client, test_user_data):
        """Test getting status when no request exists."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        
        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/recruiter-requests/my-status", headers=headers)
        
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "no_request"
        assert "No active request found" in data["message"]

    def test_get_request_status_with_request(self, client, test_user_data):
        """Test getting status when request exists."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Submit request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        
        # Check status
        res = client.get("/api/recruiter-requests/my-status", headers=headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "pending"
        assert data["reason"] == "Test reason"

    def test_get_my_requests(self, client, test_user_data):
        """Test getting all user requests."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Submit request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        
        # Get all requests
        res = client.get("/api/recruiter-requests/my-requests", headers=headers)
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["status"] == "pending"
        assert data[0]["reason"] == "Test reason"

    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication."""
        # Test without token
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"})
        assert res.status_code == 401
        
        res = client.get("/api/recruiter-requests/my-status")
        assert res.status_code == 401
        
        res = client.get("/api/recruiter-requests/my-requests")
        assert res.status_code == 401

    def test_admin_get_all_requests(self, client, test_user_data, admin_user_data):
        """Test admin can get all requests."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin gets all requests
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/admin/recruiter-requests", headers=admin_headers)
        
        assert res.status_code == 200
        data = res.get_json()
        assert "requests" in data
        assert "total" in data
        assert "pages" in data
        assert len(data["requests"]) == 1
        assert data["requests"][0]["status"] == "pending"

    def test_admin_get_requests_with_filter(self, client, test_user_data, admin_user_data):
        """Test admin can filter requests by status."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin filters by pending status
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/admin/recruiter-requests?status=pending", headers=admin_headers)
        
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["requests"]) == 1
        assert data["requests"][0]["status"] == "pending"
        
        # Admin filters by approved status (should be empty)
        res = client.get("/api/admin/recruiter-requests?status=approved", headers=admin_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["requests"]) == 0

    def test_admin_approve_request(self, client, test_user_data, admin_user_data):
        """Test admin can approve requests."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        request_id = res.get_json()["id"]
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin approves request
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "Approved for testing"},
                        headers=admin_headers)
        
        assert res.status_code == 200
        assert "approved successfully" in res.get_json()["message"]
        
        # Verify user now has recruiter role
        user = db.session.get(User, user_id)
        roles = [r.role for r in user.roles]
        assert "recruiter" in roles
        
        # Verify request status updated
        request = db.session.get(RecruiterRequest, request_id)
        assert request.status == "approved"
        assert request.reviewed_by == admin_id
        assert request.admin_notes == "Approved for testing"

    def test_admin_reject_request(self, client, test_user_data, admin_user_data):
        """Test admin can reject requests."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        request_id = res.get_json()["id"]
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin rejects request
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/reject",
                        json={"notes": "Rejected for testing"},
                        headers=admin_headers)
        
        assert res.status_code == 200
        assert "rejected successfully" in res.get_json()["message"]
        
        # Verify user does not have recruiter role
        user = db.session.get(User, user_id)
        roles = [r.role for r in user.roles]
        assert "recruiter" not in roles
        
        # Verify request status updated
        request = db.session.get(RecruiterRequest, request_id)
        assert request.status == "rejected"
        assert request.reviewed_by == admin_id
        assert request.admin_notes == "Rejected for testing"
        assert "Thank you for your interest" in request.feedback
        assert "To improve your chances" in request.reapplication_guidance

    def test_admin_cannot_approve_non_pending_request(self, client, test_user_data, admin_user_data):
        """Test admin cannot approve non-pending requests."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        request_id = res.get_json()["id"]
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Approve request first
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "First approval"},
                        headers=admin_headers)
        assert res.status_code == 200
        
        # Try to approve again (should fail)
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "Second approval"},
                        headers=admin_headers)
        assert res.status_code == 400
        assert "Only pending requests can be approved" in res.get_json()["error"]

    def test_non_admin_cannot_access_admin_endpoints(self, client, test_user_data):
        """Test that non-admin users cannot access admin endpoints."""
        user_id, token = self.create_user_and_login(client, test_user_data)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to access admin endpoints
        res = client.get("/api/admin/recruiter-requests", headers=headers)
        assert res.status_code == 403
        assert "Admin access required" in res.get_json()["error"]
        
        res = client.put("/api/admin/recruiter-requests/1/approve", 
                        json={"notes": "Test"},
                        headers=headers)
        assert res.status_code == 403
        
        res = client.put("/api/admin/recruiter-requests/1/reject",
                        json={"notes": "Test"},
                        headers=headers)
        assert res.status_code == 403

    def test_admin_mark_requests_as_viewed(self, client, test_user_data, admin_user_data):
        """Test admin can mark requests as viewed."""
        # Create regular user and submit request
        user_id, user_token = self.create_user_and_login(client, test_user_data)
        self.verify_user_email(client, user_id)
        
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test reason"},
                         headers=headers)
        assert res.status_code == 201
        
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin marks requests as viewed
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/api/admin/recruiter-requests/mark-viewed", headers=admin_headers)
        
        assert res.status_code == 200
        assert "marked as viewed" in res.get_json()["message"]

    def test_admin_cleanup_completed_requests(self, client, test_user_data, admin_user_data):
        """Test admin can cleanup completed requests."""
        # Create admin user
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        # Admin cleans up requests
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/api/admin/recruiter-requests/cleanup", headers=admin_headers)
        
        assert res.status_code == 200
        data = res.get_json()
        assert "Cleaned up" in data["message"]
        assert "completed requests" in data["message"]

    def test_pagination_parameters(self, client, admin_user_data):
        """Test pagination parameter validation."""
        admin_id, admin_token = self.create_admin_user(client, admin_user_data)
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test invalid page parameter
        res = client.get("/api/admin/recruiter-requests?page=0", headers=admin_headers)
        assert res.status_code == 200  # Should default to page 1
        
        # Test invalid per_page parameter
        res = client.get("/api/admin/recruiter-requests?per_page=200", headers=admin_headers)
        assert res.status_code == 200  # Should default to per_page 10
        
        # Test valid parameters
        res = client.get("/api/admin/recruiter-requests?page=1&per_page=5", headers=admin_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["current_page"] == 1
        assert data["per_page"] == 5
