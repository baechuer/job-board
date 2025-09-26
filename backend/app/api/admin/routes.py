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
from datetime import datetime, UTC

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


@admin_bp.get('/activity_recent')
@jwt_required()
@admin_required
def activity_recent():
    """Return a small recent activity feed aggregated from users, jobs, and recruiter requests."""
    items = []
    try:
        # Latest users
        latest_users = db.session.execute(
            select(User).order_by(User.created_at.desc()).limit(5)
        ).scalars().all()
        for u in latest_users:
            items.append({
                'type': 'user',
                'when': u.created_at.isoformat() if u.created_at else None,
                'message': f"User {u.email} registered",
                'level': 'info',
            })
    except Exception:
        pass
    try:
        # Latest jobs
        latest_jobs = db.session.execute(
            select(Job).order_by(Job.id.desc()).limit(5)
        ).scalars().all()
        for j in latest_jobs:
            items.append({
                'type': 'job',
                'when': None,
                'message': f"Job '{getattr(j, 'title', 'Untitled')}' created",
                'level': 'primary',
            })
    except Exception:
        pass
    try:
        from ...models.recruiter_request import RecruiterRequest
        latest_req = db.session.execute(
            select(RecruiterRequest).order_by(RecruiterRequest.created_at.desc()).limit(5)
        ).scalars().all()
        for r in latest_req:
            items.append({
                'type': 'recruiter_request',
                'when': r.created_at.isoformat() if getattr(r, 'created_at', None) else None,
                'message': f"Recruiter request from {getattr(r, 'email', 'unknown')}",
                'level': 'success' if getattr(r, 'status', '') == 'approved' else 'warning' if getattr(r, 'status','')=='pending' else 'muted',
            })
    except Exception:
        pass

    # Sort by when desc, unknown last
    def _key(it):
        try:
            return datetime.fromisoformat(it['when']) if it.get('when') else datetime.min
        except Exception:
            return datetime.min
    items.sort(key=_key, reverse=True)

    return jsonify({'items': items[:10]}), 200


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


@admin_bp.get('/users/<int:user_id>')
@jwt_required()
@admin_required
def get_user_detail(user_id):
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify(error='user not found'), 404
    roles = [r.role for r in user.roles]
    return jsonify({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'roles': roles,
        'created_at': user.created_at.isoformat() if getattr(user, 'created_at', None) else None,
        'is_verified': getattr(user, 'is_verified', False),
    }), 200


@admin_bp.put('/users/<int:user_id>')
@jwt_required()
@admin_required
def update_user_detail(user_id):
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify(error='user not found'), 404
    payload = request.get_json(silent=True) or {}
    updated = False
    # Update username/email without code (admin-only)
    new_username = payload.get('username')
    if isinstance(new_username, str) and new_username.strip() and new_username != user.username:
        user.username = new_username.strip()
        updated = True
    new_email = payload.get('email')
    if isinstance(new_email, str) and new_email.strip() and new_email.lower() != user.email:
        user.email = new_email.strip().lower()
        updated = True
    # Optionally update role
    role = payload.get('role')
    if role in ('candidate', 'recruiter', 'admin'):
        from ...models.user_role import UserRole
        # Remove all non-admin roles if setting admin? keep simple: ensure exactly one role provided
        # For safety, clear existing role entries of candidate/recruiter/admin and add new one
        for r in user.roles.all():
            db.session.delete(r)
        db.session.add(UserRole(user_id=user.id, role=role))
        updated = True
    if not updated:
        return jsonify(msg='no changes'), 200
    db.session.commit()
    return jsonify(msg='user updated'), 200