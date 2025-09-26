"""
Health check and monitoring API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.services.monitoring_service import get_database_health, get_health_summary, db_monitor
from app.models.user_role import UserRole

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

@monitoring_bp.get("/health")
def health_check():
    """Public health check endpoint"""
    try:
        health_status = get_database_health()
        
        # Return appropriate HTTP status code
        if health_status['overall_status'] == 'healthy':
            return jsonify(health_status), 200
        elif health_status['overall_status'] == 'unhealthy':
            return jsonify(health_status), 503  # Service Unavailable
        else:
            return jsonify(health_status), 500  # Internal Server Error
            
    except Exception as e:
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@monitoring_bp.get("/health/summary")
@jwt_required()
def health_summary():
    """Get health check summary (requires authentication)"""
    try:
        # Check if user is admin
        user_id = int(get_jwt_identity())
        user_role = UserRole.query.filter_by(user_id=user_id).first()
        
        if not user_role or user_role.role != 'admin':
            return jsonify(error="Admin access required"), 403
        
        summary = get_health_summary()
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify(error=str(e)), 500

@monitoring_bp.get("/health/history")
@jwt_required()
def health_history():
    """Get health check history (requires admin authentication)"""
    try:
        # Check if user is admin
        user_id = int(get_jwt_identity())
        user_role = UserRole.query.filter_by(user_id=user_id).first()
        
        if not user_role or user_role.role != 'admin':
            return jsonify(error="Admin access required"), 403
        
        hours = request.args.get('hours', 24, type=int)
        history = db_monitor.get_health_history(hours=hours)
        
        return jsonify({
            'history': history,
            'hours_requested': hours,
            'total_checks': len(history)
        }), 200
        
    except Exception as e:
        return jsonify(error=str(e)), 500

@monitoring_bp.post("/health/check")
@jwt_required()
def trigger_health_check():
    """Trigger a new health check (requires admin authentication)"""
    try:
        # Check if user is admin
        user_id = int(get_jwt_identity())
        user_role = UserRole.query.filter_by(user_id=user_id).first()
        
        if not user_role or user_role.role != 'admin':
            return jsonify(error="Admin access required"), 403
        
        health_status = get_database_health()
        
        return jsonify({
            'message': 'Health check triggered',
            'result': health_status
        }), 200
        
    except Exception as e:
        return jsonify(error=str(e)), 500
