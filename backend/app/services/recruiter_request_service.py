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
        return RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            RecruiterRequest.status == 'pending',
            RecruiterRequest.deleted_at.is_(None)
        ).first()
    
    def get_request_status(self, user_id: int) -> dict:
        """Get current request status for user"""
        # Get the most recent request that hasn't been actually deleted yet
        request = RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            or_(
                RecruiterRequest.deleted_at.is_(None),
                RecruiterRequest.deleted_at > datetime.now(UTC)
            )
        ).order_by(RecruiterRequest.submitted_at.desc()).first()
        
        if not request:
            return {"status": "no_request", "message": "No active request found"}
        
        return self.format_request_response(request)
    
    def get_user_requests(self, user_id: int) -> list:
        """Get all requests for a user (including completed ones)"""
        requests = RecruiterRequest.query.filter(
            RecruiterRequest.user_id == user_id,
            RecruiterRequest.deleted_at.is_(None)
        ).order_by(RecruiterRequest.submitted_at.desc()).all()
        
        return [self.format_request_response(req) for req in requests]
    
    def format_request_response(self, request: RecruiterRequest) -> dict:
        """Format request response with all relevant information"""
        return {
            "id": request.id,
            "status": request.status,
            "reason": request.reason,
            "submitted_at": request.submitted_at.isoformat(),
            "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
            "feedback": request.feedback,
            "reapplication_guidance": request.reapplication_guidance,
            "admin_notes": request.admin_notes if request.status in ['approved', 'rejected'] else None
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
            RecruiterRequest.deleted_at.is_(None)
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
