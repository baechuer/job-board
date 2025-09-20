"""End-to-end tests for complete recruiter request workflow."""

import pytest
from sqlalchemy import select
from app.extensions import db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.recruiter_request import RecruiterRequest


class TestRecruiterRequestE2E:
    """End-to-end tests that simulate real user workflows."""
    
    @pytest.fixture
    def candidate_data(self):
        return {
            "email": "candidate@example.com",
            "password": "CandidatePass123!",
            "username": "candidate"
        }
    
    @pytest.fixture
    def admin_data(self):
        return {
            "email": "admin@example.com",
            "password": "AdminPass123!",
            "username": "admin"
        }
    
    def create_and_verify_user(self, client, user_data):
        """Helper to create user, verify email, and return auth token."""
        # Register user
        res = client.post("/api/auth/register", json=user_data)
        assert res.status_code == 201
        user_id = res.get_json()["id"]
        
        # Verify email
        user = db.session.get(User, user_id)
        user.is_verified = True
        user.email_verified_at = db.func.now()
        db.session.commit()
        
        # Login to get token
        res = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert res.status_code == 200
        token = res.get_json()["access_token"]
        
        return user_id, token
    
    def create_admin_user(self, client, admin_data):
        """Helper to create admin user and return auth token."""
        user_id, token = self.create_and_verify_user(client, admin_data)
        
        # Add admin role
        user = db.session.get(User, user_id)
        user.roles.append(UserRole(role="admin"))
        db.session.commit()
        
        return user_id, token

    def test_complete_approval_workflow(self, client, candidate_data, admin_data):
        """Test complete workflow: submit request -> admin approval -> user becomes recruiter."""
        
        # === PHASE 1: CANDIDATE SUBMITS REQUEST ===
        candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
        candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
        
        # Submit recruiter request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I have 5 years of HR experience and want to help companies find talent"},
                         headers=candidate_headers)
        assert res.status_code == 201
        
        request_data = res.get_json()
        request_id = request_data["id"]
        assert request_data["status"] == "pending"
        assert request_data["reason"] == "I have 5 years of HR experience and want to help companies find talent"
        
        # Verify request exists in database
        request = db.session.get(RecruiterRequest, request_id)
        assert request is not None
        assert request.status == "pending"
        assert request.user_id == candidate_id
        
        # === PHASE 2: CANDIDATE CHECKS STATUS ===
        res = client.get("/api/recruiter-requests/my-status", headers=candidate_headers)
        assert res.status_code == 200
        status_data = res.get_json()
        assert status_data["status"] == "pending"
        
        # Get all candidate's requests
        res = client.get("/api/recruiter-requests/my-requests", headers=candidate_headers)
        assert res.status_code == 200
        requests_data = res.get_json()
        assert len(requests_data) == 1
        assert requests_data[0]["status"] == "pending"
        
        # === PHASE 3: ADMIN REVIEWS REQUEST ===
        admin_id, admin_token = self.create_admin_user(client, admin_data)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Admin gets all pending requests
        res = client.get("/api/admin/recruiter-requests?status=pending", headers=admin_headers)
        assert res.status_code == 200
        admin_requests = res.get_json()
        assert len(admin_requests["requests"]) == 1
        assert admin_requests["requests"][0]["id"] == request_id
        assert admin_requests["requests"][0]["status"] == "pending"
        
        # === PHASE 4: ADMIN APPROVES REQUEST ===
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "Strong background in HR, approved for recruiter role"},
                        headers=admin_headers)
        assert res.status_code == 200
        assert "approved successfully" in res.get_json()["message"]
        
        # === PHASE 5: VERIFY APPROVAL EFFECTS ===
        # Check request status updated
        request = db.session.get(RecruiterRequest, request_id)
        assert request.status == "approved"
        assert request.reviewed_by == admin_id
        assert request.admin_notes == "Strong background in HR, approved for recruiter role"
        assert "Congratulations" in request.feedback
        assert "recruiter features" in request.reapplication_guidance
        
        # Check user now has recruiter role
        user = db.session.get(User, candidate_id)
        roles = [r.role for r in user.roles]
        assert "candidate" in roles
        assert "recruiter" in roles
        
        # Check candidate can see updated status
        res = client.get("/api/recruiter-requests/my-status", headers=candidate_headers)
        assert res.status_code == 200
        status_data = res.get_json()
        assert status_data["status"] == "approved"
        assert "Congratulations" in status_data["feedback"]
        
        # Check admin can see approved request
        res = client.get("/api/admin/recruiter-requests?status=approved", headers=admin_headers)
        assert res.status_code == 200
        admin_requests = res.get_json()
        assert len(admin_requests["requests"]) == 1
        assert admin_requests["requests"][0]["status"] == "approved"

    def test_complete_rejection_workflow(self, client, candidate_data, admin_data):
        """Test complete workflow: submit request -> admin rejection -> user can reapply."""
        
        # === PHASE 1: CANDIDATE SUBMITS REQUEST ===
        candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
        candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
        
        # Submit recruiter request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I want to be a recruiter"},
                         headers=candidate_headers)
        assert res.status_code == 201
        
        request_data = res.get_json()
        request_id = request_data["id"]
        
        # === PHASE 2: ADMIN REJECTS REQUEST ===
        admin_id, admin_token = self.create_admin_user(client, admin_data)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/reject",
                        json={"notes": "Please gain more experience on the platform before reapplying"},
                        headers=admin_headers)
        assert res.status_code == 200
        assert "rejected successfully" in res.get_json()["message"]
        
        # === PHASE 3: VERIFY REJECTION EFFECTS ===
        # Check request status updated
        request = db.session.get(RecruiterRequest, request_id)
        assert request.status == "rejected"
        assert request.reviewed_by == admin_id
        assert request.admin_notes == "Please gain more experience on the platform before reapplying"
        assert "Thank you for your interest" in request.feedback
        assert "To improve your chances" in request.reapplication_guidance
        
        # Check user does NOT have recruiter role
        user = db.session.get(User, candidate_id)
        roles = [r.role for r in user.roles]
        assert "candidate" in roles
        assert "recruiter" not in roles
        
        # Check candidate can see rejection status
        res = client.get("/api/recruiter-requests/my-status", headers=candidate_headers)
        assert res.status_code == 200
        status_data = res.get_json()
        assert status_data["status"] == "rejected"
        assert "Thank you for your interest" in status_data["feedback"]
        assert "To improve your chances" in status_data["reapplication_guidance"]
        
        # === PHASE 4: CANDIDATE CAN REAPPLY ===
        # After rejection, candidate should be able to submit a new request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I have gained more experience and want to reapply"},
                         headers=candidate_headers)
        assert res.status_code == 201
        
        new_request_data = res.get_json()
        new_request_id = new_request_data["id"]
        assert new_request_id != request_id
        assert new_request_data["status"] == "pending"

    def test_multiple_users_multiple_requests(self, client, admin_data):
        """Test multiple users submitting requests and admin managing them."""
        
        # Create multiple candidates
        candidates = []
        for i in range(3):
            candidate_data = {
                "email": f"candidate{i}@example.com",
                "password": "CandidatePass123!",
                "username": f"candidate{i}"
            }
            candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
            candidates.append((candidate_id, candidate_token))
        
        # All candidates submit requests
        request_ids = []
        for i, (candidate_id, candidate_token) in enumerate(candidates):
            headers = {"Authorization": f"Bearer {candidate_token}"}
            res = client.post("/api/recruiter-requests/", 
                             json={"reason": f"Candidate {i} wants to become a recruiter"},
                             headers=headers)
            assert res.status_code == 201
            request_ids.append(res.get_json()["id"])
        
        # Create admin
        admin_id, admin_token = self.create_admin_user(client, admin_data)
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Admin gets all pending requests
        res = client.get("/api/admin/recruiter-requests?status=pending", headers=admin_headers)
        assert res.status_code == 200
        admin_requests = res.get_json()
        assert len(admin_requests["requests"]) == 3
        assert admin_requests["total"] == 3
        
        # Admin approves first request
        res = client.put(f"/api/admin/recruiter-requests/{request_ids[0]}/approve",
                        json={"notes": "Approved candidate 0"},
                        headers=admin_headers)
        assert res.status_code == 200
        
        # Admin rejects second request
        res = client.put(f"/api/admin/recruiter-requests/{request_ids[1]}/reject",
                        json={"notes": "Rejected candidate 1"},
                        headers=admin_headers)
        assert res.status_code == 200
        
        # Admin leaves third request pending
        
        # Verify final states
        # Approved request
        request = db.session.get(RecruiterRequest, request_ids[0])
        assert request.status == "approved"
        user = db.session.get(User, candidates[0][0])
        roles = [r.role for r in user.roles]
        assert "recruiter" in roles
        
        # Rejected request
        request = db.session.get(RecruiterRequest, request_ids[1])
        assert request.status == "rejected"
        user = db.session.get(User, candidates[1][0])
        roles = [r.role for r in user.roles]
        assert "recruiter" not in roles
        
        # Pending request
        request = db.session.get(RecruiterRequest, request_ids[2])
        assert request.status == "pending"
        user = db.session.get(User, candidates[2][0])
        roles = [r.role for r in user.roles]
        assert "recruiter" not in roles
        
        # Admin can filter by status
        res = client.get("/api/admin/recruiter-requests?status=approved", headers=admin_headers)
        assert res.status_code == 200
        approved_requests = res.get_json()
        assert len(approved_requests["requests"]) == 1
        
        res = client.get("/api/admin/recruiter-requests?status=rejected", headers=admin_headers)
        assert res.status_code == 200
        rejected_requests = res.get_json()
        assert len(rejected_requests["requests"]) == 1
        
        res = client.get("/api/admin/recruiter-requests?status=pending", headers=admin_headers)
        assert res.status_code == 200
        pending_requests = res.get_json()
        assert len(pending_requests["requests"]) == 1

    def test_email_verification_requirement(self, client, candidate_data):
        """Test that email verification is strictly enforced."""
        
        # Register user but don't verify email
        res = client.post("/api/auth/register", json=candidate_data)
        assert res.status_code == 201
        user_id = res.get_json()["id"]
        
        # Login to get token
        res = client.post("/api/auth/login", json={
            "email": candidate_data["email"],
            "password": candidate_data["password"]
        })
        assert res.status_code == 200
        token = res.get_json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to submit request (should fail)
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I want to become a recruiter"},
                         headers=headers)
        assert res.status_code == 400
        assert "Email verification required" in res.get_json()["error"]
        
        # Verify email
        user = db.session.get(User, user_id)
        user.is_verified = True
        user.email_verified_at = db.func.now()
        db.session.commit()
        
        # Now should be able to submit request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "I want to become a recruiter"},
                         headers=headers)
        assert res.status_code == 201

    def test_duplicate_request_prevention(self, client, candidate_data):
        """Test that users cannot submit multiple pending requests."""
        
        candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
        headers = {"Authorization": f"Bearer {candidate_token}"}
        
        # Submit first request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "First request"},
                         headers=headers)
        assert res.status_code == 201
        first_request_id = res.get_json()["id"]
        
        # Try to submit second request (should fail)
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Second request"},
                         headers=headers)
        assert res.status_code == 409
        assert "already have a pending recruiter request" in res.get_json()["error"]
        
        # Verify only one request exists
        res = client.get("/api/recruiter-requests/my-requests", headers=headers)
        assert res.status_code == 200
        requests = res.get_json()
        assert len(requests) == 1
        assert requests[0]["id"] == first_request_id

    def test_admin_authorization_enforcement(self, client, candidate_data):
        """Test that admin endpoints are properly protected."""
        
        candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
        headers = {"Authorization": f"Bearer {candidate_token}"}
        
        # Submit a request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test request"},
                         headers=headers)
        assert res.status_code == 201
        request_id = res.get_json()["id"]
        
        # Try to access admin endpoints as regular user (should fail)
        res = client.get("/api/admin/recruiter-requests", headers=headers)
        assert res.status_code == 403
        assert "Admin access required" in res.get_json()["error"]
        
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "Test"},
                        headers=headers)
        assert res.status_code == 403
        
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/reject",
                        json={"notes": "Test"},
                        headers=headers)
        assert res.status_code == 403

    def test_request_cleanup_functionality(self, client, candidate_data, admin_data):
        """Test that completed requests can be cleaned up."""
        
        # Create candidate and admin
        candidate_id, candidate_token = self.create_and_verify_user(client, candidate_data)
        admin_id, admin_token = self.create_admin_user(client, admin_data)
        
        candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Submit and approve request
        res = client.post("/api/recruiter-requests/", 
                         json={"reason": "Test request"},
                         headers=candidate_headers)
        assert res.status_code == 201
        request_id = res.get_json()["id"]
        
        res = client.put(f"/api/admin/recruiter-requests/{request_id}/approve",
                        json={"notes": "Approved"},
                        headers=admin_headers)
        assert res.status_code == 200
        
        # Verify request is marked for deletion
        request = db.session.get(RecruiterRequest, request_id)
        assert request.deleted_at is not None
        
        # Admin can cleanup requests
        res = client.post("/api/admin/recruiter-requests/cleanup", headers=admin_headers)
        assert res.status_code == 200
        cleanup_data = res.get_json()
        assert "Cleaned up" in cleanup_data["message"]
