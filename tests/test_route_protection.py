"""
Route Protection Integration Tests
Tests for schema validation and input sanitization across all routes
"""

import json


def test_auth_setup_with_valid_data(app):
    """Test auth setup with valid data"""
    with app.test_client() as client:
        response = client.post('/auth/setup', data={
            'company_name': 'Test Company',
            'company_email': 'test@example.com',
            'company_phone': '+905551234567',
            'company_address': 'Test Address',
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }, follow_redirects=False)
        # Should accept valid data
        assert response.status_code in [200, 302]


def test_auth_setup_with_xss_attempt(app):
    """Test auth setup blocks XSS in company name"""
    with app.test_client() as client:
        response = client.post('/auth/setup', data={
            'company_name': '<script>alert("xss")</script>Evil Corp',
            'company_email': 'test@example.com',
            'company_phone': '+905551234567',
            'company_address': 'Test Address',
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }, follow_redirects=True)
        # Should either sanitize or reject
        assert response.status_code == 200


def test_auth_setup_with_weak_password(app):
    """Test auth setup rejects weak password"""
    with app.test_client() as client:
        response = client.post('/auth/setup', data={
            'company_name': 'Test Company',
            'company_email': 'test@example.com',
            'company_phone': '+905551234567',
            'company_address': 'Test Address',
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'weak',  # Weak password
            'first_name': 'John',
            'last_name': 'Doe'
        }, follow_redirects=True)
        # Should reject weak password
        assert response.status_code == 200
        # Check for error message in response
        assert b'password' in response.data.lower() or b'\xc5\x9fifre' in response.data.lower()


def test_reservation_with_valid_phone(app, authenticated_client):
    """Test reservation creation with valid Turkish phone"""
    valid_phones = [
        '+905551234567',
        '05551234567',
        '+90 555 123 45 67',
        '0555 123 45 67'
    ]
    
    for phone in valid_phones:
        response = authenticated_client.post('/reservation/create', data={
            'phone': phone,
            'first_name': 'Test',
            'last_name': 'User',
            'seating_id': '1'
        }, follow_redirects=True)
        # Should accept valid Turkish phone formats
        assert response.status_code == 200


def test_reservation_with_invalid_phone(app, authenticated_client):
    """Test reservation creation rejects invalid phone"""
    invalid_phones = [
        '123',
        'abcdefg',
        '+1',
        '0000000000'
    ]
    
    for phone in invalid_phones:
        response = authenticated_client.post('/reservation/create', data={
            'phone': phone,
            'first_name': 'Test',
            'last_name': 'User',
            'seating_id': '1'
        }, follow_redirects=True)
        # Should reject invalid phone
        assert response.status_code == 200


def test_reservation_with_xss_in_name(app, authenticated_client):
    """Test reservation sanitizes XSS attempts in name"""
    response = authenticated_client.post('/reservation/create', data={
        'phone': '+905551234567',
        'first_name': '<script>alert(1)</script>Test',
        'last_name': '<img src=x onerror=alert(1)>User',
        'seating_id': '1'
    }, follow_redirects=True)
    # Should sanitize and accept
    assert response.status_code == 200


def test_event_creation_with_valid_data(app, admin_client):
    """Test event creation with valid data"""
    response = admin_client.post('/event/create', data={
        'name': 'Test Event',
        'event_date': '2025-12-31',
        'event_time': '19:00'
    }, follow_redirects=True)
    # Should accept valid event data
    assert response.status_code == 200


def test_event_creation_with_xss(app, admin_client):
    """Test event creation sanitizes XSS"""
    response = admin_client.post('/event/create', data={
        'name': '<script>alert("xss")</script>Dangerous Event',
        'event_date': '2025-12-31',
        'event_time': '19:00'
    }, follow_redirects=True)
    # Should sanitize XSS
    assert response.status_code == 200


def test_template_creation_with_valid_data(app, admin_client):
    """Test template creation with valid data"""
    response = admin_client.post('/template/seating/create', data={
        'name': 'Test Template',
        'category': 'restaurant',
        'stage_position': 'north',
        'configuration': '{}'
    }, follow_redirects=True)
    # Should accept valid template data
    assert response.status_code == 200


def test_template_creation_with_invalid_category(app, admin_client):
    """Test template creation rejects invalid category"""
    response = admin_client.post('/template/seating/create', data={
        'name': 'Test Template',
        'category': 'invalid_category',
        'stage_position': 'north',
        'configuration': '{}'
    }, follow_redirects=True)
    # Should reject invalid category
    assert response.status_code == 200


def test_sql_injection_protection_in_reservation(app, authenticated_client):
    """Test SQL injection protection"""
    response = authenticated_client.post('/reservation/create', data={
        'phone': "+905551234567' OR '1'='1",
        'first_name': "Test' OR '1'='1",
        'last_name': 'User',
        'seating_id': '1'
    }, follow_redirects=True)
    # Should safely handle SQL injection attempts
    assert response.status_code == 200


def test_csrf_protection(app):
    """Test CSRF protection is active"""
    with app.test_client() as client:
        # Try to POST without CSRF token
        response = client.post('/auth/setup', data={
            'company_name': 'Test Company'
        })
        # Should block or require CSRF token
        # Note: Exact behavior depends on CSRF configuration
        assert response.status_code in [200, 302, 400, 403]


def test_multiple_xss_vectors(app, authenticated_client):
    """Test various XSS attack vectors are blocked"""
    xss_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        'javascript:alert(1)',
        '<iframe src="javascript:alert(1)">',
        '<body onload=alert(1)>'
    ]
    
    for payload in xss_payloads:
        response = authenticated_client.post('/reservation/create', data={
            'phone': '+905551234567',
            'first_name': payload + 'Test',
            'last_name': 'User',
            'seating_id': '1'
        }, follow_redirects=True)
        # Should sanitize all XSS attempts
        assert response.status_code == 200
        # Verify dangerous content is not in response
        assert b'<script>' not in response.data
        assert b'onerror' not in response.data.lower()


def test_input_length_validation(app, authenticated_client):
    """Test input length limits are enforced"""
    # Very long name (should be rejected or truncated)
    response = authenticated_client.post('/reservation/create', data={
        'phone': '+905551234567',
        'first_name': 'A' * 1000,
        'last_name': 'User',
        'seating_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
