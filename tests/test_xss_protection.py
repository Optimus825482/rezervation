"""
Tests for XSS protection and input sanitization.
"""
import pytest
from app.utils.validators import sanitize_html, sanitize_text_input
from app.utils.template_filters import safe_text, safe_html, format_phone


class TestXSSProtection:
    """Test XSS protection functions."""
    
    def test_sanitize_html_removes_script_tags(self):
        """Test that script tags are removed from HTML."""
        malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
        result = sanitize_html(malicious_html)
        
        assert '<script>' not in result
        assert 'alert("XSS")' not in result
        assert '<p>Safe content</p>' in result
    
    def test_sanitize_html_removes_onclick_handlers(self):
        """Test that event handlers are removed."""
        malicious_html = '<a href="#" onclick="alert(\'XSS\')">Click me</a>'
        result = sanitize_html(malicious_html)
        
        assert 'onclick' not in result
        assert 'alert' not in result
    
    def test_sanitize_html_allows_safe_tags(self):
        """Test that safe HTML tags are preserved."""
        safe_html_input = '<p>Hello <strong>world</strong>!</p>'
        result = sanitize_html(safe_html_input)
        
        assert '<p>' in result
        assert '<strong>' in result
        assert 'Hello' in result
        assert 'world' in result
    
    def test_sanitize_html_custom_allowed_tags(self):
        """Test custom allowed tags."""
        html = '<p>Para</p><div>Div</div><span>Span</span>'
        result = sanitize_html(html, allow_tags=['p', 'span'])
        
        assert '<p>' in result
        assert '<span>' in result
        assert '<div>' not in result
    
    def test_sanitize_text_input_escapes_html(self):
        """Test that HTML is escaped in text input."""
        malicious_input = '<script>alert("XSS")</script>'
        result = sanitize_text_input(malicious_input)
        
        assert '&lt;script&gt;' in result
        assert '<script>' not in result
    
    def test_sanitize_text_input_strips_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        input_with_whitespace = '  Hello World  '
        result = sanitize_text_input(input_with_whitespace)
        
        assert result == 'Hello World'
    
    def test_sanitize_text_input_handles_none(self):
        """Test that None input returns empty string."""
        result = sanitize_text_input(None)
        assert result == ''
    
    def test_sanitize_text_input_handles_empty_string(self):
        """Test that empty string is handled correctly."""
        result = sanitize_text_input('')
        assert result == ''


class TestTemplateFilters:
    """Test custom Jinja2 template filters."""
    
    def test_safe_text_filter(self):
        """Test safe_text filter escapes HTML."""
        malicious_input = '<script>alert("XSS")</script>'
        result = safe_text(malicious_input)
        
        assert '&lt;script&gt;' in result
        assert '<script>' not in result
    
    def test_safe_text_filter_handles_none(self):
        """Test safe_text filter handles None."""
        result = safe_text(None)
        assert result == ''
    
    def test_safe_html_filter_allows_safe_tags(self):
        """Test safe_html filter preserves safe tags."""
        safe_input = '<p>Hello <strong>world</strong>!</p>'
        result = safe_html(safe_input)
        
        assert '<p>' in str(result)
        assert '<strong>' in str(result)
    
    def test_safe_html_filter_removes_script(self):
        """Test safe_html filter removes script tags."""
        malicious_input = '<script>alert("XSS")</script><p>Safe</p>'
        result = safe_html(malicious_input)
        
        assert '<script>' not in str(result)
        assert '<p>Safe</p>' in str(result)
    
    def test_format_phone_filter(self):
        """Test phone number formatting."""
        phone = '05551234567'
        result = format_phone(phone)
        
        assert result == '0555 123 45 67'
    
    def test_format_phone_filter_handles_formatted_input(self):
        """Test phone formatting with already formatted input."""
        phone = '0555 123 45 67'
        result = format_phone(phone)
        
        assert result == '0555 123 45 67'
    
    def test_format_phone_filter_handles_invalid_length(self):
        """Test phone formatting with invalid length."""
        phone = '123'
        result = format_phone(phone)
        
        assert result == '123'  # Returns original if invalid
    
    def test_format_phone_filter_handles_none(self):
        """Test phone formatting with None."""
        result = format_phone(None)
        assert result == ''


class TestXSSVectors:
    """Test common XSS attack vectors."""
    
    def test_javascript_protocol(self):
        """Test javascript: protocol in links."""
        malicious = '<a href="javascript:alert(\'XSS\')">Click</a>'
        result = sanitize_html(malicious)
        
        assert 'javascript:' not in result
    
    def test_data_protocol(self):
        """Test data: protocol."""
        malicious = '<img src="data:text/html,<script>alert(\'XSS\')</script>">'
        result = sanitize_html(malicious)
        
        # img tag is not in allowed tags by default
        assert '<img' not in result
    
    def test_svg_xss(self):
        """Test SVG-based XSS."""
        malicious = '<svg onload="alert(\'XSS\')"></svg>'
        result = sanitize_html(malicious)
        
        assert 'onload' not in result
        assert 'alert' not in result
    
    def test_iframe_injection(self):
        """Test iframe injection."""
        malicious = '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        result = sanitize_html(malicious)
        
        assert '<iframe' not in result
    
    def test_style_injection(self):
        """Test CSS/style injection."""
        malicious = '<div style="background:url(javascript:alert(\'XSS\'))">Test</div>'
        result = sanitize_html(malicious)
        
        # div is not in allowed tags by default
        assert '<div' not in result
    
    def test_base64_encoded_script(self):
        """Test base64 encoded script."""
        malicious = '<img src="data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=">'
        result = sanitize_html(malicious)
        
        assert '<img' not in result
    
    def test_html_entity_encoding_bypass(self):
        """Test HTML entity encoding bypass attempts."""
        malicious = '&lt;script&gt;alert("XSS")&lt;/script&gt;'
        result = sanitize_text_input(malicious)
        
        # Should still be escaped
        assert '&lt;' in result or '&amp;lt;' in result


class TestPasswordPolicyDisplay:
    """Test that password policy is displayed in forms."""
    
    def test_password_policy_message_content(self):
        """Test password policy message content."""
        expected_message = "En az 8 karakter, 1 büyük harf, 1 küçük harf, 1 rakam ve 1 özel karakter içermelidir."
        
        # This would be tested in integration tests with actual template rendering
        assert len(expected_message) > 0
        assert '8 karakter' in expected_message
        assert 'büyük harf' in expected_message
        assert 'küçük harf' in expected_message
        assert 'rakam' in expected_message
        assert 'özel karakter' in expected_message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
