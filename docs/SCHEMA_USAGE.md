# Schema Usage Documentation

## 📋 İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Mevcut Schemalar](#mevcut-schemalar)
3. [BaseSchema](#baseschema)
4. [UserSchema](#userschema)
5. [ReservationSchema](#reservationschema)
6. [EventSchema](#eventschema)
7. [TemplateSchema](#templateschema)
8. [Yeni Schema Oluşturma](#yeni-schema-oluşturma)
9. [Validation Örnekleri](#validation-örnekleri)
10. [Hata Yönetimi](#hata-yönetimi)

---

## Genel Bakış

Bu sistem, kullanıcı girdilerini validate etmek ve sanitize etmek için **Marshmallow** kütüphanesini kullanır. Her veri modeli için bir schema tanımlanmıştır.

### Neden Schema Kullanıyoruz?

✅ **Input Validation** - Geçersiz verileri erken yakala  
✅ **Type Safety** - Veri tiplerini garanti et  
✅ **XSS Protection** - Otomatik sanitization  
✅ **Documentation** - Self-documenting code  
✅ **Consistency** - Tutarlı validation mantığı

### Schema Mimarisi

```
BaseSchema (Temel işlevsellik)
    │
    ├── UserSchema (Kullanıcı validasyonu)
    │   └── PasswordChangeSchema
    │
    ├── ReservationSchema (Rezervasyon validasyonu)
    │
    ├── EventSchema (Etkinlik validasyonu)
    │
    └── TemplateSchema (Şablon validasyonu)
        ├── SeatingTemplateSchema
        └── EventTemplateSchema
```

---

## Mevcut Schemalar

### Schema Listesi

| Schema | Dosya | Kullanım Alanı |
|--------|-------|----------------|
| `BaseSchema` | `app/schemas/__init__.py` | Tüm schema'lar için temel sınıf |
| `UserSchema` | `app/schemas/user_schema.py` | Kullanıcı oluşturma/güncelleme |
| `PasswordChangeSchema` | `app/schemas/user_schema.py` | Şifre değiştirme |
| `ReservationSchema` | `app/schemas/reservation_schema.py` | Rezervasyon oluşturma |
| `EventSchema` | `app/schemas/event_schema.py` | Etkinlik oluşturma |
| `SeatingTemplateSchema` | `app/schemas/template_schema.py` | Oturma düzeni şablonu |
| `EventTemplateSchema` | `app/schemas/template_schema.py` | Etkinlik şablonu |

---

## BaseSchema

Tüm schema'lar için temel sınıf. Ortak işlevsellik sağlar.

### Özellikler

```python
class BaseSchema(Schema):
    """Base schema for all schemas"""
    
    class Meta:
        unknown = EXCLUDE  # Bilinmeyen alanları yoksay
    
    def validate_turkish_phone(self, phone: str) -> bool:
        """Türk telefon numarası validasyonu"""
        # +90 555 123 45 67, 05551234567 formatlarını destekler
        
    def normalize_turkish_phone(self, phone: str) -> str:
        """Telefon numarasını normalize et"""
        # +905551234567 formatına dönüştürür
```

### Kullanım

```python
from app.schemas import BaseSchema
from marshmallow import fields

class MySchema(BaseSchema):
    """Custom schema BaseSchema'dan türer"""
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
```

---

## UserSchema

Kullanıcı oluşturma ve güncelleme için schema.

### Alanlar

| Alan | Tip | Zorunlu | Validation |
|------|-----|---------|------------|
| `username` | String | ✅ | Alphanumeric, 3-80 karakter |
| `email` | Email | ✅ | Valid email format |
| `password` | String | ✅ | Güçlü şifre politikası |
| `first_name` | String | ✅ | 1-50 karakter |
| `last_name` | String | ✅ | 1-50 karakter |
| `phone` | String | ✅ | Türk telefon formatı |
| `role` | String | ✅ | admin, controller, user |

### Örnek Kullanım

```python
from app.schemas.user_schema import UserSchema
from marshmallow import ValidationError

@bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    schema = UserSchema()
    
    try:
        # Validate input data
        validated_data = schema.load({
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone'),
            'role': request.form.get('role', 'user')
        })
        
        # Create user with validated data
        user = User(
            company_id=current_user.company_id,
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kullanıcı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('admin.users'))
        
    except ValidationError as e:
        # Handle validation errors
        for field, messages in e.messages.items():
            for message in messages if isinstance(messages, list) else [messages]:
                flash(f'{field}: {message}', 'danger')
        return redirect(url_for('admin.users'))
```

### Password Validation

Şifre alanı otomatik olarak güçlü şifre politikasını kontrol eder:

```python
@validates('password')
def validate_password(self, value):
    """Validate password strength"""
    from app.utils.validators import validate_password_strength
    
    is_valid, message = validate_password_strength(value)
    if not is_valid:
        raise ValidationError(message)
```

**Şifre Gereksinimleri:**
- ✅ Minimum 8 karakter
- ✅ En az 1 büyük harf
- ✅ En az 1 küçük harf
- ✅ En az 1 rakam
- ✅ En az 1 özel karakter

---

## PasswordChangeSchema

Şifre değiştirme işlemleri için özel schema.

### Alanlar

| Alan | Tip | Zorunlu | Validation |
|------|-----|---------|------------|
| `current_password` | String | ✅ | - |
| `new_password` | String | ✅ | Güçlü şifre politikası |
| `confirm_password` | String | ✅ | new_password ile eşleşmeli |

### Örnek Kullanım

```python
from app.schemas.user_schema import PasswordChangeSchema

@bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_own_password():
    schema = PasswordChangeSchema()
    
    try:
        validated_data = schema.load({
            'current_password': request.form.get('current_password'),
            'new_password': request.form.get('new_password'),
            'confirm_password': request.form.get('confirm_password')
        })
        
        # Verify current password
        if not current_user.check_password(validated_data['current_password']):
            flash('Mevcut şifre yanlış.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Set new password
        current_user.set_password(validated_data['new_password'])
        db.session.commit()
        
        flash('Şifre başarıyla değiştirildi.', 'success')
        return redirect(url_for('admin.profile'))
        
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(url_for('admin.profile'))
```

---

## ReservationSchema

Rezervasyon oluşturma için schema.

### Alanlar

| Alan | Tip | Zorunlu | Validation |
|------|-----|---------|------------|
| `guest_name` | String | ✅ | 1-100 karakter |
| `guest_phone` | String | ✅ | Türk telefon formatı |
| `guest_count` | Integer | ✅ | Minimum 1 |
| `notes` | String | ❌ | Max 500 karakter |
| `special_requests` | String | ❌ | Max 500 karakter |

### Örnek Kullanım

```python
from app.schemas.reservation_schema import ReservationSchema

@bp.route('/reservation/create/<int:event_id>', methods=['POST'])
@login_required
def create_reservation(event_id):
    schema = ReservationSchema()
    
    try:
        validated_data = schema.load({
            'guest_name': request.form.get('guest_name'),
            'guest_phone': request.form.get('guest_phone'),
            'guest_count': request.form.get('guest_count'),
            'notes': request.form.get('notes')
        })
        
        reservation = Reservation(
            event_id=event_id,
            guest_name=validated_data['guest_name'],
            guest_phone=validated_data['guest_phone'],
            guest_count=validated_data['guest_count'],
            notes=validated_data.get('notes', '')
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        flash('Rezervasyon oluşturuldu.', 'success')
        return redirect(url_for('reservation.index'))
        
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(url_for('reservation.index'))
```

### Telefon Numarası Formatları

Schema aşağıdaki formatları kabul eder:

```
✅ +905551234567
✅ +90 555 123 45 67
✅ 05551234567
✅ 0555 123 45 67
✅ 555 123 45 67
```

---

## EventSchema

Etkinlik oluşturma için schema.

### Alanlar

| Alan | Tip | Zorunlu | Validation |
|------|-----|---------|------------|
| `name` | String | ✅ | 1-200 karakter |
| `description` | String | ❌ | Max 1000 karakter |
| `event_date` | Date | ✅ | Gelecek tarih |
| `event_time` | Time | ❌ | Valid time format |
| `capacity` | Integer | ✅ | Minimum 1 |
| `venue` | String | ❌ | Max 200 karakter |

### Örnek Kullanım

```python
from app.schemas.event_schema import EventSchema

@bp.route('/event/create', methods=['POST'])
@login_required
@admin_required
def create_event():
    schema = EventSchema()
    
    try:
        validated_data = schema.load({
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'capacity': request.form.get('capacity'),
            'venue': request.form.get('venue')
        })
        
        event = Event(
            company_id=current_user.company_id,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            event_date=validated_data['event_date'],
            event_time=validated_data.get('event_time'),
            capacity=validated_data['capacity'],
            venue=validated_data.get('venue', '')
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Etkinlik oluşturuldu.', 'success')
        return redirect(url_for('event.index'))
        
    except ValidationError as e:
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
        return redirect(url_for('event.index'))
```

---

## TemplateSchema

Şablon oluşturma için schema'lar.

### SeatingTemplateSchema

```python
from app.schemas.template_schema import SeatingTemplateSchema

schema = SeatingTemplateSchema()
validated_data = schema.load({
    'name': 'Restaurant Layout 1',
    'category': 'restaurant',  # restaurant, conference, theater, etc.
    'stage_position': 'north',  # north, south, east, west, center, none
    'configuration': '{}'  # JSON configuration
})
```

### EventTemplateSchema

```python
from app.schemas.template_schema import EventTemplateSchema

schema = EventTemplateSchema()
validated_data = schema.load({
    'name': 'Gala Dinner Template',
    'description': 'Standard gala dinner setup',
    'default_capacity': 200,
    'default_duration': 180  # minutes
})
```

---

## Yeni Schema Oluşturma

### Adım 1: Schema Dosyası Oluştur

```python
# app/schemas/my_schema.py

from marshmallow import fields, validates, ValidationError
from app.schemas import BaseSchema

class MySchema(BaseSchema):
    """My custom schema"""
    
    # Define fields
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    age = fields.Int(validate=lambda x: x >= 18)
    
    # Custom validators
    @validates('name')
    def validate_name(self, value):
        """Validate name field"""
        if not value.strip():
            raise ValidationError('Name cannot be empty')
        if len(value) > 100:
            raise ValidationError('Name is too long')
```

### Adım 2: Schema'yı Route'da Kullan

```python
from app.schemas.my_schema import MySchema
from marshmallow import ValidationError

@bp.route('/my-endpoint', methods=['POST'])
def my_endpoint():
    schema = MySchema()
    
    try:
        validated_data = schema.load({
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'age': request.form.get('age')
        })
        
        # Use validated data
        # ...
        
    except ValidationError as e:
        # Handle errors
        for field, messages in e.messages.items():
            flash(f'{field}: {messages[0]}', 'danger')
```

### Adım 3: Test Yaz

```python
# tests/test_my_schema.py

def test_valid_data():
    schema = MySchema()
    data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 25
    }
    result = schema.load(data)
    assert result['name'] == 'John Doe'

def test_invalid_email():
    schema = MySchema()
    data = {
        'name': 'John Doe',
        'email': 'invalid-email',
        'age': 25
    }
    with pytest.raises(ValidationError) as exc:
        schema.load(data)
    assert 'email' in exc.value.messages
```

---

## Validation Örnekleri

### String Validation

```python
# Required field
name = fields.Str(required=True)

# Max length
name = fields.Str(required=True, validate=lambda x: len(x) <= 100)

# Not empty
@validates('name')
def validate_name(self, value):
    if not value.strip():
        raise ValidationError('Field cannot be empty')
```

### Email Validation

```python
# Built-in email validation
email = fields.Email(required=True)

# Custom email validation
@validates('email')
def validate_email(self, value):
    if not value.endswith('@company.com'):
        raise ValidationError('Must use company email')
```

### Integer Validation

```python
# Minimum value
age = fields.Int(validate=lambda x: x >= 18)

# Range validation
count = fields.Int(validate=lambda x: 1 <= x <= 100)

# Multiple validations
@validates('count')
def validate_count(self, value):
    if value < 1:
        raise ValidationError('Count must be at least 1')
    if value > 1000:
        raise ValidationError('Count cannot exceed 1000')
```

### Date/Time Validation

```python
from marshmallow import fields
from datetime import datetime, date

# Date field
event_date = fields.Date(required=True)

# Future date only
@validates('event_date')
def validate_date(self, value):
    if value < date.today():
        raise ValidationError('Date must be in the future')

# Time field
event_time = fields.Time()
```

### Phone Validation

```python
# Turkish phone validation (built-in via BaseSchema)
phone = fields.Str(required=True)

# BaseSchema automatically validates Turkish phone format
# Accepts: +905551234567, 05551234567, +90 555 123 45 67, etc.
```

### Choice/Enum Validation

```python
from marshmallow import validates, ValidationError

role = fields.Str(required=True)

@validates('role')
def validate_role(self, value):
    valid_roles = ['admin', 'controller', 'user']
    if value not in valid_roles:
        raise ValidationError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')
```

---

## Hata Yönetimi

### Validation Error Handling

```python
from marshmallow import ValidationError

try:
    validated_data = schema.load(data)
except ValidationError as e:
    # e.messages is a dict: {'field': ['error1', 'error2']}
    for field, messages in e.messages.items():
        for message in messages if isinstance(messages, list) else [messages]:
            flash(f'{field}: {message}', 'danger')
```

### Flash Messages

```python
# Single error
flash('Email is invalid', 'danger')

# Field-specific errors
for field, messages in e.messages.items():
    flash(f'{field.title()}: {messages[0]}', 'danger')

# Multiple errors
errors = []
for field, messages in e.messages.items():
    errors.extend([f'{field}: {msg}' for msg in messages])
flash('; '.join(errors), 'danger')
```

### API Response Errors

```python
from flask import jsonify

try:
    validated_data = schema.load(data)
except ValidationError as e:
    return jsonify({
        'status': 'error',
        'errors': e.messages
    }), 400
```

### Custom Error Messages

```python
from marshmallow import fields, validates, ValidationError

class MySchema(BaseSchema):
    email = fields.Email(required=True, error_messages={
        'required': 'Email alanı zorunludur',
        'invalid': 'Geçersiz email formatı'
    })
    
    @validates('email')
    def validate_email(self, value):
        if not value.endswith('@company.com'):
            raise ValidationError('Sadece şirket emaili kullanılabilir')
```

---

## Best Practices

### ✅ DO

1. **Her zaman schema kullan** - Tüm user input'ları schema'dan geçir
2. **BaseSchema'dan türet** - Ortak işlevselliği paylaş
3. **Custom validators yaz** - Business logic'i validator'larda tut
4. **Test yaz** - Her schema için test suite oluştur
5. **Hataları handle et** - ValidationError'ları yakala ve user-friendly mesaj göster

### ❌ DON'T

1. **Schema'yı bypass etme** - Direkt request.form kullanma
2. **Validation logic'i route'ta tutma** - Schema'da tut
3. **Generic error messages** - Specific ve yardımcı mesajlar kullan
4. **Validation'ı skip etme** - "Trusted" input yok
5. **Schema'yı tekrar kullanma** - Her use case için uygun schema kullan

---

**Son Güncelleme:** 2025-11-07  
**Versiyon:** 1.0
