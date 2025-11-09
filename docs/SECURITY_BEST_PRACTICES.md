# Security Best Practices Guide

## 📋 İçindekiler
1. [Giriş](#giriş)
2. [Input Validation](#input-validation)
3. [Password Security](#password-security)
4. [XSS Protection](#xss-protection)
5. [CSRF Protection](#csrf-protection)
6. [SQL Injection Prevention](#sql-injection-prevention)
7. [Security Headers](#security-headers)
8. [Session Security](#session-security)
9. [Development vs Production](#development-vs-production)
10. [Security Checklist](#security-checklist)

---

## Giriş

Bu rehber, rezervasyon sisteminde uygulanan güvenlik önlemlerini ve geliştiricilerin takip etmesi gereken en iyi uygulamaları açıklar.

### Güvenlik Katmanları

Sistem, çok katmanlı güvenlik yaklaşımı kullanır:

```
┌─────────────────────────────────────┐
│  1. Security Headers (CSP, HSTS)    │
├─────────────────────────────────────┤
│  2. Input Validation (Schemas)      │
├─────────────────────────────────────┤
│  3. XSS Sanitization (bleach)       │
├─────────────────────────────────────┤
│  4. CSRF Protection (Flask)         │
├─────────────────────────────────────┤
│  5. SQL Injection (SQLAlchemy ORM)  │
├─────────────────────────────────────┤
│  6. Authentication & Authorization  │
└─────────────────────────────────────┘
```

---

## Input Validation

### ✅ DO: Schema Kullanımı

**Her zaman** Marshmallow schema kullanarak kullanıcı girdilerini validate edin:

```python
from marshmallow import ValidationError
from app.schemas.user_schema import UserSchema

@bp.route('/users/create', methods=['POST'])
def create_user():
    schema = UserSchema()
    
    try:
        # Validate and sanitize input
        validated_data = schema.load({
            'email': request.form.get('email'),
            'name': request.form.get('name'),
            'phone': request.form.get('phone')
        })
        
        # Use validated data
        user = User(**validated_data)
        db.session.add(user)
        db.session.commit()
        
    except ValidationError as e:
        # Handle validation errors
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
```

### ❌ DON'T: Doğrudan Form Verisi Kullanımı

```python
# YANLIŞ - Asla böyle yapmayın!
@bp.route('/users/create', methods=['POST'])
def create_user():
    user = User(
        email=request.form.get('email'),  # ⚠️ Validate edilmemiş!
        name=request.form.get('name'),    # ⚠️ XSS riski!
        phone=request.form.get('phone')   # ⚠️ Format kontrolü yok!
    )
    db.session.add(user)
    db.session.commit()
```

### Schema Oluşturma Kuralları

1. **BaseSchema'dan türet:**
```python
from app.schemas import BaseSchema

class MySchema(BaseSchema):
    """Her schema BaseSchema'dan türemeli"""
    pass
```

2. **Custom validators kullan:**
```python
from marshmallow import validates, ValidationError

class UserSchema(BaseSchema):
    name = fields.Str(required=True)
    
    @validates('name')
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError('İsim boş olamaz')
        if len(value) > 100:
            raise ValidationError('İsim çok uzun')
```

3. **Telefon numarası validasyonu:**
```python
from app.schemas import BaseSchema

class MySchema(BaseSchema):
    phone = fields.Str(required=True)
    # BaseSchema otomatik olarak Türk telefon numarası validate eder
```

---

## Password Security

### Şifre Politikası

Sistem aşağıdaki şifre gereksinimlerini zorunlu kılar:

- ✅ Minimum 8 karakter
- ✅ En az 1 büyük harf (A-Z)
- ✅ En az 1 küçük harf (a-z)
- ✅ En az 1 rakam (0-9)
- ✅ En az 1 özel karakter (!@#$%^&*()_+-=[]{}|;:,.<>?)

### ✅ DO: validate_password_strength Kullanımı

```python
from app.utils.validators import validate_password_strength

def set_user_password(user, password):
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        raise ValueError(message)
    
    # Set password (hashes automatically)
    user.set_password(password)
```

### ✅ DO: User.set_password() Kullanımı

```python
# Model otomatik olarak şifreyi hash'ler
user = User(username='john', email='john@example.com')
user.set_password('SecurePass123!')  # ✅ Otomatik hash + validation
db.session.add(user)
```

### ❌ DON'T: Plain Text Password

```python
# YANLIŞ - Asla plain text şifre saklamayın!
user.password = 'mypassword'  # ⚠️ Hash'lenmemiş!
user.password_hash = 'mypassword'  # ⚠️ Yanlış!
```

### Password Değiştirme

```python
# Current password check + new password validation
if user.check_password(current_password):
    is_valid, message = validate_password_strength(new_password)
    if is_valid:
        user.set_password(new_password)
        db.session.commit()
```

---

## XSS Protection

### Template'lerde Otomatik Escaping

Jinja2 otomatik escaping kullanır, ancak ek koruma için custom filter'lar kullanın:

```html
<!-- ✅ DOĞRU: safe_text filter kullanımı -->
<td>{{ user.name | safe_text }}</td>
<td>{{ user.email | safe_text }}</td>

<!-- ✅ DOĞRU: Telefon formatı -->
<td>{{ reservation.phone | format_phone }}</td>

<!-- ❌ YANLIŞ: safe filter kullanımı -->
<td>{{ user.name | safe }}</td>  <!-- XSS riski! -->
```

### HTML İçerik İzni

Eğer HTML içeriğe izin vermeniz gerekiyorsa, `safe_html` filter kullanın:

```html
<!-- ✅ DOĞRU: Güvenli HTML taglarına izin ver -->
<div>{{ description | safe_html }}</div>
<!-- Sadece p, br, strong, em, u taglarına izin verir -->

<!-- ❌ YANLIŞ: Tüm HTML'e izin ver -->
<div>{{ description | safe }}</div>
```

### Backend'de Sanitization

```python
from app.utils.validators import sanitize_text_input, sanitize_html

# Text input temizleme
clean_text = sanitize_text_input(user_input)

# HTML içerik temizleme (güvenli taglara izin ver)
clean_html = sanitize_html(user_html)
```

### İzin Verilen HTML Tagları

```python
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u']
ALLOWED_ATTRIBUTES = {}  # Hiçbir attribute'a izin verilmez
```

---

## CSRF Protection

Flask-WTF otomatik CSRF koruması sağlar.

### ✅ DO: CSRF Token Kullanımı

```html
<form method="POST">
    {{ form.hidden_tag() }}  <!-- ✅ CSRF token -->
    {{ form.username }}
    <button type="submit">Gönder</button>
</form>
```

### AJAX İstekleri

```javascript
// CSRF token'ı meta tag'den al
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(data)
});
```

---

## SQL Injection Prevention

### ✅ DO: SQLAlchemy ORM Kullanımı

```python
# ✅ DOĞRU: ORM kullanımı (otomatik parameterization)
user = User.query.filter_by(username=username).first()
events = Event.query.filter(Event.company_id == company_id).all()
```

### ✅ DO: Parameterized Queries

```python
# ✅ DOĞRU: Parameterized query
result = db.session.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": username}
)
```

### ❌ DON'T: String Concatenation

```python
# YANLIŞ - SQL Injection riski!
query = f"SELECT * FROM users WHERE username = '{username}'"  # ⚠️
db.session.execute(query)

# YANLIŞ - String formatting
query = "SELECT * FROM users WHERE id = %s" % user_id  # ⚠️
```

---

## Security Headers

### Otomatik Header Ekleme

Tüm response'lara otomatik olarak güvenlik header'ları eklenir:

```python
# app/__init__.py içinde otomatik eklenir
@app.after_request
def add_security_headers(response):
    headers = SecurityConfig.get_security_headers(is_production)
    for header_name, header_value in headers.items():
        response.headers[header_name] = header_value
    return response
```

### Content Security Policy (CSP)

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://cdn.jsdelivr.net;
  style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;
  img-src 'self' data: blob:;
  report-uri /security/csp-report
```

### CSP İhlal Raporlama

CSP ihlalleri `/security/csp-report` endpoint'ine loglanır:

```python
# Otomatik loglama
@bp.route('/security/csp-report', methods=['POST'])
def csp_report():
    # CSP violations are logged automatically
    pass
```

---

## Session Security

### Session Yapılandırması

```python
# config.py
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  # ✅ Environment variable
    SESSION_COOKIE_SECURE = True               # ✅ HTTPS only
    SESSION_COOKIE_HTTPONLY = True             # ✅ JavaScript erişimini engelle
    SESSION_COOKIE_SAMESITE = 'Lax'            # ✅ CSRF koruması
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
```

### ✅ DO: Secure Session Configuration

```python
# Production ortamında
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS zorunlu
app.config['SESSION_COOKIE_HTTPONLY'] = True    # XSS koruması
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF koruması
```

### ❌ DON'T: Hardcoded Secrets

```python
# YANLIŞ - Secret key'i hardcode etmeyin!
app.config['SECRET_KEY'] = 'my-secret-key-123'  # ⚠️

# DOĞRU - Environment variable kullanın
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
```

---

## Development vs Production

### Development Ortamı

```python
# config.py - DevelopmentConfig
class DevelopmentConfig(Config):
    DEBUG = True
    HSTS_ENABLED = False  # HTTPS zorunlu değil
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline' 'unsafe-eval'"
```

### Production Ortamı

```python
# config.py - ProductionConfig
class ProductionConfig(Config):
    DEBUG = False
    HSTS_ENABLED = True   # HTTPS zorunlu
    HSTS_MAX_AGE = 31536000  # 1 yıl
    SESSION_COOKIE_SECURE = True
    # Strict CSP (unsafe-inline kaldırıldı)
```

### Environment Variables

```bash
# .env dosyası (production)
FLASK_ENV=production
SECRET_KEY=<güçlü-rastgele-key>
DATABASE_URL=postgresql://user:pass@host/db
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
```

---

## Security Checklist

### ✅ Yeni Route Eklerken

- [ ] Schema validation kullanıldı mı?
- [ ] CSRF protection aktif mi?
- [ ] Authentication/authorization kontrolleri var mı?
- [ ] Input sanitization yapılıyor mu?
- [ ] Error messages sensitive bilgi içermiyor mu?
- [ ] Rate limiting gerekli mi?

### ✅ Yeni Template Eklerken

- [ ] `safe_text` filter kullanıldı mı?
- [ ] `safe_html` sadece gerektiğinde kullanıldı mı?
- [ ] `safe` filter kullanılmadı mı? (⚠️)
- [ ] CSRF token eklendi mi?
- [ ] Form validation mesajları gösteriliyor mu?

### ✅ Database İşlemleri

- [ ] ORM kullanılıyor mu?
- [ ] Raw SQL varsa parameterized mi?
- [ ] String concatenation yok mu?
- [ ] User input direkt query'de kullanılmıyor mu?

### ✅ Authentication

- [ ] Password hash'leniyor mu?
- [ ] Password strength validation var mı?
- [ ] Session timeout ayarlandı mı?
- [ ] Remember-me güvenli mi?
- [ ] Logout sonrası session temizleniyor mu?

### ✅ Production Deployment

- [ ] DEBUG = False
- [ ] HSTS enabled
- [ ] Secure cookies (HTTPS only)
- [ ] Environment variables kullanılıyor
- [ ] Secret keys hardcoded değil
- [ ] CSP policy strict
- [ ] Error logging aktif
- [ ] Regular security updates

---

## Güvenlik İhlali Durumunda

### Acil Durum Prosedürü

1. **Tespit ve İzolasyon**
   - Etkilenen sistemleri izole edin
   - Loglardaki anormal aktiviteyi kontrol edin

2. **Zarar Tespiti**
   - Hangi veriler etkilendi?
   - Kaç kullanıcı etkilendi?
   - Süre ne kadardı?

3. **Düzeltme**
   - Güvenlik açığını kapatın
   - Testleri çalıştırın
   - Security scan yapın

4. **İletişim**
   - Etkilenen kullanıcıları bilgilendirin
   - Yönetimi bilgilendirin
   - Gerekirse yetkililere bildirin

5. **Post-Mortem**
   - Kök neden analizi
   - Önleyici tedbirler
   - Dokümantasyon güncelleme

---

## Kaynaklar

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [bleach Documentation](https://bleach.readthedocs.io/)

---

**Son Güncelleme:** 2025-11-07  
**Versiyon:** 1.0
