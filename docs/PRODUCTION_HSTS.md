# HTTP Strict Transport Security (HSTS) Configuration

## Overview

HTTP Strict Transport Security (HSTS) is a web security policy mechanism that helps protect websites against protocol downgrade attacks and cookie hijacking. HSTS instructs web browsers to only interact with the server using secure HTTPS connections, never plain HTTP.

## HSTS Configuration

### Production Settings

HSTS is configured in `app/security_config.py` under `ProductionSecurityConfig`:

```python
# Enable HSTS in production
HSTS_ENABLED = True
HSTS_MAX_AGE = 31536000  # 1 year (in seconds)
HSTS_INCLUDE_SUBDOMAINS = True
HSTS_PRELOAD = False  # Set to True only after testing and submitting to preload list
```

### Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `HSTS_ENABLED` | `True` | Enables HSTS header in production |
| `HSTS_MAX_AGE` | `31536000` | Time (in seconds) browser should remember to only use HTTPS (1 year) |
| `HSTS_INCLUDE_SUBDOMAINS` | `True` | Apply HSTS to all subdomains |
| `HSTS_PRELOAD` | `False` | Enable HSTS preloading (requires submission to browser preload list) |

### Development Settings

HSTS is **disabled** in development to allow HTTP access:

```python
class DevelopmentSecurityConfig(SecurityConfig):
    # No HSTS in development
    HSTS_ENABLED = False
```

## How HSTS Works

### 1. Server Response

When a browser visits your site over HTTPS, the server includes the HSTS header:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 2. Browser Behavior

After receiving the HSTS header, the browser:
1. **Automatically upgrades** all HTTP requests to HTTPS
2. **Prevents** users from bypassing certificate warnings
3. **Remembers** this policy for the duration of `max-age`

### 3. Example Flow

```
User types: http://example.com
             ↓
Browser remembers HSTS policy
             ↓
Browser automatically changes to: https://example.com
             ↓
Secure connection established
```

## HSTS Header Format

### Basic Header

```
Strict-Transport-Security: max-age=31536000
```

### With Subdomains

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### With Preload

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

## HSTS Implementation

### Middleware Integration

HSTS is automatically added via security headers middleware in `app/__init__.py`:

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    headers = SecurityConfig.get_security_headers(is_production=is_production)
    
    # HSTS is included in production headers
    for header_name, header_value in headers.items():
        response.headers[header_name] = header_value
    
    return response
```

### Security Config Method

The HSTS header is built dynamically in `app/security_config.py`:

```python
@classmethod
def get_hsts_header(cls) -> str:
    """Build HSTS header"""
    parts = [f'max-age={cls.HSTS_MAX_AGE}']
    if cls.HSTS_INCLUDE_SUBDOMAINS:
        parts.append('includeSubDomains')
    if cls.HSTS_PRELOAD:
        parts.append('preload')
    return '; '.join(parts)
```

## Environment Variables

Configure HSTS behavior with environment variables:

```bash
# .env file
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000          # 1 year
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=false             # Set to true only after testing
```

### Environment Variable Priority

1. **Production:** Uses `ProductionSecurityConfig` (HSTS enabled by default)
2. **Development:** Uses `DevelopmentSecurityConfig` (HSTS disabled)
3. **Override:** Environment variables can override defaults

## Testing HSTS

### 1. Verify HSTS Header

**Using curl:**
```bash
curl -I https://your-domain.com | grep Strict-Transport-Security
```

Expected output:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

**Using browser DevTools:**
1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Click on the main document request
5. Check Response Headers for `Strict-Transport-Security`

### 2. Test Browser Behavior

1. Visit site over HTTPS: `https://your-domain.com`
2. HSTS header is received
3. Try to visit HTTP version: `http://your-domain.com`
4. Browser should automatically redirect to HTTPS

### 3. Online Testing Tools

**SSL Labs:**
- URL: https://www.ssllabs.com/ssltest/
- Comprehensive SSL/TLS and HSTS testing
- Provides detailed security report

**HSTS Preload Check:**
- URL: https://hstspreload.org/
- Check if your site is preload-ready
- Verify HSTS configuration

### 4. Test HSTS in Development

To test HSTS in development environment:

