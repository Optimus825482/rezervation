# -*- coding: utf-8 -*-
"""
Security Event Logger
Logs security-related events for audit trail and monitoring
"""

import logging
from datetime import datetime
from flask import request
import json
import os


class SecurityLogger:
    """Centralized security event logging"""
    
    def __init__(self, app=None):
        self.logger = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security logger with Flask app"""
        # Create security logger
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if not exists
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # File handler for security events
        log_file = os.path.join(log_dir, 'security.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler
        self.logger.addHandler(file_handler)
        
        # Also log to console in development
        if app.config.get('DEBUG'):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _get_request_info(self):
        """Extract request information for logging"""
        return {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'path': request.path,
            'method': request.method,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def log_failed_login(self, username, reason='Invalid credentials'):
        """Log failed login attempt"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'failed_login',
            'username': username,
            'reason': reason,
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"Failed login attempt - Username: {username}, "
            f"IP: {event_data['ip']}, Reason: {reason}"
        )
        
        # Store structured event data
        self._log_structured_event(event_data)
    
    def log_successful_login(self, username, user_id):
        """Log successful login"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'successful_login',
            'username': username,
            'user_id': user_id,
            **self._get_request_info()
        }
        
        self.logger.info(
            f"Successful login - Username: {username}, "
            f"User ID: {user_id}, IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def log_validation_error(self, schema_name, field, error_message, input_value=None):
        """Log schema validation error (potential XSS or malicious input)"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'validation_error',
            'schema': schema_name,
            'field': field,
            'error': error_message,
            'input_value': str(input_value)[:100] if input_value else None,  # Limit length
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"Validation error - Schema: {schema_name}, "
            f"Field: {field}, Error: {error_message}, "
            f"IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def log_xss_attempt(self, field, input_value):
        """Log potential XSS attempt"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'xss_attempt',
            'field': field,
            'input_value': str(input_value)[:200],  # Limit to 200 chars
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"Potential XSS attempt detected - Field: {field}, "
            f"IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def log_csp_violation(self, violation_data):
        """Log Content Security Policy violation"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'csp_violation',
            'document_uri': violation_data.get('document-uri'),
            'violated_directive': violation_data.get('violated-directive'),
            'blocked_uri': violation_data.get('blocked-uri'),
            'source_file': violation_data.get('source-file'),
            'line_number': violation_data.get('line-number'),
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"CSP Violation - Directive: {event_data['violated_directive']}, "
            f"Blocked: {event_data['blocked_uri']}, "
            f"IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def log_rate_limit_exceeded(self, endpoint, limit):
        """Log rate limit exceeded event"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'rate_limit_exceeded',
            'endpoint': endpoint,
            'limit': limit,
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"Rate limit exceeded - Endpoint: {endpoint}, "
            f"Limit: {limit}, IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def log_unauthorized_access(self, resource, required_role=None):
        """Log unauthorized access attempt"""
        if not self.logger:
            return
        
        event_data = {
            'event_type': 'unauthorized_access',
            'resource': resource,
            'required_role': required_role,
            **self._get_request_info()
        }
        
        self.logger.warning(
            f"Unauthorized access attempt - Resource: {resource}, "
            f"Required role: {required_role}, IP: {event_data['ip']}"
        )
        
        self._log_structured_event(event_data)
    
    def _log_structured_event(self, event_data):
        """Log structured event data to separate JSON log file"""
        if not self.logger:
            return
        
        try:
            # Get app root path
            log_dir = os.path.dirname(self.logger.handlers[0].baseFilename)
            json_log_file = os.path.join(log_dir, 'security_events.json')
            
            # Append event to JSON log
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write structured event: {e}")


# Global security logger instance
security_logger = SecurityLogger()
