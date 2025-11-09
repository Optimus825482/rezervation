# Production Content Security Policy (CSP) Configuration

## Overview

This document describes the Content Security Policy configuration for production environments. The production CSP is significantly stricter than development, removing `unsafe-inline` and `unsafe-eval` directives and using nonce-based approach for inline scripts and styles.

## Production CSP Policy

### Directive Configuration

The production CSP is configured in `app/security_config.py` under `ProductionSecurityConfig`:

```python
CSP_SCRIPT_SRC = "'self' https://cdn.jsdelivr.net https://code.jquery.com"
CSP_STYLE_SRC = "'self' https://cdn.jsdelivr.net https://fonts.googleapis.com"
CSP_IMG_SRC = "'self' data:"
```

### Key Differences from Development

| Directive | Development | Production |
|-----------|-------------|------------|
| `script-src` | `'self' 'unsafe-inline' 'unsafe-eval' ...` | `'self' ...` (no unsafe directives) |
| `style-src` | `'self' 'unsafe-inline' ...` | `'self' ...` (no unsafe directives) |
| `img-src` | `'self' data: blob:` | `'self' data:` (blob removed) |

## Nonce-Based CSP

### What is a Nonce?

A nonce (number used once) is a cryptographically secure random value that is:
- Generated for each HTTP request
- Included in the CSP header
- Added to inline `<script>` and `<style>` tags

This allows inline scripts/styles to execute while blocking all other inline code.

### How Nonce Works

1. **Nonce Generation** (`app/__init__.py`):
```python
@app.before_request
def generate_csp_nonce():
    """Generate CSP nonce for each request"""
    from flask import g
    import secrets
    g.csp_nonce = secrets.token_urlsafe(16)
```

2. **CSP Header with Nonce** (`app/security_config.py`):
```python
@classmethod
def get_csp_header_with_nonce(cls, nonce: str) -> str:
    return (
        f"default-src {cls.CSP_DEFAULT_SRC}; "
        f"script-src {cls.CSP_SCRIPT_SRC} 'nonce-{nonce}'; "
        f"style-src {cls.CSP_STYLE_SRC} 'nonce-{nonce}'; "
        # ... other directives
    )
```

3. **Template Usage** (`app/templates/base.html`):
```html
<style{% if g.csp_nonce %} nonce="{{ g.csp_nonce }}"{% endif %}>
    body { background-color: #f5f5f5; }
</style>

<script{% if g.csp_nonce %} nonce="{{ g.csp_nonce }}"{% endif %}>
    // Your inline JavaScript
</script>
```

### Adding Nonce to Templates

For any inline `<script>` or `<style>` tag in your templates:

**Before (Development):**
```html
<style>
    .my-class { color: red; }
</style>

<script>
    console.log('Hello');
</script>
```

**After (Production-Ready):**
```html
<style{% if g.csp_nonce %} nonce="{{ g.csp_nonce }}"{% endif %}>
    .my-class { color: red; }
</style>

<script{% if g.csp_nonce %} nonce="{{ g.csp_nonce }}"{% endif %}>
    console.log('Hello');
</script>
```

The `{% if g.csp_nonce %}` check ensures backward compatibility with development environment.

## Allowed External Sources

### Scripts
- `'self'` - Same origin scripts
- `https://cdn.jsdelivr.net` - Bootstrap, Font Awesome
- `https://code.jquery.com` - jQuery library

### Styles
- `'self'` - Same origin stylesheets
- `https://cdn.jsdelivr.net` - Bootstrap, Font Awesome
- `https://fonts.googleapis.com` - Google Fonts CSS

### Fonts
- `'self'` - Same origin fonts
- `https://fonts.gstatic.com` - Google Fonts
- `https://cdn.jsdelivr.net` - Font Awesome fonts

### Images
- `'self'` - Same origin images
- `data:` - Data URIs (for inline images, QR codes)

## CSP Violation Reporting

### Report Endpoint

All CSP violations are reported to `/security/csp-report`:

```python
CSP_REPORT_URI = "/security/csp-report"
```

### Violation Handling

Violations are logged to:
- `logs/security.log` - Human-readable log
- `logs/security_events.json` - Structured JSON events

Example violation log:
```json
{
    "timestamp": "2024-01-15T10:30:45.123456",
    "event_type": "csp_violation",
    "violation": {
        "blocked-uri": "https://malicious-site.com/script.js",
        "violated-directive": "script-src",
        "document-uri": "https://example.com/page"
    }
}
```

## Testing CSP in Production

### 1. Browser Developer Tools

**Chrome DevTools:**
1. Open DevTools (F12)
2. Go to Console tab
3. Look for CSP violation messages:
   ```
   Refused to execute inline script because it violates the following Content Security Policy directive: "script-src 'self' ..."
   ```

**Firefox Developer Tools:**
1. Open Developer Tools (F12)
2. Go to Console tab
3. CSP violations appear as warnings with detailed information

### 2. Report-Only Mode (Testing)

For testing CSP before enforcement, use `Content-Security-Policy-Report-Only` header:

```python
# In app/security_config.py (temporary for testing)
headers['Content-Security-Policy-Report-Only'] = cls.get_csp_header_with_nonce(nonce)
```

This logs violations without blocking resources, allowing you to identify issues before enforcing the policy.

