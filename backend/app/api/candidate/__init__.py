from flask import Blueprint

candidate_bp = Blueprint('candidate', __name__)

from . import routes  # noqa: F401


