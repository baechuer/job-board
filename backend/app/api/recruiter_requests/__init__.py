from flask import Blueprint

recruiter_requests_bp = Blueprint("recruiter_requests", __name__, url_prefix="/recruiter-requests")

from . import routes