```python
# In app/security_config.py - temporarily for testing
class DevelopmentSecurityConfig(SecurityConfig):
    # Enable HSTS for testing (requires HTTPS in dev)
    HSTS_ENABLED = True
    HSTS_MAX_AGE = 300  # Short duration for testing (5 minutes)
```

**Note:** You'll need HTTPS in development (e.g., using ngrok or self-signed certificate).

## HSTS Best Practices

### 1. Start with Short max-age

When first deploying HSTS, start with a short duration:

```python
HSTS_MAX_AGE = 300  # 5 minutes for initial testing
```

After confirming everything works:

```python
HSTS_MAX_AGE = 2592000  # 30 days
```

Finally, increase to recommended duration:

```python
HSTS_MAX_AGE = 31536000  # 1 year
```

### 2. Gradual Rollout Checklist

- [ ] **Week 1:** Deploy with `max-age=300` (5 minutes)
- [ ] **Week 2:** Monitor logs, increase to `max-age=86400` (1 day)
- [ ] **Week 3:** Increase to `max-age=604800` (1 week)
- [ ] **Week 4:** Increase to `max-age=2592000` (30 days)
- [ ] **Month 2:** Increase to `max-age=31536000` (1 year)
- [ ] **Month 3:** Consider enabling `preload`

### 3. includeSubDomains Considerations

Before enabling `includeSubDomains`:

1. **Audit all subdomains:**
   ```bash
   # List all DNS records
   dig ANY your-domain.com
   ```

2. **Ensure all subdomains support HTTPS:**
   - ✅ api.your-domain.com - has SSL certificate
   - ✅ www.your-domain.com - has SSL certificate
   - ❌ staging.your-domain.com - no SSL certificate → Fix before enabling

3. **Test each subdomain:**
   ```bash
   curl -I https://api.your-domain.com
   curl -I https://www.your-domain.com
   ```

### 4. Preload Considerations

**Before enabling HSTS preload:**

⚠️ **Warning:** HSTS preload is **permanent** and **irreversible**. Removal can take months.

**Requirements for preload:**
1. Valid SSL certificate
2. HTTPS on all subdomains
3. `max-age` of at least **31536000** (1 year)
4. `includeSubDomains` directive enabled
5. HTTPS redirect from HTTP on same host

**Preload submission:**
1. Verify all requirements at https://hstspreload.org/
2. Submit your domain
3. Wait for inclusion in browser preload lists (can take months)

**Only enable preload if:**
- You're 100% certain you'll always support HTTPS
- All current and future subdomains will support HTTPS
- You understand the long-term commitment

## Troubleshooting

### Issue: HSTS Header Not Appearing

**Check 1: Verify production environment**
```python
# In your application
import os
print(f"ENV: {os.getenv('FLASK_ENV')}")  # Should be 'production'
```

**Check 2: Verify HSTS is enabled in config**
```python
# In app/security_config.py
print(f"HSTS_ENABLED: {ProductionSecurityConfig.HSTS_ENABLED}")  # Should be True
```

**Check 3: Verify HTTPS connection**
HSTS header should only be sent over HTTPS. If testing over HTTP, HSTS won't appear.

### Issue: HSTS Blocking Development Access

**Problem:** After visiting production site, can't access development site over HTTP.

**Solution 1: Clear HSTS settings in browser**

**Chrome:**
1. Visit `chrome://net-internals/#hsts`
2. Enter your domain in "Delete domain security policies"
3. Click "Delete"

**Firefox:**
1. Close Firefox
2. Find profile folder (visit `about:support` → "Profile Folder")
3. Delete `SiteSecurityServiceState.txt`
4. Restart Firefox

**Solution 2: Use different domain for development**
- Production: `https://example.com`
- Development: `http://dev.example.com` or `http://localhost:5000`

### Issue: Certificate Warnings Can't Be Bypassed

**Problem:** Users can't bypass SSL certificate warnings after HSTS is enabled.

**Why:** This is intentional HSTS behavior for security.

