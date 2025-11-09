# Project Context

## Purpose
Etkinlik Rezervasyon Yönetim Sistemi - Modern, kapsamlı bir etkinlik rezervasyon ve yönetim çözümü. Konser, düğün, konferans gibi çeşitli etkinlikler için görsel koltuk düzenleme, QR kod tabanlı check-in, ve detaylı raporlama özellikleri sunar.

## Tech Stack
- **Backend**: Python 3.11, Flask 3.0
- **Database**: PostgreSQL 15+, SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Auth**: Flask-Login, Flask-JWT-Extended
- **Frontend**: Jinja2 Templates, Bootstrap 5, jQuery
- **QR Code**: qrcode + Pillow
- **Reports**: ReportLab, openpyxl, pandas, matplotlib, plotly
- **Deployment**: Docker + Docker Compose

## Project Conventions

### Code Style
- **Python**: PEP 8 compliance, max line length 100
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google style, required for all public functions/classes
- **Type Hints**: Encouraged for function signatures
- **Imports**: Standard library → third-party → local, alphabetically sorted

### Architecture Patterns
- **MVC Pattern**: Models (SQLAlchemy), Routes (Flask Blueprints), Templates (Jinja2)
- **Service Layer**: Business logic in `app/services/`
- **Blueprints**: Feature-based routing (`auth`, `admin`, `event`, `reservation`, `controller`, `checkin`, `report`)
- **ORM Only**: No raw SQL, use SQLAlchemy for all database operations
- **Session Management**: Redis-backed Flask sessions

### Testing Strategy
- **Framework**: pytest
- **Coverage Target**: >80%
- **Test Types**: Unit tests (models, services, utils), Integration tests (routes, DB)
- **Fixtures**: Use conftest.py for shared fixtures
- **Database**: Use test database or SQLite in-memory for tests

### Git Workflow
- **Branches**: `main` (production), `develop` (staging), `feature/*`, `bugfix/*`, `hotfix/*`
- **Commits**: Conventional commits (feat:, fix:, docs:, refactor:, test:)
- **PRs**: Required for merging to main/develop

## Domain Context

### User Roles
- **Admin**: Tam sistem erişimi - etkinlik oluşturma, koltuk düzenleme, rezervasyon yönetimi, raporlama, kullanıcı yönetimi
- **Controller**: Sınırlı erişim - etkinlik seçimi, rezervasyon görüntüleme, check-in işlemleri

### Core Entities
- **Company**: Çoklu firma desteği (multi-tenant)
- **Event**: Etkinlikler (konser, düğün, konferans, vb.)
- **EventSeating**: Etkinlik koltuk/masa düzeni (görsel pozisyon + kapasite)
- **Reservation**: Müşteri rezervasyonları (sadece telefon zorunlu, ad/soyad opsiyonel)
- **Template**: Yeniden kullanılabilir şablonlar (koltuk düzeni, etkinlik)

### Key Features
1. **Görsel Koltuk Düzenleme**: Drag-and-drop ile koltuk yerleştirme (KRITIK - şu an eksik)
2. **QR Kod Sistemi**: Her rezervasyona unique QR kod
3. **Check-in**: QR tarama veya manuel arama (QR scanner UI eksik)
4. **Şablon Sistemi**: Etkinlik ve koltuk düzeni şablonları
5. **Raporlama**: PDF/Excel/CSV export, grafikler

## Important Constraints

### Security
- CSRF koruması zorunlu (Flask-WTF)
- SQL Injection koruması (SQLAlchemy ORM only)
- Şifre hash'leme (Werkzeug)
- Rate limiting (Flask-Limiter)
- **EKSİK**: Input validation (Marshmallow), XSS koruması, güçlü şifre politikası

### Performance
- Database queries: <100ms target
- Page load: <3s target
- **EKSİK**: Database indeksler eksik
- Caching: Redis kullanımı için prepared

### Multi-tenancy
- Tüm veriler company_id ile izole
- Her işlemde company bazlı filtreleme gerekli
- Cross-company data leakage önlenmeli

## External Dependencies
- **PostgreSQL 15+**: Ana veritabanı
- **Redis 7+**: Session storage, cache
- **SMTP Server**: (Planlı) Email bildirimleri için
- **SMS Gateway**: (Planlı) SMS bildirimleri için

## Current Status (Based on Analysis Report)

### ✅ Tamamlanmış
- Database schema ve modeller (9 tablo)
- Temel authentication (Flask-Login, JWT)
- Temel CRUD işlemleri
- QR kod üretimi
- Docker setup

### ⚠️ Kısmi
- Frontend templates (mevcut ama eksik)
- Raporlama altyapısı (kütüphaneler yüklü, implementasyon eksik)

### ❌ Kritik Eksikler (Bu değişiklikler için hedef)
1. **Security Hardening**: Input validation, XSS, güçlü şifre
2. **Visual Seating Editor**: Drag-and-drop UI
3. **QR Code Scanner**: Web-based scanner UI
4. **Database Indexes**: Performans için kritik
5. **Production Deployment**: Nginx, Gunicorn, SSL

### Score
- Overall: 6.25/10 (İyi - Beta aşaması)
- Production ready: ~2-3 ay (kritik eksikler tamamlanınca)
