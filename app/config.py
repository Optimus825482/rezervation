import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-me'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost/rezervasyon_db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost/rezervasyon_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Flask-Session Configuration
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'redis')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT', 'False').lower() == 'true'
    SESSION_USE_SIGNER = os.environ.get('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'session_')
    SESSION_REDIS = None  # Will be set in __init__.py from Redis connection

    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB

    # CSRF
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'

    # Security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or REDIS_URL

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
