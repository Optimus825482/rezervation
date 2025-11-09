# Routes package initialization
# Import all blueprints to make them available for registration

from .auth import bp as auth_bp
from .admin import bp as admin_bp
from .event import bp as event_bp
from .template import bp as template_bp
from .reservation import bp as reservation_bp
from .report import bp as report_bp
from .controller import bp as controller_bp
from .checkin import bp as checkin_bp
from .security import bp as security_bp
from .kiosk import bp as kiosk_bp
from .analytics import bp as analytics_bp

# Export all blueprints for easy importing in app/__init__.py
__all__ = [
    'auth_bp',
    'admin_bp', 
    'event_bp',
    'template_bp',
    'reservation_bp',
    'report_bp',
    'controller_bp',
    'checkin_bp',
    'security_bp',
    'kiosk_bp',
    'analytics_bp'
]
