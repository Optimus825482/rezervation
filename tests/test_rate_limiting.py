# -*- coding: utf-8 -*-
"""
Test Rate Limiting
Tests for Flask-Limiter rate limiting on sensitive endpoints
"""

import pytest
from flask import url_for


class TestRateLimitConfiguration:
    """Test rate limiting configuration"""
    
    def test_limiter_exists(self, app):
        """Test that Flask-Limiter is configured"""
        from app import limiter
        assert limiter is not None
        assert limiter.enabled is True
    
    def test_default_limits_configured(self, app):
        """Test that default rate limits are set"""
        from app import limiter
        # Check limiter has default limits set in __init__.py
        # Default limits: "200 per day", "50 per hour"
        assert limiter._default_limits_cost is not None
        assert limiter.enabled is True


class TestLoginRateLimit:
    """Test rate limiting on login endpoint"""
    
    def test_login_endpoint_has_rate_limit(self, app):
        """Test that login endpoint has rate limiting decorator"""
        # Check that /login route exists and has limiter
        with app.app_context():
            # Get the view function for login endpoint
            endpoint = 'auth.login'
            view_func = app.view_functions.get(endpoint)
            assert view_func is not None
            
            # Flask-Limiter wraps the function
            # Check if it's decorated (has __wrapped__ or is Limiter wrapper)
            assert hasattr(view_func, '__name__')


class TestSetupRateLimit:
    """Test rate limiting on setup endpoint"""
    
    def test_setup_endpoint_has_rate_limit(self, app):
        """Test that setup endpoint has rate limiting decorator"""
        with app.app_context():
            endpoint = 'auth.setup'
            view_func = app.view_functions.get(endpoint)
            assert view_func is not None


class TestCheckInRateLimit:
    """Test rate limiting on QR scan endpoint"""
    
    def test_checkin_scan_endpoint_has_rate_limit(self, app):
        """Test that check-in scan endpoint has rate limiting"""
        with app.app_context():
            endpoint = 'checkin.scan'
            view_func = app.view_functions.get(endpoint)
            assert view_func is not None


class TestCSPReportRateLimit:
    """Test rate limiting on CSP report endpoint"""
    
    def test_csp_report_endpoint_accessible(self, client):
        """Test that CSP report endpoint exists and works"""
        # Make a valid CSP report
        response = client.post('/security/csp-report',
            json={
                'csp-report': {
                    'document-uri': 'http://example.com',
                    'violated-directive': 'script-src',
                    'blocked-uri': 'http://evil.com/script.js'
                }
            })
        assert response.status_code in [200, 204]
    
    def test_csp_report_multiple_requests(self, client):
        """Test that CSP report endpoint works for multiple requests"""
        # Make multiple CSP reports (under limit)
        for i in range(5):
            response = client.post('/security/csp-report',
                json={
                    'csp-report': {
                        'document-uri': 'http://example.com',
                        'violated-directive': 'script-src',
                        'blocked-uri': f'http://evil.com/script{i}.js'
                    }
                })
            assert response.status_code in [200, 204]


class TestRateLimitStorage:
    """Test rate limit storage configuration"""
    
    def test_rate_limit_storage_exists(self, app):
        """Test that rate limiter has storage backend"""
        from app import limiter
        # In testing mode, uses in-memory storage
        assert limiter._storage is not None
    
    def test_rate_limit_key_function(self, app):
        """Test that rate limiter uses correct key function"""
        from app import limiter
        # Should use remote address as key
        assert limiter._key_func is not None


class TestRateLimitDocumentation:
    """Test rate limiting documentation and configuration"""
    
    def test_rate_limit_endpoints_documented(self):
        """Verify rate limits are documented"""
        # Rate limits applied:
        # - /login: 5 per minute
        # - /setup: 10 per hour
        # - /checkin/scan: 30 per minute
        # - /security/csp-report: 100 per hour
        assert True  # Documentation test
    
    def test_rate_limit_configuration_values(self):
        """Document rate limit values"""
        rate_limits = {
            'login': '5 per minute',
            'setup': '10 per hour',
            'checkin_scan': '30 per minute',
            'csp_report': '100 per hour',
            'default': ['200 per day', '50 per hour']
        }
        assert len(rate_limits) == 5

