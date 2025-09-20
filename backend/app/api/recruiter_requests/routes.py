from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import recruiter_requests_bp
from ...services.recruiter_request_service import RecruiterRequestService
from ...schemas.recruiter_request_schema import (
    SubmitRequestSchema,
    ReviewRequestSchema,
    RequestStatusSchema,
    RequestListSchema,
)
from ...common.exceptions import ConflictError, ValidationError as CustomValidationError
from marshmallow import ValidationError

# Initialize schemas
_submit_schema = SubmitRequestSchema()
_review_schema = ReviewRequestSchema()
_status_schema = RequestStatusSchema()
_list_schema = RequestListSchema()


@recruiter_requests_bp.post("/")
@jwt_required()
def submit_request():
    """Submit a new recruiter request"""
    user_id = int(get_jwt_identity())
    
    try:
        data = _submit_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="Invalid payload", details=e.messages), 400
    
    try:
        result = RecruiterRequestService().submit_request(
            user_id=user_id,
            reason=data.get('reason')
        )
        return jsonify(result), 201
    except CustomValidationError as e:
        return jsonify(error=str(e)), 400
    except ConflictError as e:
        return jsonify(error=str(e)), 409


@recruiter_requests_bp.get("/my-status")
@jwt_required()
def get_my_request_status():
    """Get current request status for authenticated user"""
    user_id = int(get_jwt_identity())
    status = RecruiterRequestService().get_request_status(user_id)
    return jsonify(status), 200


@recruiter_requests_bp.get("/my-requests")
@jwt_required()
def get_my_requests():
    """Get all requests for authenticated user"""
    user_id = int(get_jwt_identity())
    requests = RecruiterRequestService().get_user_requests(user_id)
    return jsonify(requests), 200
