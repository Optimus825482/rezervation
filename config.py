import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-me'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))

    # Database - Railway compatibility fix
    @staticmethod
    def get_database_uri():
        """Get database URI with Railway postgres:// to postgresql:// fix"""
        database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost/rezervasyon_db')
        
        # Railway uses postgres:// but SQLAlchemy needs postgresql://
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        return database_url
    
    DATABASE_URL = get_database_uri.__func__()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'pool_size': 10,        # Connection pool size
        'max_overflow': 20      # Max overflow connections
    }

    # Redis (Opsiyonel)
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    REDIS_URL = os.environ.get('REDIS_URL', None)

    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB

    # CSRF
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'

    # Security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Rate Limiting - Redis yoksa memory kullan
    # Environment'tan direkt oku, class içinde referans verme
    _redis_enabled = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    _redis_url = os.environ.get('REDIS_URL', None)
    RATELIMIT_STORAGE_URL = _redis_url if (_redis_enabled and _redis_url) else 'memory://'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = False
    
    # Development'ta Redis opsiyonel (varsayılan: kapalı)
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    
    # Session için filesystem kullan (Redis yoksa)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR', 'flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    
    # Database - Override with production settings
    DATABASE_URL = Config.get_database_uri()
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30 second query timeout
        }
    }
    
    # Secure Cookie Settings
    SESSION_COOKIE_SECURE = True      # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True    # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
    
    # Redis kontrolü ile session yapılandırması
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'true').lower() == 'true'
    
    # Session Configuration - Redis varsa kullan, yoksa filesystem
    _prod_redis_enabled = os.environ.get('REDIS_ENABLED', 'true').lower() == 'true'
    _prod_redis_url = os.environ.get('REDIS_URL', None)
    SESSION_TYPE = 'redis' if (_prod_redis_enabled and _prod_redis_url) else 'filesystem'
    SESSION_FILE_DIR = os.environ.get('SESSION_FILE_DIR', '/tmp/flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True          # Sign session cookies
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def init_app(app):
        """Production-specific initialization"""
        # Log to stderr
        import logging
        from logging import StreamHandler
        
        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Production config initialized')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SESSION_TYPE = 'null'  # Disable session for testing


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
