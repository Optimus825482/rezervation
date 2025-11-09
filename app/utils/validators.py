import phonenumbers
from phonenumbers import NumberParseException
import re
import bleach


def validate_turkish_phone(phone):
    """Validate Turkish phone number"""
    try:
        parsed = phonenumbers.parse(phone, "TR")
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False


def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """
    Validate password strength according to security policy.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password string to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalıdır"
    
    if not re.search(r'[A-Z]', password):
        return False, "Şifre en az bir büyük harf içermelidir"
    
    if not re.search(r'[a-z]', password):
        return False, "Şifre en az bir küçük harf içermelidir"
    
    if not re.search(r'\d', password):
        return False, "Şifre en az bir rakam içermelidir"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        return False, "Şifre en az bir özel karakter içermelidir (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return True, "Şifre güçlü"


def sanitize_html(text, allow_tags=None):
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        text: Text to sanitize
        allow_tags: List of allowed HTML tags (default: None - strip all tags)
        
    Returns:
        Sanitized text
    """
    if not text:
        return text
    
    # Default: strip all HTML tags
    if allow_tags is None:
        return bleach.clean(text, tags=[], strip=True)
    
    # Allow specific safe tags
    safe_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt'],
    }
    
    return bleach.clean(
        text,
        tags=allow_tags,
        attributes=safe_attrs,
        strip=True
    )


def sanitize_text_input(text):
    """
    Sanitize regular text input (names, notes, etc).
    Removes all HTML tags and dangerous content.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text with all HTML removed and whitespace stripped
    """
    if not text:
        return ''
    
    # Strip all HTML tags and strip whitespace
    cleaned = bleach.clean(str(text), tags=[], strip=True)
    return cleaned.strip()
