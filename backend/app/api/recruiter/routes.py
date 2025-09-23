from . import recruiter_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request
from marshmallow import ValidationError
from ...services.job_service import JobService
from ...common.exceptions import BusinessLogicError
from ...schemas.recruiter_schema import RecruiterPostJobSchema
from ...schemas.recruiter_schema import RecruiterJobUpdateSchema

@recruiter_bp.get("/my-jobs")
@jwt_required()
def get_my_jobs():
    user_id = int(get_jwt_identity())
    page = int((request.args.get('page') or 1))
    per_page = int((request.args.get('per_page') or 20))
    status = request.args.get('status')
    data = JobService().list_jobs(user_id, page=page, per_page=per_page, status=status)
    return jsonify(data), 200


@recruiter_bp.get("/metrics")
@jwt_required()
def get_metrics():
    user_id = int(get_jwt_identity())
    active_jobs = JobService().count_active_jobs(user_id)
    # Applications and interviews are placeholders until implemented
    return jsonify({
        "active_jobs": active_jobs,
        "applications": 0,
        "interviews": 0,
    }), 200


@recruiter_bp.get("/my-jobs/<int:job_id>")
@jwt_required()
def get_my_job(job_id):
    user_id = int(get_jwt_identity())
    job = JobService().get_job(user_id, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify(job), 200


@recruiter_bp.post("/my-jobs/<int:job_id>/archive")
@jwt_required()
def archive_job(job_id):
    user_id = int(get_jwt_identity())
    ok = JobService().archive_job(user_id, job_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "Job archived"}), 200

@recruiter_bp.post("/my-jobs/<int:job_id>/unarchive")
@jwt_required()
def unarchive_job(job_id):
    user_id = int(get_jwt_identity())
    ok = JobService().unarchive_job(user_id, job_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "Job unarchived"}), 200

@recruiter_bp.post("/create-job")
@jwt_required()
def create_job():

    _post_schema = RecruiterPostJobSchema()
    try:
        data = _post_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="Invalid payload", details=e.messages), 400
    user_id = int(get_jwt_identity())

    try:
        result = JobService().create_job(user_id=user_id, job_data=data)
        return jsonify(result), 201
    except BusinessLogicError as e:
        return jsonify(error=str(e)), getattr(e, 'status_code', 400)


@recruiter_bp.put("/my-jobs/<int:job_id>")
@jwt_required()
def update_job(job_id):
    user_id = int(get_jwt_identity())
    schema = RecruiterJobUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(error="Invalid payload", details=e.messages), 400
    result = JobService().update_job(user_id, job_id, data)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result), 200


@recruiter_bp.get("/jobs")
def public_jobs():
    q = request.args.get('q')
    page = int((request.args.get('page') or 1))
    per_page = int((request.args.get('per_page') or 20))
    data = JobService().search_public_jobs(q, page=page, per_page=per_page)
    return jsonify(data), 200


@recruiter_bp.get("/jobs/<int:job_id>")
def public_job_detail(job_id):
    data = JobService().get_public_job(job_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data), 200