# Rate Limiting Documentation

## Overview

This document describes the rate limiting implementation using Flask-Limiter to protect sensitive endpoints from brute force attacks and abuse.

## Configuration

### Default Limits

All endpoints have default rate limits configured in `app/__init__.py`:

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

- **200 requests per day** per IP address
- **50 requests per hour** per IP address

### Storage Backend

- **Development/Testing**: In-memory storage (automatic)
- **Production**: Redis recommended (configure `RATELIMIT_STORAGE_URL` in environment)

```bash
# Production configuration
export RATELIMIT_STORAGE_URL=redis://localhost:6379/1
```

## Endpoint-Specific Limits

### Authentication Endpoints

#### Login (`/login`)
```python
@limiter.limit("5 per minute")
```

- **Limit**: 5 attempts per minute
- **Purpose**: Prevent brute force password attacks
- **Reset**: Every 60 seconds

**Recommendation**: Monitor failed login attempts and implement account lockout after multiple failures.

#### Initial Setup (`/setup`)
```python
@limiter.limit("10 per hour")
```

- **Limit**: 10 attempts per hour
- **Purpose**: Prevent repeated setup attempts
- **Reset**: Every 3600 seconds (1 hour)

### Check-in Endpoints

#### QR Code Scan (`/checkin/scan`)
```python
@limiter.limit("30 per minute")
```

- **Limit**: 30 scans per minute
- **Purpose**: Prevent QR code scanning abuse
- **Reset**: Every 60 seconds

**Note**: This allows legitimate high-volume check-in scenarios while preventing abuse.

### Security Endpoints

#### CSP Violation Report (`/security/csp-report`)
```python
@limiter.limit("100 per hour")
```

- **Limit**: 100 reports per hour
- **Purpose**: Prevent CSP report flooding
- **Reset**: Every 3600 seconds (1 hour)

## Rate Limit Responses

### HTTP 429 - Too Many Requests

When rate limit is exceeded:

```json
{
    "error": "ratelimit exceeded",
    "message": "Too many requests"
}
```

**Headers Included**:
- `Retry-After`: Seconds until rate limit resets
- `X-RateLimit-Limit`: The rate limit ceiling
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

### Example Response

```http
HTTP/1.1 429 TOO MANY REQUESTS
Content-Type: application/json
Retry-After: 45
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699545678

{
    "error": "ratelimit exceeded"
}
```

## Testing

### Running Rate Limiting Tests

```bash
# Run all rate limiting tests
pytest tests/test_rate_limiting.py -v

# Run specific test class
pytest tests/test_rate_limiting.py::TestLoginRateLimit -v

# Run with coverage
pytest tests/test_rate_limiting.py --cov=app --cov-report=html
```

### Test Results

✅ **11/11 tests passing**:
- Configuration tests: 2/2
- Login endpoint tests: 1/1
- Setup endpoint tests: 1/1
- Check-in endpoint tests: 1/1
- CSP report tests: 2/2
- Storage tests: 2/2
- Documentation tests: 2/2

## Custom Rate Limits

### Adding Rate Limiting to New Endpoints

1. **Import limiter**:
```python
from app import limiter
```

2. **Apply decorator**:
```python
@bp.route('/api/sensitive-action', methods=['POST'])
@limiter.limit("10 per minute")
def sensitive_action():
    # Your code here
    pass
```

### Dynamic Rate Limits

For user-specific or role-based limits:

```python
def get_user_limit():
    if current_user.is_admin:
        return "1000 per hour"
    return "100 per hour"

@bp.route('/api/action')
@limiter.limit(get_user_limit)
def action():
    pass
```

## Best Practices

### DO ✅

1. **Use strict limits on auth endpoints**
   ```python
   @limiter.limit("5 per minute")  # Login
   @limiter.limit("3 per minute")  # Password reset
   ```

2. **Monitor rate limit violations**
   - Log 429 responses
   - Alert on suspicious patterns
   - Track repeat offenders

3. **Use Redis in production**
   ```python
   RATELIMIT_STORAGE_URL = "redis://localhost:6379/1"
   ```

