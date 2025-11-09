from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_session import Session
from config import config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
# Limiter will be initialized in create_app with storage_uri
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
cors = CORS()
session = Session()

# Import security logger
from app.services.security_logger import security_logger

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'warning'

from app.models import company  # noqa


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from app.models.user import User
    return User.query.get(int(user_id))


def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    
    # Initialize limiter with storage_uri from config/env
    storage_uri = app.config.get('RATELIMIT_STORAGE_URL') or os.environ.get('RATELIMIT_STORAGE_URL')
    if storage_uri:
        limiter.storage_uri = storage_uri
    limiter.init_app(app)
    
    cors.init_app(app, supports_credentials=True)
    
    # Initialize security logger
    security_logger.init_app(app)
    
    # Initialize session with Redis
    if not app.config.get('TESTING'):
        # Ensure SESSION_TYPE is set (Flask-Session requires it in app.config)
        if not app.config.get('SESSION_TYPE'):
            app.config['SESSION_TYPE'] = 'redis'
            app.config['SESSION_PERMANENT'] = False
            app.config['SESSION_USE_SIGNER'] = True
            app.config['SESSION_KEY_PREFIX'] = 'session_'
        
        # Setup Redis connection for session
        import redis
        from urllib.parse import urlparse
        
        # Get session Redis URL (use different DB than main Redis)
        session_redis_url = os.environ.get('SESSION_REDIS') or app.config.get('REDIS_URL', 'redis://localhost:6379/1')
        
        # Parse Redis URL
        parsed = urlparse(session_redis_url)
        session_redis = redis.Redis(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 6379,
            db=int(parsed.path[1:]) if parsed.path and len(parsed.path) > 1 else 1,
            password=parsed.password,
            decode_responses=False
        )
        
        app.config['SESSION_REDIS'] = session_redis
        session.init_app(app)

    # Register blueprints
    from app.routes import auth, admin, event, template, reservation, report, controller, checkin, security
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(event.bp, url_prefix='/event')
    app.register_blueprint(template.bp, url_prefix='/template')
    app.register_blueprint(reservation.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(checkin.bp)
    app.register_blueprint(controller.bp)
    app.register_blueprint(security.bp)

    # Add context processors
    from app.utils.context_processors import inject_globals
    app.context_processor(inject_globals)

    # Register custom template filters
    from app.utils.template_filters import register_filters
    register_filters(app)

    # Get security configuration
    from app.security_config import get_security_config
    config_name = app.config.get('ENV', 'development')
    SecurityConfig = get_security_config(config_name)
    is_production = config_name == 'production'

    # Add security headers middleware with CSP nonce support
    @app.before_request
    def generate_csp_nonce():
        """Generate CSP nonce for each request"""
        from flask import g
        import secrets
        g.csp_nonce = secrets.token_urlsafe(16)
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        from flask import g
        
        # Get base security headers
        headers = SecurityConfig.get_security_headers(is_production=is_production)
        
        # Override CSP with nonce if in production and nonce method exists
        if is_production and hasattr(SecurityConfig, 'get_csp_header_with_nonce'):
            nonce = getattr(g, 'csp_nonce', None)
            if nonce:
                headers['Content-Security-Policy'] = SecurityConfig.get_csp_header_with_nonce(nonce)
        
        # Add headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response
    
    # Rate limit exceeded handler with logging
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors with logging"""
        from flask import jsonify, request
        security_logger.log_rate_limit_exceeded(
            endpoint=request.endpoint or request.path,
            limit=str(e.description)
        )
        return jsonify({
            'error': 'ratelimit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429
    
    # Legacy route redirects
    @app.route('/seating', methods=['GET', 'POST'])
    @app.route('/seating/<path:subpath>', methods=['GET', 'POST'])
    def legacy_seating_redirect(subpath=''):
        """Redirect old /seating routes to /template/seating"""
        from flask import redirect, url_for, request
        if request.method == 'POST':
            # Redirect POST to the correct endpoint
            if subpath == 'create':
                return redirect(url_for('template.create_seating_template'), code=307)
            elif 'delete' in subpath:
                # Extract ID from subpath like '123/delete'
                parts = subpath.split('/')
                if len(parts) >= 2 and parts[1] == 'delete':
                    template_id = int(parts[0])
                    return redirect(url_for('template.delete_seating_template', template_id=template_id), code=307)
        
        # GET redirects
        if subpath:
            return redirect(f'/template/seating/{subpath}', code=301)
        return redirect(url_for('template.seating_templates'), code=301)
    
    # Offline page for PWA
    @app.route('/offline.html')
    def offline():
        """Offline fallback page for PWA"""
        from flask import render_template
        return render_template('offline.html')
    
    # Service worker route - serve from root /static
    @app.route('/static/service-worker.js')
    def service_worker():
        """Serve service worker with correct headers"""
        from flask import send_from_directory, make_response
        response = make_response(send_from_directory(
            os.path.join(app.root_path, 'static'),
            'service-worker.js'
        ))
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Service-Worker-Allowed'] = '/'
        return response

    return app