### 3. Common Issues and Fixes

**Issue: Inline scripts blocked**
```
Refused to execute inline script because it violates CSP
```
**Fix:** Add nonce attribute to script tag:
```html
<script nonce="{{ g.csp_nonce }}">...</script>
```

**Issue: External script blocked**
```
Refused to load script from 'https://example.com/script.js'
```
**Fix:** Add domain to `CSP_SCRIPT_SRC` in `security_config.py`:
```python
CSP_SCRIPT_SRC = "'self' https://cdn.jsdelivr.net https://example.com"
```

**Issue: Inline styles blocked**
```
Refused to apply inline style because it violates CSP
```
**Fix:** Add nonce attribute to style tag:
```html
<style nonce="{{ g.csp_nonce }}">...</style>
```

## Monitoring and Alerts

### CSP Violation Monitoring

Monitor `logs/security_events.json` for CSP violations:

```bash
# Watch for CSP violations in real-time
tail -f logs/security_events.json | grep csp_violation

# Count violations by blocked URI
grep csp_violation logs/security_events.json | \
  jq -r '.violation["blocked-uri"]' | \
  sort | uniq -c | sort -nr
```

### Setting Up Alerts

**Example: Alert on excessive CSP violations**

```bash
#!/bin/bash
# Alert if more than 10 CSP violations in last hour

violations=$(grep csp_violation logs/security_events.json | \
  jq -r 'select(.timestamp > (now - 3600)) | .timestamp' | \
  wc -l)

if [ "$violations" -gt 10 ]; then
  echo "Alert: $violations CSP violations in last hour" | \
    mail -s "CSP Violation Alert" admin@example.com
fi
```

## Best Practices

### 1. Minimize Inline Scripts/Styles

**Bad:**
```html
<button onclick="doSomething()">Click</button>
<div style="color: red;">Text</div>
```

**Good:**
```html
<!-- External JavaScript -->
<button id="myButton">Click</button>
<script src="/static/js/app.js"></script>

<!-- External CSS -->
<div class="text-red">Text</div>
<link rel="stylesheet" href="/static/css/app.css">
```

### 2. Use External Resources from Trusted CDNs

Only include CDNs in CSP that you trust:
- ✅ cdn.jsdelivr.net (verified CDN)
- ✅ fonts.googleapis.com (Google Fonts)
- ❌ unknown-cdn.com (unverified)

### 3. Avoid 'unsafe-eval'

Never use `'unsafe-eval'` in production. If you need dynamic code evaluation:

**Bad:**
```javascript
eval(userInput); // Blocked by CSP and dangerous
```

**Good:**
```javascript
// Use JSON parsing instead
const data = JSON.parse(userInput);
```

### 4. Regular CSP Audits

1. Review `logs/security_events.json` weekly for violations
2. Investigate unexpected violations
3. Update CSP policy if legitimate resources are blocked
4. Remove unused domains from whitelist

## Environment Variables

Configure CSP behavior with environment variables:

```bash
# Enable/disable specific CSP features
CSP_REPORT_ONLY=false  # Set to true for testing
CSP_ENABLE_NONCE=true  # Enable nonce-based CSP

# Custom report endpoint (optional)
CSP_REPORT_URI=/custom-csp-report
```

## Troubleshooting

### CSP Not Applied

**Check 1:** Verify production environment
```python
# In app/__init__.py
config_name = app.config.get('ENV', 'development')
print(f"Environment: {config_name}")  # Should be 'production'
```

**Check 2:** Verify headers in response
```bash
curl -I https://your-domain.com | grep Content-Security-Policy
```

### Nonce Not Generated

**Check 1:** Verify `before_request` hook is registered
```python
# In app/__init__.py - should be present
@app.before_request
def generate_csp_nonce():
    ...
```

**Check 2:** Verify nonce in template context
```html
<!-- Add to template for debugging -->
<!-- CSP Nonce: {{ g.csp_nonce }} -->
```

### External Resource Blocked

**Step 1:** Check browser console for exact violation
**Step 2:** Add domain to appropriate CSP directive in `security_config.py`
**Step 3:** Restart application and verify

## Migration from Development to Production

### Checklist

- [ ] All inline scripts have nonce attribute
- [ ] All inline styles have nonce attribute
- [ ] Event handlers moved from HTML to JavaScript files
- [ ] Style attributes moved to CSS classes
- [ ] CSP tested with Report-Only mode
- [ ] No violations in test environment
- [ ] Monitoring set up for CSP violations
- [ ] Team trained on CSP requirements

### Migration Script

```bash
# Step 1: Find inline scripts/styles without nonce
grep -r "<script>" app/templates/ | grep -v "nonce="
grep -r "<style>" app/templates/ | grep -v "nonce="

# Step 2: Find inline event handlers
grep -r "onclick=" app/templates/
grep -r "onload=" app/templates/

# Step 3: Find inline styles
grep -r "style=" app/templates/
```

## References

- [MDN Web Docs - Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/) - Test your CSP
- [Content Security Policy Reference](https://content-security-policy.com/)
- [OWASP CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

## Support

For CSP-related issues:
1. Check CSP violation logs: `logs/security_events.json`
2. Review this documentation
3. Test with CSP Report-Only mode
4. Contact security team if violations persist
