from app.utils.validators import sanitize_html

malicious_html = '<script>alert("XSS")</script><p>Safe content</p>'
result = sanitize_html(malicious_html, allow_tags=['p'])
print('Result:', repr(result))
print('Has script tag:', '<script>' in result)
print('Has alert:', 'alert' in result)
