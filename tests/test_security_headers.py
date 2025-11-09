"""
Security Headers Tests
Tests for security headers middleware and CSP reporting
"""

import json


def test_csp_header_present(app):
    """Test that CSP header is present in responses"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'Content-Security-Policy' in response.headers
        assert "default-src 'self'" in response.headers['Content-Security-Policy']


def test_x_frame_options_header(app):
    """Test that X-Frame-Options header is set"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'


def test_x_content_type_options_header(app):
    """Test that X-Content-Type-Options header is set"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'


def test_x_xss_protection_header(app):
    """Test that X-XSS-Protection header is set"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'X-XSS-Protection' in response.headers
        assert '1; mode=block' in response.headers['X-XSS-Protection']


def test_referrer_policy_header(app):
    """Test that Referrer-Policy header is set"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'Referrer-Policy' in response.headers
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'


def test_permissions_policy_header(app):
    """Test that Permissions-Policy header is set"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        assert 'Permissions-Policy' in response.headers


def test_hsts_not_in_development(app):
    """Test that HSTS is not set in development mode"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        # HSTS should not be present in development
        # unless explicitly enabled in config
        if app.debug:
            assert 'Strict-Transport-Security' not in response.headers or \
                   app.config.get('HSTS_ENABLED', False)


def test_csp_report_endpoint_exists(app):
    """Test that CSP report endpoint is registered"""
    with app.test_client() as client:
        # Send a test CSP report
        report_data = {
            'csp-report': {
                'document-uri': 'https://example.com/page',
                'violated-directive': 'script-src',
                'blocked-uri': 'https://evil.com/script.js',
                'original-policy': "default-src 'self'"
            }
        }
        response = client.post(
            '/security/csp-report',
            data=json.dumps(report_data),
            content_type='application/json'
        )
        # Should return 204 No Content on success
        assert response.status_code == 204


def test_csp_report_invalid_data(app):
    """Test CSP report endpoint with invalid data"""
    with app.test_client() as client:
        response = client.post(
            '/security/csp-report',
            data='invalid json',
            content_type='application/json'
        )
        # Should return 400 Bad Request
        assert response.status_code == 400


def test_security_headers_test_endpoint(app):
    """Test security headers test endpoint"""
    with app.test_client() as client:
        response = client.get('/security/security-headers-test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'headers_to_check' in data
        assert 'Content-Security-Policy' in data['headers_to_check']


def test_csp_includes_report_uri(app):
    """Test that CSP header includes report-uri directive"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        csp_header = response.headers.get('Content-Security-Policy', '')
        assert 'report-uri /security/csp-report' in csp_header


def test_csp_frame_ancestors_none(app):
    """Test that CSP prevents framing"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        csp_header = response.headers.get('Content-Security-Policy', '')
        assert "frame-ancestors 'none'" in csp_header


def test_all_security_headers_present(app):
    """Test that all required security headers are present"""
    with app.test_client() as client:
        response = client.get('/auth/login')
        
        required_headers = [
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Missing security header: {header}"


def test_security_headers_on_different_routes(app):
    """Test that security headers are applied to all routes"""
    with app.test_client() as client:
        routes_to_test = [
            '/auth/login',
            '/security/security-headers-test'
        ]
        
        for route in routes_to_test:
            response = client.get(route)
            assert 'Content-Security-Policy' in response.headers, \
                f"CSP header missing on {route}"
            assert 'X-Frame-Options' in response.headers, \
                f"X-Frame-Options header missing on {route}"
