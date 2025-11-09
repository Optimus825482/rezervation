"""
Custom Jinja2 template filters for security and formatting.
"""
from app.utils.validators import sanitize_text_input, sanitize_html
from markupsafe import Markup


def safe_text(value):
    """
    Sanitize text input for safe display in templates.
    This filter escapes HTML and prevents XSS attacks.
    
    Usage in templates: {{ user_input|safe_text }}
    """
    if value is None:
        return ''
    return sanitize_text_input(str(value))


def safe_html(value, allow_tags=None):
    """
    Sanitize HTML content for safe display in templates.
    Allows only whitelisted HTML tags.
    
    Usage in templates: {{ user_html|safe_html }}
    """
    if value is None:
        return ''
    
    # Default allowed tags for rich content
    if allow_tags is None:
        allow_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    
    # Sanitize and return as Markup to prevent double-escaping
    cleaned = sanitize_html(str(value), allow_tags=allow_tags)
    return Markup(cleaned)


def format_phone(value):
    """
    Format Turkish phone number for display.
    
    Usage in templates: {{ phone|format_phone }}
    """
    if not value:
        return ''
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, str(value)))
    
    # Format as 05XX XXX XX XX
    if len(digits) == 11 and digits.startswith('0'):
        return f"{digits[0:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"
    
    return value


def register_filters(app):
    """
    Register all custom filters with the Flask app.
    
    Args:
        app: Flask application instance
    """
    app.jinja_env.filters['safe_text'] = safe_text
    app.jinja_env.filters['safe_html'] = safe_html
    app.jinja_env.filters['format_phone'] = format_phone