**Solution:** Ensure valid SSL certificate is installed:
```bash
# Check certificate validity
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Verify certificate expiration
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

### Issue: Subdomain Not Accessible

**Problem:** Subdomain blocked after enabling `includeSubDomains`.

**Check:** Does subdomain have valid SSL certificate?
```bash
curl -I https://subdomain.your-domain.com
```

**Solution:** 
1. Add SSL certificate to subdomain
2. OR temporarily disable `includeSubDomains` in config:
```python
HSTS_INCLUDE_SUBDOMAINS = False
```

## Monitoring HSTS

### 1. Log HSTS Header Delivery

Monitor that HSTS headers are being sent:

```python
# In app/__init__.py
@app.after_request
def add_security_headers(response):
    headers = SecurityConfig.get_security_headers(is_production=is_production)
    
    # Log HSTS header in production
    if is_production and 'Strict-Transport-Security' in headers:
        app.logger.info(f"HSTS header sent: {headers['Strict-Transport-Security']}")
    
    for header_name, header_value in headers.items():
        response.headers[header_name] = header_value
    
    return response
```

### 2. Monitor HTTP Requests

Monitor and alert on HTTP requests in production (should be rare after HSTS):

```bash
# Analyze access logs for HTTP requests
grep "^[^:]*:80 " /var/log/nginx/access.log | wc -l

# Alert if HTTP requests exceed threshold
if [ $(grep "^[^:]*:80 " /var/log/nginx/access.log | wc -l) -gt 100 ]; then
  echo "Alert: High number of HTTP requests detected"
fi
```

### 3. SSL Certificate Monitoring

Monitor SSL certificate expiration (critical for HSTS sites):

```bash
#!/bin/bash
# Check certificate expiration

DOMAIN="your-domain.com"
EXPIRY_DATE=$(echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)

EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
NOW_EPOCH=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
  echo "Alert: SSL certificate expires in $DAYS_UNTIL_EXPIRY days"
fi
```

## Integration with Other Security Features

### HSTS + HTTPS Redirect

Ensure HTTP to HTTPS redirect is configured in web server:

**Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Flask application
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

**Apache:**
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # Flask application
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    RequestHeader set X-Forwarded-Proto "https"
</VirtualHost>
```

### HSTS + Secure Cookies

HSTS works with secure cookies configured in `config.py`:

```python
class ProductionConfig(Config):
    # HSTS ensures these are transmitted over HTTPS only
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### HSTS + CSP

HSTS and Content Security Policy work together:

```python
# Both configured in security_config.py
class ProductionSecurityConfig(SecurityConfig):
    # HSTS prevents HTTP connections
    HSTS_ENABLED = True
    
    # CSP upgrade-insecure-requests helps transition
    CSP_UPGRADE_INSECURE_REQUESTS = True  # Optional
```

## Security Benefits

### 1. Prevents Protocol Downgrade Attacks

**Without HSTS:**
```
Attacker intercepts HTTP request → Serves malicious content over HTTP
```

**With HSTS:**
```
Browser enforces HTTPS → Attacker can't downgrade to HTTP
```

### 2. Prevents Cookie Hijacking

**Without HSTS:**
```
User visits http://site.com → Session cookie sent over HTTP → Attacker steals cookie
```

**With HSTS:**
```
Browser auto-upgrades to HTTPS → Cookie only sent over encrypted connection
```

### 3. Prevents SSL Stripping Attacks

**Without HSTS:**
```
Attacker strips HTTPS → User connects over HTTP → Credentials stolen
```

**With HSTS:**
```
Browser remembers HSTS policy → Always uses HTTPS → Attack fails
```

## Compliance and Standards

### OWASP Recommendations

OWASP recommends HSTS with:
- Minimum `max-age` of **31536000** seconds (1 year)
- `includeSubDomains` directive enabled
- Consider HSTS preloading for high-security sites

### PCI DSS Compliance

PCI DSS requires:
- HTTPS for all cardholder data transmission
- HSTS helps enforce this requirement
- Recommended for PCI DSS compliance

### GDPR Compliance

HSTS supports GDPR by:
- Ensuring encrypted data transmission
- Protecting user privacy
- Preventing data interception

## References

- [RFC 6797 - HTTP Strict Transport Security](https://tools.ietf.org/html/rfc6797)
- [OWASP HSTS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Strict_Transport_Security_Cheat_Sheet.html)
- [MDN Web Docs - HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
- [HSTS Preload List](https://hstspreload.org/)
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)

## Support

For HSTS-related issues:
1. Check browser DevTools Network tab for HSTS header
2. Verify SSL certificate validity
3. Review this documentation
4. Clear HSTS settings in browser if needed (see Troubleshooting)
5. Contact security team for production issues
