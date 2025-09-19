from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from .exceptions import BusinessLogicError
import traceback

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(err):
        msg = getattr(err, "description", "bad request")
        return jsonify(error=msg), 400

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="not found"), 404

    @app.errorhandler(422)
    def unprocessable(err):
        msg = getattr(err, "description", "unprocessable")
        return jsonify(error=msg), 422

    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(err):
        # Log the error for debugging
        app.logger.warning(f"Business Logic Error: {err.message}")
        # Return the actual error message to frontend
        return jsonify(error=err.message), err.status_code

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        # Handle ValueError as business logic errors (like your current auth service)
        app.logger.warning(f"Value Error: {str(err)}")
        return jsonify(error=str(err)), 400

    @app.errorhandler(Exception)
    def internal(err):
        # Log the full error for debugging
        app.logger.exception(err)
        
        # Check if it's a custom business logic error with a message
        error_msg = getattr(err, "description", None)
        if error_msg:
            # Return the actual error message for business logic errors
            return jsonify(error=error_msg), 500
        
        # For unexpected errors, return a generic message
        return jsonify(error="An unexpected error occurred. Please try again."), 500

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(err):
        return jsonify({"errors": err.normalized_messages()}), 400