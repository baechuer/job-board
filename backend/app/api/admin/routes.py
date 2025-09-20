from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import admin_bp
from ...services.recruiter_request_service import RecruiterRequestService
from ...schemas.recruiter_request_schema import ReviewRequestSchema, RequestListSchema
from ...common.decorators import admin_required
from ...common.exceptions import ValidationError as CustomValidationError
from marshmallow import ValidationError

# Initialize schemas
_review_schema = ReviewRequestSchema()
_list_schema = RequestListSchema()


@admin_bp.get("/recruiter-requests")
@jwt_required()
@admin_required
def get_all_requests():
    """Get all recruiter requests with filtering and pagination"""
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    requests = RecruiterRequestService().get_all_requests(
        status_filter=status_filter,
        page=page,
        per_page=per_page
    )
    return jsonify(requests), 200


@admin_bp.put("/recruiter-requests/<int:request_id>/approve")
@jwt_required()
@admin_required
def approve_request(request_id):
    """Approve a recruiter request"""
    admin_id = int(get_jwt_identity())
    
    try:
        data = _review_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="Invalid payload", details=e.messages), 400
    
    try:
        RecruiterRequestService().approve_request(
            request_id=request_id,
            admin_id=admin_id,
            notes=data.get('notes')
        )
        return jsonify({"message": "Request approved successfully"}), 200
    except CustomValidationError as e:
        return jsonify(error=str(e)), 400


@admin_bp.put("/recruiter-requests/<int:request_id>/reject")
@jwt_required()
@admin_required
def reject_request(request_id):
    """Reject a recruiter request"""
    admin_id = int(get_jwt_identity())
    
    try:
        data = _review_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="Invalid payload", details=e.messages), 400
    
    try:
        RecruiterRequestService().reject_request(
            request_id=request_id,
            admin_id=admin_id,
            notes=data.get('notes')
        )
        return jsonify({"message": "Request rejected successfully"}), 200
    except CustomValidationError as e:
        return jsonify(error=str(e)), 400


@admin_bp.post("/recruiter-requests/mark-viewed")
@jwt_required()
@admin_required
def mark_requests_as_viewed():
    """Mark all new requests as viewed by admin"""
    admin_id = int(get_jwt_identity())
    
    RecruiterRequestService().mark_requests_as_viewed(admin_id)
    return jsonify({"message": "All requests marked as viewed"}), 200


@admin_bp.post("/recruiter-requests/cleanup")
@jwt_required()
@admin_required
def cleanup_completed_requests():
    """Clean up completed requests that are past their deletion time"""
    deleted_count = RecruiterRequestService().cleanup_completed_requests()
    return jsonify({
        "message": f"Cleaned up {deleted_count} completed requests"
    }), 200
