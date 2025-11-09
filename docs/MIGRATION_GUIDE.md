# Migration Guide for Existing Users

## 📋 İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Versiyon Bilgisi](#versiyon-bilgisi)
3. [Breaking Changes](#breaking-changes)
4. [Migration Adımları](#migration-adımları)
5. [Route Güncellemeleri](#route-güncellemeleri)
6. [Template Güncellemeleri](#template-güncellemeleri)
7. [Test Güncellemeleri](#test-güncellemeleri)
8. [Deployment Notları](#deployment-notları)
9. [Rollback Prosedürü](#rollback-prosedürü)
10. [FAQ](#faq)

---

## Genel Bakış

Bu rehber, mevcut rezervasyon sistemini **Security Hardening** güncellemesine geçirmek için gerekli adımları açıklar.

### Güncelleme Özeti

**Versiyon:** 1.0 → 2.0 (Security Hardening)  
**Tarih:** 2025-11-07  
**Kategori:** Major Security Update

### Neler Değişti?

✅ **Input Validation** - Tüm user input'ları Marshmallow schema ile validate ediliyor  
✅ **XSS Protection** - bleach library + custom Jinja2 filters  
✅ **Password Security** - Güçlü şifre politikası zorunlu  
✅ **Security Headers** - 7 güvenlik header'ı eklendi  
✅ **Route Protection** - Tüm route'lar schema validation kullanıyor  
✅ **CSP Reporting** - Content Security Policy ihlalleri loglanıyor

### Backward Compatibility

⚠️ **Breaking Changes Var** - Manuel migration gerekli  
⚠️ **Şifre Reset** - Tüm kullanıcılar yeni şifre politikasına uymalı  
⚠️ **Template Updates** - Template syntax'ı güncellendi

---

## Versiyon Bilgisi

### Sistem Gereksinimleri

```
Python: 3.11+
Flask: 3.0.0+
PostgreSQL: 15+
Redis: 7.0+
```

### Yeni Dependencies

```txt
bleach==6.1.0           # XSS sanitization
marshmallow==3.20.2     # Schema validation
phonenumbers==9.0.18    # Phone validation
Flask-Session==0.8.0    # Session management
```

### Güncelleme Komutu

```bash
pip install -r requirements.txt
```

---

## Breaking Changes

### 1. Password Policy Enforcement

**ÖNCESİ:** Herhangi bir şifre kabul ediliyordu  
**SONRASI:** Güçlü şifre politikası zorunlu

```python
# Artık bu şifreler kabul edilmiyor:
❌ "password"
❌ "123456"
❌ "admin"

# Geçerli şifre örnekleri:
✅ "SecurePass123!"
✅ "MyP@ssw0rd2024"
✅ "C0mpl3x!Pass"
```

**Gereksinimler:**
- Minimum 8 karakter
- En az 1 büyük harf
- En az 1 küçük harf
- En az 1 rakam
- En az 1 özel karakter

### 2. Phone Number Format

**ÖNCESİ:** Herhangi bir format kabul ediliyordu  
**SONRASI:** Sadece geçerli Türk telefon numaraları

```python
# Geçerli formatlar:
✅ +905551234567
✅ 05551234567
✅ +90 555 123 45 67
✅ 0555 123 45 67

# Artık kabul edilmiyor:
❌ 123
❌ abcdefg
❌ 0000000000
```

### 3. Schema Validation

**ÖNCESİ:** request.form direkt kullanılıyordu  
**SONRASI:** Tüm input'lar schema'dan geçmeli

```python
# ÖNCESİ (Artık YANLIŞ):
@bp.route('/users/create', methods=['POST'])
def create_user():
    user = User(
        email=request.form.get('email'),  # ⚠️ Validate edilmemiş!
        name=request.form.get('name')     # ⚠️ XSS riski!
    )

# SONRASI (DOĞRU):
from app.schemas.user_schema import UserSchema
from marshmallow import ValidationError

@bp.route('/users/create', methods=['POST'])
def create_user():
    schema = UserSchema()
    try:
        validated_data = schema.load({
            'email': request.form.get('email'),
            'name': request.form.get('name')
        })
        user = User(**validated_data)
    except ValidationError as e:
        # Handle errors
```

### 4. Template Filters

**ÖNCESİ:** Otomatik escaping  
**SONRASI:** Custom filter'lar zorunlu

```html
<!-- ÖNCESİ (Artık güvenli değil): -->
<td>{{ user.name }}</td>

<!-- SONRASI (DOĞRU): -->
<td>{{ user.name | safe_text }}</td>
<td>{{ user.phone | format_phone }}</td>
```

### 5. Security Headers

**YENİ:** Tüm response'lara otomatik security header'ları ekleniyor

```
Content-Security-Policy
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security (production only)
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

---

## Migration Adımları

### Adım 1: Backup

```bash
# Database backup
pg_dump rezervasyon_db > backup_$(date +%Y%m%d).sql

# Code backup
git tag -a v1.0-backup -m "Pre-migration backup"
git push --tags

# File backup
tar -czf backup_files_$(date +%Y%m%d).tar.gz app/ static/ templates/
```

### Adım 2: Dependencies Güncelleme

```bash
# Virtual environment aktif et
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Dependencies'leri güncelle
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import bleach; import marshmallow; print('OK')"
```

### Adım 3: Database Migration

```bash
# Migration script'lerini çalıştır
flask db upgrade

# Verify migration
flask db current
```

### Adım 4: Şifre Reset Emaili Gönder

**Önemli:** Tüm kullanıcıların şifrelerini sıfırlaması gerekiyor!

```python
# scripts/send_password_reset.py
from app import create_app, db
from app.models import User
from flask_mail import Mail, Message

app = create_app('production')
mail = Mail(app)

with app.app_context():
    users = User.query.all()
    for user in users:
        # Generate password reset token
        token = user.get_reset_token()
        
        # Send email
        msg = Message(
            'Şifre Güncelleme Gerekli',
            recipients=[user.email]
        )
        msg.body = f'''Sistemimiz güvenlik güncellemesi aldı.
        
Yeni şifre politikası:
- Minimum 8 karakter
- En az 1 büyük harf, 1 küçük harf, 1 rakam, 1 özel karakter

Şifrenizi sıfırlamak için: {url_for('auth.reset_password', token=token, _external=True)}
'''
        mail.send(msg)

print(f'{len(users)} kullanıcıya email gönderildi.')
```

```bash
# Email gönder
python scripts/send_password_reset.py
```

### Adım 5: Template Güncellemeleri

Tüm template'leri güncellemeniz gerekiyor:

```bash
# Template'lerdeki safe_text filter eksikliklerini bul
grep -r "{{ .*\\..*}}" app/templates/ | grep -v "safe_text" | grep -v "safe_html" | grep -v "format_phone"

# Her bir template'i manuel olarak güncelleyin
```

### Adım 6: Route Güncellemeleri

Custom route'larınızı schema validation kullanacak şekilde güncelleyin:

```python
# Örnek: Custom route güncelleme
# ÖNCESİ:
@bp.route('/my-route', methods=['POST'])
def my_route():
    data = request.form.get('data')
    # process data

# SONRASI:
from app.schemas.my_schema import MySchema
from marshmallow import ValidationError

@bp.route('/my-route', methods=['POST'])
def my_route():
    schema = MySchema()
    try:
        validated_data = schema.load({
            'data': request.form.get('data')
        })
        # process validated_data
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
```

### Adım 7: Test

```bash
# Tüm testleri çalıştır
pytest

# Özel test suite'leri
pytest tests/test_schemas.py -v
pytest tests/test_password_validation.py -v
pytest tests/test_xss_simple.py -v
pytest tests/test_security_headers.py -v
pytest tests/test_route_protection.py -v
```

### Adım 8: Production Deployment

```bash
# 1. Maintenance mode aktif et
touch maintenance.flag

# 2. Code deploy
git pull origin main

# 3. Dependencies
pip install -r requirements.txt

# 4. Database migration
flask db upgrade

# 5. Static files
flask collect-static

# 6. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 7. Maintenance mode kapat
rm maintenance.flag

# 8. Health check
curl -I https://your-domain.com/health
```

---

## Route Güncellemeleri

### Tüm Custom Route'ları Güncelle

#### 1. Schema Oluştur

```python
# app/schemas/my_schema.py
from app.schemas import BaseSchema
from marshmallow import fields, validates, ValidationError

class MyCustomSchema(BaseSchema):
    field1 = fields.Str(required=True)
    field2 = fields.Int(validate=lambda x: x > 0)
    
    @validates('field1')
    def validate_field1(self, value):
        if len(value) > 100:
            raise ValidationError('Too long')
```

#### 2. Route'u Güncelle

```python
# app/routes/my_routes.py
from app.schemas.my_schema import MyCustomSchema
from marshmallow import ValidationError

@bp.route('/my-endpoint', methods=['POST'])
def my_endpoint():
    schema = MyCustomSchema()
    
    try:
        validated_data = schema.load(request.form)
        # Use validated_data
        
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(request.referrer)
```

### Ortak Route Pattern'leri

#### Create Route

```python
@bp.route('/resource/create', methods=['POST'])
@login_required
def create_resource():
    schema = ResourceSchema()
    try:
        validated_data = schema.load(request.form)
        resource = Resource(**validated_data, user_id=current_user.id)
        db.session.add(resource)
        db.session.commit()
        flash('Created successfully', 'success')
        return redirect(url_for('resource.index'))
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(url_for('resource.index'))
```

#### Update Route

```python
@bp.route('/resource/<int:id>/edit', methods=['POST'])
@login_required
def edit_resource(id):
    resource = Resource.query.get_or_404(id)
    schema = ResourceSchema()
    try:
        validated_data = schema.load(request.form)
        for key, value in validated_data.items():
            setattr(resource, key, value)
        db.session.commit()
        flash('Updated successfully', 'success')
        return redirect(url_for('resource.index'))
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(url_for('resource.edit', id=id))
```

---

## Template Güncellemeleri

### User Input Gösterimi

```html
<!-- ÖNCESİ -->
<td>{{ user.name }}</td>
<td>{{ user.email }}</td>

<!-- SONRASI -->
<td>{{ user.name | safe_text }}</td>
<td>{{ user.email | safe_text }}</td>
```

### Telefon Numarası

```html
<!-- ÖNCESİ -->
<td>{{ reservation.phone }}</td>

<!-- SONRASI -->
<td>{{ reservation.phone | format_phone }}</td>
<!-- Çıktı: 0555 123 45 67 -->
```

### HTML İçerik

```html
<!-- ÖNCESİ -->
<div>{{ event.description | safe }}</div>

<!-- SONRASI -->
<div>{{ event.description | safe_html }}</div>
<!-- Sadece güvenli HTML taglarına izin verir -->
```

### Form Validation Messages

```html
<!-- Şifre politikası mesajı ekle -->
<div class="form-group">
    <label for="password">Şifre</label>
    <input type="password" name="password" required>
    <small class="form-text text-muted">
        En az 8 karakter, 1 büyük harf, 1 küçük harf, 1 rakam ve 1 özel karakter içermelidir.
    </small>
</div>
```

---

## Test Güncellemeleri

### Yeni Test Kategorileri

1. **Schema Tests** (`tests/test_schemas.py`)
2. **Password Tests** (`tests/test_password_validation.py`)
3. **XSS Tests** (`tests/test_xss_simple.py`)
4. **Security Headers Tests** (`tests/test_security_headers.py`)
5. **Route Protection Tests** (`tests/test_route_protection.py`)

### Custom Test Örnekleri

```python
# tests/test_my_route.py
def test_my_route_with_valid_data(client):
    """Test route with valid data"""
    response = client.post('/my-route', data={
        'field1': 'valid data',
        'field2': '10'
    })
    assert response.status_code == 200

def test_my_route_with_xss(client):
    """Test route blocks XSS"""
    response = client.post('/my-route', data={
        'field1': '<script>alert(1)</script>',
        'field2': '10'
    })
    assert response.status_code == 200
    assert b'<script>' not in response.data
```

---

## Deployment Notları

### Environment Variables

```bash
# .env (production)
FLASK_ENV=production
SECRET_KEY=<güçlü-rastgele-key>
DATABASE_URL=postgresql://user:pass@host/db

# Security
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
SESSION_COOKIE_SECURE=true
```

### Nginx Configuration

```nginx
# CSP header (Nginx tarafından override edilmemeli)
# Flask'tan gelen header'ları kullan
proxy_pass_header Content-Security-Policy;
proxy_pass_header X-Frame-Options;
proxy_pass_header Strict-Transport-Security;
```

### SSL/TLS

```bash
# Production'da HTTPS zorunlu
# Let's Encrypt kullanımı önerilir
certbot --nginx -d your-domain.com
```

---

## Rollback Prosedürü

Eğer migration sırasında sorun yaşarsanız:

### Adım 1: Kodu Geri Al

```bash
git checkout v1.0-backup
```

### Adım 2: Database Rollback

```bash
# Migration'ları geri al
flask db downgrade -1

# Veya backup'tan restore et
psql rezervasyon_db < backup_20251107.sql
```

### Adım 3: Dependencies Rollback

```bash
# Eski requirements.txt'yi kullan
pip install -r requirements.txt.old
```

### Adım 4: Service Restart

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## FAQ

### S: Mevcut kullanıcıların şifreleri ne olacak?

**C:** Tüm kullanıcıların şifrelerini sıfırlaması gerekiyor. Migration script'i otomatik email gönderir.

### S: Custom route'larım çalışmayacak mı?

**C:** Custom route'ları schema validation kullanacak şekilde güncellemeniz gerekiyor.

### S: Template'lerdeki değişiklikler zorunlu mu?

**C:** Evet, XSS koruması için tüm user input gösterimlerinde `safe_text` filter kullanılmalı.

### S: Production'da test edebilir miyim?

**C:** Önce staging ortamında test edin. Production'a geçmeden önce tam test yapın.

### S: Migration ne kadar sürer?

**C:** Sistem büyüklüğüne bağlı, tipik olarak 15-30 dakika.

### S: Downtime olacak mı?

**C:** Evet, migration sırasında 5-10 dakika downtime olacak.

### S: Rollback mümkün mü?

**C:** Evet, backup'larınız varsa geri dönüş mümkün.

### S: API endpoint'lerim etkilenir mi?

**C:** Evet, tüm endpoint'ler schema validation kullanmalı.

---

## Destek

Sorun yaşarsanız:

1. **Logları kontrol edin:**
   ```bash
   tail -f /var/log/gunicorn/error.log
   ```

2. **Test çalıştırın:**
   ```bash
   pytest -v
   ```

3. **Documentation okuyun:**
   - [Security Best Practices](SECURITY_BEST_PRACTICES.md)
   - [Schema Usage](SCHEMA_USAGE.md)

4. **GitHub Issue açın:**
   - Detaylı hata mesajı
   - Reproduction steps
   - Environment bilgisi

---

**Migration Tarihi:** 2025-11-07  
**Doküman Versiyonu:** 1.0  
**Son Güncelleme:** 2025-11-07
