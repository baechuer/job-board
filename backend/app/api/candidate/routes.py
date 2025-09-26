from . import candidate_bp
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...services.saved_job_service import SavedJobService


@candidate_bp.get('/saved-jobs')
@jwt_required()
def list_saved_jobs():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    data = SavedJobService().list(user_id, page=page, per_page=per_page)
    return jsonify(data), 200


@candidate_bp.get('/saved-jobs/status/<int:job_id>')
@jwt_required()
def saved_status(job_id):
    user_id = int(get_jwt_identity())
    saved = SavedJobService().is_saved(user_id, job_id)
    return jsonify({"saved": saved}), 200


@candidate_bp.post('/saved-jobs/<int:job_id>')
@jwt_required()
def save_job(job_id):
    user_id = int(get_jwt_identity())
    result = SavedJobService().save(user_id, job_id)
    return jsonify(result), 200


@candidate_bp.delete('/saved-jobs/<int:job_id>')
@jwt_required()
def unsave_job(job_id):
    user_id = int(get_jwt_identity())
    result = SavedJobService().unsave(user_id, job_id)
    return jsonify(result), 200


