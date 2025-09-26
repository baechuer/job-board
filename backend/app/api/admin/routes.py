from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import admin_bp
from ...services.recruiter_request_service import RecruiterRequestService
from ...schemas.recruiter_request_schema import ReviewRequestSchema, RequestListSchema
from ...common.decorators import admin_required
from ...common.exceptions import ValidationError as CustomValidationError
from marshmallow import ValidationError
from ...extensions import db
from sqlalchemy import select, func
from ...models.user_role import UserRole
from ...models.user import User
from ...models.job import Job
from hashlib import sha1

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


@admin_bp.get('/metrics')
@jwt_required()
@admin_required
def metrics():
    """Admin metrics for dashboard (no hardcoding)."""
    # Counts
    total_users = db.session.execute(select(func.count(User.id))).scalar() or 0
    total_recruiters = db.session.execute(
        select(func.count(UserRole.id)).where(UserRole.role == 'recruiter')
    ).scalar() or 0
    from datetime import datetime, UTC
    today = datetime.now(UTC).date()
    active_jobs = db.session.execute(
        select(func.count(Job.id)).where((Job.application_deadline == None) | (Job.application_deadline >= today))  # noqa: E711
    ).scalar() or 0

    # Pending recruiter requests (if model/table exists)
    pending_requests = 0
    try:
        from ...models.recruiter_request import RecruiterRequest
        pending_requests = db.session.execute(
            select(func.count(RecruiterRequest.id)).where(RecruiterRequest.status == 'pending')
        ).scalar() or 0
    except Exception:
        pass

    payload = {
        'pending_recruiter_requests': pending_requests,
        'total_users': total_users,
        'total_recruiters': total_recruiters,
        'active_jobs': active_jobs,
    }

    # Simple ETag based on payload values for efficient frontend caching
    etag_seed = f"{pending_requests}:{total_users}:{total_recruiters}:{active_jobs}".encode()
    etag = 'W/"' + sha1(etag_seed).hexdigest() + '"'
    client_etag = request.headers.get('If-None-Match')
    if client_etag == etag:
        return ('', 304, {'ETag': etag, 'Cache-Control': 'private, max-age=30'})

    resp = jsonify(payload)
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'private, max-age=30'
    return resp, 200


@admin_bp.get('/users')
@jwt_required()
@admin_required
def list_users():
    """List users for admin; filter by role=candidate|recruiter; exclude admins."""
    role = request.args.get('role')
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = request.args.get('per_page', 20, type=int)
    if per_page < 1 or per_page > 100:
        per_page = 20

    # Base: join User with UserRole; explicitly exclude admins
    q = select(User, UserRole.role).join(UserRole, UserRole.user_id == User.id)
    q = q.where(UserRole.role != 'admin')
    if role in ('candidate', 'recruiter'):
        q = q.where(UserRole.role == role)

    total = db.session.execute(select(func.count(User.id)).select_from(User).join(UserRole, UserRole.user_id == User.id).where(UserRole.role != 'admin' if role not in ('candidate','recruiter') else UserRole.role == role)).scalar() or 0

    q = q.order_by(User.created_at.desc() if hasattr(User, 'created_at') else User.id.desc())
    q = q.limit(per_page).offset((page - 1) * per_page)
    rows = db.session.execute(q).all()

    users = []
    for user, user_role in rows:
        users.append({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user_role,
            'created_at': user.created_at.isoformat() if getattr(user, 'created_at', None) else None,
        })

    return jsonify({
        'users': users,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if total else 1
        }
    }), 200
