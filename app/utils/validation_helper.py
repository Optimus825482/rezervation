# -*- coding: utf-8 -*-
"""
Validation Helper with Security Logging
Wraps schema validation to log security events
"""

from marshmallow import ValidationError
from app.services.security_logger import security_logger


def validate_with_logging(schema, data, schema_name=None):
    """
    Validate data with schema and log validation errors
    
    Args:
        schema: Marshmallow schema instance
        data: Data to validate
        schema_name: Name of schema (for logging)
    
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    if schema_name is None:
        schema_name = schema.__class__.__name__
    
    try:
        # Validate data
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as err:
        # Log each validation error
        for field, messages in err.messages.items():
            for message in messages:
                # Get input value if available
                input_value = data.get(field) if isinstance(data, dict) else None
                
                # Log validation error
                security_logger.log_validation_error(
                    schema_name=schema_name,
                    field=field,
                    error_message=message,
                    input_value=input_value
                )
                
                # Detect potential XSS attempts
                if input_value and isinstance(input_value, str):
                    xss_patterns = [
                        '<script', 'javascript:', 'onerror=', 'onclick=',
                        'onload=', '<iframe', 'eval(', 'alert('
                    ]
                    if any(pattern in input_value.lower() for pattern in xss_patterns):
                        security_logger.log_xss_attempt(field, input_value)
        
        # Re-raise the error
        raise


def log_validation_errors(schema_name, errors, data):
    """
    Log validation errors from marshmallow ValidationError
    
    Args:
        schema_name: Name of the schema
        errors: Error dictionary from ValidationError
        data: Original input data
    """
    for field, messages in errors.items():
        if isinstance(messages, list):
            for message in messages:
                input_value = data.get(field) if isinstance(data, dict) else None
                security_logger.log_validation_error(
                    schema_name=schema_name,
                    field=field,
                    error_message=message,
                    input_value=input_value
                )
                
                # Check for XSS patterns
                if input_value and isinstance(input_value, str):
                    xss_patterns = [
                        '<script', 'javascript:', 'onerror=', 'onclick=',
                        'onload=', '<iframe', 'eval(', 'alert('
                    ]
                    if any(pattern in input_value.lower() for pattern in xss_patterns):
                        security_logger.log_xss_attempt(field, input_value)
