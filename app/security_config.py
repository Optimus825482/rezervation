"""
Security Configuration
Environment-based security settings for headers, CSP, CORS, etc.
"""

import os
from typing import Dict


class SecurityConfig:
    """Security configuration for the application"""
    
    # Content Security Policy
    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com https://unpkg.com https://cdn.tailwindcss.com"
    CSP_STYLE_SRC = "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com"
    CSP_FONT_SRC = "'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    CSP_IMG_SRC = "'self' data: blob:"
    CSP_CONNECT_SRC = "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    CSP_FRAME_ANCESTORS = "'none'"
    CSP_BASE_URI = "'self'"
    CSP_FORM_ACTION = "'self'"
    CSP_REPORT_URI = "/security/csp-report"
    
    # Frame Options
    X_FRAME_OPTIONS = 'DENY'
    
    # Content Type Options
    X_CONTENT_TYPE_OPTIONS = 'nosniff'
    
    # XSS Protection (legacy browsers)
    X_XSS_PROTECTION = '1; mode=block'
    
    # HSTS (HTTP Strict Transport Security)
    HSTS_ENABLED = os.getenv('HSTS_ENABLED', 'False').lower() == 'true'
    HSTS_MAX_AGE = int(os.getenv('HSTS_MAX_AGE', '31536000'))  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = os.getenv('HSTS_INCLUDE_SUBDOMAINS', 'True').lower() == 'true'
    HSTS_PRELOAD = os.getenv('HSTS_PRELOAD', 'False').lower() == 'true'
    
    # Referrer Policy
    REFERRER_POLICY = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    PERMISSIONS_POLICY = 'geolocation=(), microphone=(), camera=()'
    
    @classmethod
    def get_csp_header(cls) -> str:
        """Build Content Security Policy header"""
        return (
            f"default-src {cls.CSP_DEFAULT_SRC}; "
            f"script-src {cls.CSP_SCRIPT_SRC}; "
            f"style-src {cls.CSP_STYLE_SRC}; "
            f"font-src {cls.CSP_FONT_SRC}; "
            f"img-src {cls.CSP_IMG_SRC}; "
            f"connect-src {cls.CSP_CONNECT_SRC}; "
            f"frame-ancestors {cls.CSP_FRAME_ANCESTORS}; "
            f"base-uri {cls.CSP_BASE_URI}; "
            f"form-action {cls.CSP_FORM_ACTION}; "
            f"report-uri {cls.CSP_REPORT_URI}"
        )
    
    @classmethod
    def get_hsts_header(cls) -> str:
        """Build HSTS header"""
        parts = [f'max-age={cls.HSTS_MAX_AGE}']
        if cls.HSTS_INCLUDE_SUBDOMAINS:
            parts.append('includeSubDomains')
        if cls.HSTS_PRELOAD:
            parts.append('preload')
        return '; '.join(parts)
    
    @classmethod
    def get_security_headers(cls, is_production: bool = False) -> Dict[str, str]:
        """
        Get all security headers as a dictionary
        
        Args:
            is_production: Whether running in production mode
            
        Returns:
            Dictionary of header name to value
        """
        headers = {
            'Content-Security-Policy': cls.get_csp_header(),
            'X-Frame-Options': cls.X_FRAME_OPTIONS,
            'X-Content-Type-Options': cls.X_CONTENT_TYPE_OPTIONS,
            'X-XSS-Protection': cls.X_XSS_PROTECTION,
            'Referrer-Policy': cls.REFERRER_POLICY,
            'Permissions-Policy': cls.PERMISSIONS_POLICY
        }
        
        # Only add HSTS in production or if explicitly enabled
        if is_production or cls.HSTS_ENABLED:
            headers['Strict-Transport-Security'] = cls.get_hsts_header()
        
        return headers


class DevelopmentSecurityConfig(SecurityConfig):
    """Security configuration for development environment"""
    # Relaxed CSP for development
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.tailwindcss.com"
    CSP_STYLE_SRC = "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com"
    CSP_FONT_SRC = "'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    CSP_CONNECT_SRC = "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    
    # No HSTS in development
    HSTS_ENABLED = False


class ProductionSecurityConfig(SecurityConfig):
    """Security configuration for production environment"""
    
    # Strict CSP for production - remove unsafe-inline and unsafe-eval
    # Use nonce-based approach for inline scripts/styles
    CSP_SCRIPT_SRC = "'self' https://cdn.jsdelivr.net https://code.jquery.com https://unpkg.com https://cdn.tailwindcss.com"
    CSP_STYLE_SRC = "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com"
    CSP_FONT_SRC = "'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    CSP_CONNECT_SRC = "'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com"
    
    # Strict image sources - remove blob: if not needed
    CSP_IMG_SRC = "'self' data:"
    
    # Enable HSTS in production
    HSTS_ENABLED = True
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = False  # Set to True only after testing and submitting to preload list
    
    @classmethod
    def get_csp_header_with_nonce(cls, nonce: str) -> str:
        """
        Build Content Security Policy header with nonce for inline scripts/styles
        
        Args:
            nonce: Cryptographically secure random nonce for this request
            
        Returns:
            CSP header string with nonce
        """
        return (
            f"default-src {cls.CSP_DEFAULT_SRC}; "
            f"script-src {cls.CSP_SCRIPT_SRC} 'nonce-{nonce}'; "
            f"style-src {cls.CSP_STYLE_SRC} 'nonce-{nonce}'; "
            f"font-src {cls.CSP_FONT_SRC}; "
            f"img-src {cls.CSP_IMG_SRC}; "
            f"connect-src {cls.CSP_CONNECT_SRC}; "
            f"frame-ancestors {cls.CSP_FRAME_ANCESTORS}; "
            f"base-uri {cls.CSP_BASE_URI}; "
            f"form-action {cls.CSP_FORM_ACTION}; "
            f"report-uri {cls.CSP_REPORT_URI}"
        )


# Configuration mapping
security_config = {
    'development': DevelopmentSecurityConfig,
    'production': ProductionSecurityConfig,
    'default': SecurityConfig
}


def get_security_config(config_name: str = 'default') -> type:
    """
    Get security configuration class for environment
    
    Args:
        config_name: Configuration name (development, production, default)
        
    Returns:
        Security configuration class
    """
    return security_config.get(config_name, SecurityConfig)
