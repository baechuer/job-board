from . import recruiter_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, request
from marshmallow import ValidationError
from ...services.job_service import JobService
from ...common.exceptions import BusinessLogicError
from ...schemas.recruiter_schema import RecruiterPostJobSchema
@recruiter_bp.get("/")
@jwt_required()
def get_recruiter_profile():
    return jsonify({"message": "Recruiter profile"}), 200



@recruiter_bp.get("/my-jobs")
@jwt_required()
def get_my_jobs():
    return jsonify({"message": "My jobs"}), 200


@recruiter_bp.get("/my-jobs/<int:job_id>")
@jwt_required()
def get_my_job(job_id):
    return jsonify({"message": "My job"}), 200


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