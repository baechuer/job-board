from datetime import datetime, UTC, timedelta
from ..extensions import db, mail
from ..models.user import User
from ..models.user_role import UserRole
from ..models.recruiter_request import RecruiterRequest
from ..common.exceptions import ConflictError, ValidationError as CustomValidationError
from flask_mail import Message
from sqlalchemy import select, or_


class RecruiterRequestService:
    
    def submit_request(self, user_id: int, reason: str = None) -> dict:
        """Submit a new recruiter request with validation checks"""
        
        # Get user and validate email verification
        user = User.query.get_or_404(user_id)
        if not user.is_verified:
            raise CustomValidationError("Email verification required to submit recruiter request")
        
        # Check for existing pending request
        existing_pending = self.get_user_pending_request(user_id)
        if existing_pending:
            raise ConflictError("You already have a pending recruiter request")
        
        # Create new request
        request = RecruiterRequest(
            user_id=user_id,
            reason=reason,
            status='pending'
        )
        
        db.session.add(request)
        db.session.commit()
        
        return self.format_request_response(request)
    
    def get_user_pending_request(self, user_id: int) -> RecruiterRequest:
        """Get user's pending request if exists"""
        try:
            deleted_filter = or_(
                RecruiterRequest.deleted_at.is_(None),
                RecruiterRequest.deleted_at > datetime.now(UTC)
            )
        except TypeError:
            # In unit tests where RecruiterRequest is mocked, comparing mocked columns to datetime can raise TypeError
            deleted_filter = RecruiterRequest.deleted_at.is_(None)

        q = RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            RecruiterRequest.status == 'pending',
            deleted_filter,
        )
        # Keep simple to work with unit test mocks
        return q.first()
    
    def get_request_status(self, user_id: int) -> dict:
        """Get current request status for user (only 'pending' counts as active)."""
        # Look for a pending, non-deleted request first
        try:
            pending = self.get_user_pending_request(user_id)
        except TypeError:
            pending = None
        if pending and getattr(pending, 'status', None) == 'pending':
            return self.format_request_response(pending)

        # If latest request exists but is approved/rejected, treat as no active request
        try:
            deleted_filter_latest = or_(
                RecruiterRequest.deleted_at.is_(None),
                RecruiterRequest.deleted_at > datetime.now(UTC)
            )
        except TypeError:
            deleted_filter_latest = RecruiterRequest.deleted_at.is_(None)

        latest = RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            deleted_filter_latest
        ).order_by(RecruiterRequest.submitted_at.desc()).first()

        if not latest:
            return {"status": "no_request", "message": "No active request found"}

        if latest.status == "approved":
            return self.format_request_response(latest)
        if latest.status == "rejected":
            return self.format_request_response(latest)

        # Fallback
        return self.format_request_response(latest)
    
    def get_user_requests(self, user_id: int) -> list:
        """Get all requests for a user (including completed ones)"""
        requests = RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            RecruiterRequest.deleted_at.is_(None)
        ).order_by(RecruiterRequest.submitted_at.desc()).all()
        
        return [self.format_request_response(req) for req in requests]
    
    def format_request_response(self, request: RecruiterRequest) -> dict:
        """Format request response with all relevant information and user summary"""
        # Attach a short preview of the reason and basic user info for admin listing
        reason_preview = None
        if request.reason:
            preview = request.reason.strip().splitlines()[0]
            reason_preview = (preview[:120] + '…') if len(preview) > 120 else preview

        user = User.query.get(request.user_id) if request else None

        return {
            "id": request.id if request else None,
            "status": request.status if request else None,
            "reason": request.reason if request else None,
            "reason_preview": reason_preview,
            "submitted_at": request.submitted_at.isoformat() if request and request.submitted_at else None,
            "reviewed_at": request.reviewed_at.isoformat() if request and request.reviewed_at else None,
            "feedback": request.feedback if request else None,
            "reapplication_guidance": request.reapplication_guidance if request else None,
            "admin_notes": request.admin_notes if request and request.status in ['approved', 'rejected'] else None,
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else None,
                "email": user.email if user else None,
            },
        }
    
    def approve_request(self, request_id: int, admin_id: int, notes: str = None):
        """Approve request and update user role"""
        request = RecruiterRequest.query.get_or_404(request_id)
        
        if request.status != 'pending':
            raise CustomValidationError("Only pending requests can be approved")
        
        # Update request
        request.status = 'approved'
        request.reviewed_at = datetime.now(UTC)
        request.reviewed_by = admin_id
        request.admin_notes = notes
        request.feedback = "Congratulations! Your request has been approved. Welcome to the recruiter team!"
        request.reapplication_guidance = "You can now access all recruiter features and start posting jobs."
        
        # Update user role
        user = User.query.get(request.user_id)
        if not user.roles.filter(UserRole.role == 'recruiter').first():
            user.roles.append(UserRole(role='recruiter'))
        
        db.session.commit()
        
        # Send approval notification
        self.send_approval_notification(request)
        
        # Schedule request deletion (after 30 days)
        self.schedule_request_deletion(request_id, days=30)
    
    def reject_request(self, request_id: int, admin_id: int, notes: str = None):
        """Reject request with detailed feedback"""
        request = RecruiterRequest.query.get_or_404(request_id)
        
        if request.status != 'pending':
            raise CustomValidationError("Only pending requests can be rejected")
        
        # Update request
        request.status = 'rejected'
        request.reviewed_at = datetime.now(UTC)
        request.reviewed_by = admin_id
        request.admin_notes = notes
        request.feedback = self.generate_rejection_feedback(notes)
        request.reapplication_guidance = self.generate_reapplication_guidance()
        
        db.session.commit()
        
        # Send rejection notification
        self.send_rejection_notification(request)
        
        # Schedule request deletion (after 7 days)
        self.schedule_request_deletion(request_id, days=7)
    
    def generate_rejection_feedback(self, admin_notes: str = None) -> str:
        """Generate rejection feedback"""
        base_feedback = "Thank you for your interest in becoming a recruiter. Unfortunately, we cannot approve your request at this time."
        
        if admin_notes:
            return f"{base_feedback} {admin_notes}"
        
        return f"{base_feedback} Please review the requirements and consider reapplying in the future."
    
    def generate_reapplication_guidance(self) -> str:
        """Generate reapplication guidance"""
        return (
            "To improve your chances for future applications:\n"
            "1. Ensure your profile is complete and up-to-date\n"
            "2. Provide a detailed reason for wanting to become a recruiter\n"
            "3. Highlight any relevant experience or skills\n"
            "4. Wait at least 7 days before submitting a new request\n"
            "5. Consider gaining more experience on the platform before reapplying"
        )
    
    def schedule_request_deletion(self, request_id: int, days: int):
        """Schedule request for deletion after specified days"""
        deletion_time = datetime.now(UTC) + timedelta(days=days)
        request = RecruiterRequest.query.get(request_id)
        request.deleted_at = deletion_time
        db.session.commit()
    
    def cleanup_completed_requests(self):
        """Clean up requests that are past their deletion time"""
        cutoff_time = datetime.now(UTC)
        requests_to_delete = RecruiterRequest.query.filter(
            RecruiterRequest.deleted_at <= cutoff_time
        ).all()
        
        for request in requests_to_delete:
            db.session.delete(request)
        
        db.session.commit()
        return len(requests_to_delete)
    
    def get_all_requests(self, status_filter: str = None, page: int = 1, per_page: int = 10):
        """Get all requests with filtering and pagination"""
        query = RecruiterRequest.query.filter(
            or_(
                RecruiterRequest.deleted_at.is_(None),
                RecruiterRequest.deleted_at > datetime.now(UTC)
            )
        )
        
        if status_filter:
            query = query.filter(RecruiterRequest.status == status_filter)
        
        requests = query.order_by(RecruiterRequest.submitted_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            "requests": [self.format_request_response(req) for req in requests.items],
            "total": requests.total,
            "pages": requests.pages,
            "current_page": page,
            "per_page": per_page
        }
    
    def mark_requests_as_viewed(self, admin_id: int):
        """Mark all new requests as viewed by admin"""
        RecruiterRequest.query.filter(
            RecruiterRequest.is_new == True,
            RecruiterRequest.deleted_at.is_(None)
        ).update({"is_new": False})
        
        db.session.commit()
    
    def send_approval_notification(self, request: RecruiterRequest):
        """Send approval notification email"""
        user = User.query.get(request.user_id)
        try:
            msg = Message(
                subject="Recruiter Request Approved!",
                recipients=[user.email],
                body=f"""
                Congratulations! Your request to become a recruiter has been approved.
                
                You can now:
                - Post job listings
                - Access recruiter dashboard
                - Manage candidate applications
                
                Welcome to the recruiter team!
                """
            )
            mail.send(msg)
        except Exception:
            # Don't fail the approval if email fails
            pass
    
    def send_rejection_notification(self, request: RecruiterRequest):
        """Send rejection notification email"""
        user = User.query.get(request.user_id)
        try:
            msg = Message(
                subject="Recruiter Request Update",
                recipients=[user.email],
                body=f"""
                Thank you for your interest in becoming a recruiter.
                
                Unfortunately, we cannot approve your request at this time.
                
                Feedback: {request.feedback}
                
                Reapplication Guidance:
                {request.reapplication_guidance}
                
                You can submit a new request after 7 days.
                """
            )
            mail.send(msg)
        except Exception:
            # Don't fail the rejection if email fails
            pass