4. **Set appropriate limits for each endpoint**
   - Consider legitimate use cases
   - Balance security and usability
   - Test with realistic traffic

5. **Include Retry-After headers**
   - Helps well-behaved clients
   - Reduces unnecessary retries

### DON'T ❌

1. **Don't use same limits for all endpoints**
   ```python
   # Bad: Same limit for login and public API
   @limiter.limit("50 per hour")  # Too lenient for auth
   ```

2. **Don't skip rate limiting in production**
   ```python
   # Bad: Disabling in production
   if not app.config['TESTING']:
       limiter.enabled = False  # NEVER DO THIS
   ```

3. **Don't use in-memory storage in production**
   ```python
   # Bad: Won't work with multiple workers
   # Use Redis or Memcached instead
   ```

4. **Don't set limits too low**
   ```python
   # Bad: May affect legitimate users
   @limiter.limit("1 per hour")  # Too strict
   ```

5. **Don't ignore rate limit errors**
   - Monitor 429 responses
   - Investigate patterns
   - Adjust limits as needed

## Environment Configuration

### Development

```python
# config.py - DevelopmentConfig
RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URL = None  # Uses in-memory
```

### Production

```python
# config.py - ProductionConfig
RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
RATELIMIT_HEADERS_ENABLED = True
```

## Monitoring

### Log Rate Limit Violations

```python
from flask import request
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(
        f"Rate limit exceeded: {request.remote_addr} - {request.path}"
    )
    return jsonify({
        "error": "ratelimit exceeded",
        "message": str(e.description)
    }), 429
```

### Metrics to Track

1. **Rate limit hits per endpoint**
   - Which endpoints are being rate limited
   - Frequency of violations

2. **IP addresses triggering limits**
   - Identify potential attackers
   - Consider IP blocking for repeat offenders

3. **Time patterns**
   - Peak times for rate limiting
   - Coordinated attack patterns

4. **False positives**
   - Legitimate users being rate limited
   - Adjust limits if needed

## Troubleshooting

### Issue: Rate Limits Not Working

**Cause**: Limiter not initialized or disabled

**Solution**:
```python
# Check limiter status
from app import limiter
print(limiter.enabled)  # Should be True
print(limiter._storage)  # Should not be None
```

### Issue: Rate Limits Too Strict

**Cause**: Limits set too low for legitimate traffic

**Solution**:
```python
# Adjust limits based on monitoring
@limiter.limit("10 per minute")  # Increase from 5
```

### Issue: Rate Limits Not Reset

**Cause**: Storage backend issue or time drift

**Solution**:
```bash
# Check Redis connection
redis-cli ping

# Check server time
date
```

### Issue: Multiple Workers Reset Counts

**Cause**: Using in-memory storage with multiple workers

**Solution**:
```python
# Use Redis for production
RATELIMIT_STORAGE_URL = "redis://localhost:6379/1"
```

## Security Considerations

1. **Brute Force Protection**
   - Login: 5 attempts/minute
   - Password reset: 3 attempts/minute
   - Account lockout after 10 failed attempts

2. **DDoS Mitigation**
   - Default limits prevent simple attacks
   - Use CDN/WAF for advanced protection
   - Consider IP-based blocking

3. **Resource Protection**
   - Prevent database overload
   - Protect expensive operations
   - Rate limit file uploads

4. **Privacy**
   - Don't log sensitive data in rate limit events
   - Use hashed IPs for storage if needed
   - Comply with data retention policies

## Future Enhancements

1. **User-based rate limiting**
   - Different limits for different user roles
   - Authenticated vs anonymous users

2. **Adaptive rate limiting**
   - Adjust limits based on traffic patterns
   - Machine learning for anomaly detection

3. **Distributed rate limiting**
   - Cross-service coordination
   - Shared rate limit pools

4. **Custom error pages**
   - User-friendly 429 error pages
   - Retry suggestions
   - Contact support options

## References

- [Flask-Limiter Documentation](https://flask-limiter.readthedocs.io/)
- [OWASP Rate Limiting Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Rate_Limiting_Cheat_Sheet.html)
- [RFC 6585 - HTTP 429 Status Code](https://tools.ietf.org/html/rfc6585)
