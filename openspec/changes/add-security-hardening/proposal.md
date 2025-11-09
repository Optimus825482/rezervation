# Security Hardening

## Why

Sistem analiz raporuna göre güvenlik puanı 6/10 seviyesinde ve kritik güvenlik eksiklikleri mevcut:
- Input validation eksik (kullanıcı girdileri doğrulanmıyor)
- XSS (Cross-Site Scripting) koruması yetersiz
- Güçlü şifre politikası uygulanmıyor
- Security headers (CSP, X-Frame-Options, vb.) eksik

Bu eksiklikler production ortamında ciddi güvenlik riskleri oluşturur.

## What Changes

- **ADDED**: Marshmallow tabanlı input validation şemaları (rezervasyon, kullanıcı, etkinlik)
- **ADDED**: XSS koruması için output sanitization
- **ADDED**: Güçlü şifre politikası (min 8 karakter, büyük/küçük harf, sayı, özel karakter)
- **ADDED**: Security headers middleware (CSP, X-Frame-Options, HSTS, X-Content-Type-Options)
- **ADDED**: Şifre kuvvet kontrolü helper fonksiyonu
- **MODIFIED**: User model - şifre doğrulama methodunu güçlendir
- **MODIFIED**: Auth routes - input validation ekle

## Impact

### Affected Specs
- `auth` - Authentication ve authorization
- `validation` - Input validation (YENİ capability)

### Affected Code
- `app/models/user.py` - Password validation
- `app/routes/auth.py` - Input validation
- `app/routes/reservation.py` - Input validation
- `app/routes/event.py` - Input validation
- `app/utils/validators.py` - Validation helpers
- `app/__init__.py` - Security headers middleware
- `app/schemas/` (YENİ) - Marshmallow schemas

### Dependencies Added
- marshmallow-sqlalchemy (zaten requirements.txt'de mevcut)
- bleach (XSS sanitization için eklenecek)

### Breaking Changes
- **BREAKING**: Mevcut zayıf şifreler artık kabul edilmeyecek
- Migration gerekebilir: Mevcut kullanıcıları şifre değiştirmeye zorla

## Migration Plan

1. Yeni şifre politikasını uygula
2. Mevcut kullanıcılara email/bildirim gönder (şifre güncelleme gerekli)
3. İlk login'de şifre kontrolü yap, uygun değilse şifre değiştirmeye yönlendir
