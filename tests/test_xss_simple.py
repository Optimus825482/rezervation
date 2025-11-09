"""
Simple XSS protection tests without database dependencies.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.validators import sanitize_html, sanitize_text_input


def test_sanitize_html_removes_script_tags():
    """Test that script tags are removed from HTML."""
    malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
    result = sanitize_html(malicious_html, allow_tags=['p'])
    
    # Script tag should be removed (but content might remain as text)
    assert '<script>' not in result
    assert '</script>' not in result
    assert 'Safe content' in result  # Safe content should be preserved
    print("✓ Script tags removed successfully")


def test_sanitize_html_allows_safe_tags():
    """Test that safe HTML tags are preserved."""
    safe_html_input = '<p>Hello <strong>world</strong>!</p>'
    result = sanitize_html(safe_html_input, allow_tags=['p', 'strong'])
    
    assert '<p>' in result
    assert '<strong>' in result
    assert 'Hello' in result
    assert 'world' in result
    print("✓ Safe HTML tags preserved")


def test_sanitize_text_input_escapes_html():
    """Test that HTML is escaped in text input."""
    malicious_input = '<script>alert("XSS")</script>'
    result = sanitize_text_input(malicious_input)
    
    # bleach.clean with tags=[] will remove tags completely
    assert '<script>' not in result
    assert 'alert("XSS")' in result or result == 'alert("XSS")'
    print("✓ Text input sanitized")


def test_sanitize_text_input_strips_whitespace():
    """Test that leading/trailing whitespace is removed."""
    input_with_whitespace = '  Hello World  '
    result = sanitize_text_input(input_with_whitespace)
    
    assert result == 'Hello World'
    print("✓ Whitespace stripped")


def test_javascript_protocol():
    """Test javascript: protocol in links."""
    malicious = '<a href="javascript:alert(\'XSS\')">Click</a>'
    result = sanitize_html(malicious, allow_tags=['a'])
    
    # bleach should remove javascript: protocol
    assert 'javascript:' not in result
    print("✓ JavaScript protocol removed")


def test_iframe_injection():
    """Test iframe injection."""
    malicious = '<iframe src="javascript:alert(\'XSS\')"></iframe>'
    result = sanitize_html(malicious)
    
    assert '<iframe' not in result
    print("✓ Iframe injection blocked")


if __name__ == '__main__':
    print("\n🔒 Running XSS Protection Tests\n")
    print("=" * 50)
    
    try:
        test_sanitize_html_removes_script_tags()
        test_sanitize_html_allows_safe_tags()
        test_sanitize_text_input_escapes_html()
        test_sanitize_text_input_strips_whitespace()
        test_javascript_protocol()
        test_iframe_injection()
        
        print("=" * 50)
        print("\n✅ All XSS protection tests passed!\n")
    except AssertionError as e:
        print(f"\n❌ Test failed!")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
