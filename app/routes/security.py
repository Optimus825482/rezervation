"""
Security Routes
Handles security-related endpoints like CSP violation reporting
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from datetime import datetime
from app import limiter
from app.services.security_logger import security_logger

bp = Blueprint('security', __name__, url_prefix='/security')


@bp.route('/csp-report', methods=['POST'])
@limiter.limit("100 per hour")  # Max 100 CSP reports per hour
def csp_report():
    """
    CSP Violation Report Endpoint with Enhanced Logging
    Receives and logs Content Security Policy violation reports
    """
    try:
        # Get CSP report from request
        report = request.get_json(force=True)
        
        if not report:
            return jsonify({'status': 'error', 'message': 'No report data'}), 400
        
        # Extract CSP report details
        csp_report = report.get('csp-report', {})
        
        # Log with security logger (structured logging)
        security_logger.log_csp_violation(csp_report)
        
        # Also log to app logger for debugging
        current_app.logger.warning(
            f"CSP Violation Report:\n"
            f"  Document URI: {csp_report.get('document-uri', 'unknown')}\n"
            f"  Violated Directive: {csp_report.get('violated-directive', 'unknown')}\n"
            f"  Blocked URI: {csp_report.get('blocked-uri', 'unknown')}\n"
            f"  Original Policy: {csp_report.get('original-policy', 'unknown')}\n"
            f"  Timestamp: {datetime.utcnow().isoformat()}"
        )
        
        # In production, you might want to:
        # - Store violations in database
        # - Send alerts for critical violations
        # - Aggregate violations for analysis
        
        return jsonify({'status': 'success'}), 204
        
    except (ValueError, BadRequest):
        # Invalid JSON
        return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
    except Exception as e:
        current_app.logger.error(f"Error processing CSP report: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@bp.route('/security-headers-test', methods=['GET'])
def security_headers_test():
    """
    Test endpoint to verify security headers are properly set
    Returns current response headers for debugging
    """
    from flask import make_response
    
    response = make_response(jsonify({
        'message': 'Security headers test endpoint',
        'headers_to_check': [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
    }))
    
    return response
