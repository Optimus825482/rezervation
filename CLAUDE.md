# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Event Reservation Management System** (Etkinlik Rezervasyon Yönetim Sistemi) built with Python Flask and PostgreSQL. The system enables visual planning and management of seat/table reservations for various event types, with QR code check-in capabilities.

**Target Audience**: Turkish-speaking users (interface should use Turkish language)

## Technology Stack

### Backend
- **Framework**: Flask 3.x (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login + Flask-JWT-Extended
- **Forms & Validation**: Flask-WTF, Marshmallow
- **Security**: Flask-Limiter, Flask-CORS, CSRF protection
- **QR Codes**: qrcode + Pillow
- **Phone Validation**: phonenumbers library (Turkish format: 05XX XXX XX XX)

### Reports & Analytics
- **PDF Export**: ReportLab or WeasyPrint
- **Excel Export**: openpyxl or xlsxwriter
- **Data Analysis**: pandas
- **Charts**: matplotlib or plotly

### Frontend (Recommended)
- **Framework**: React 18+ with TypeScript and Vite
- **State Management**: Zustand or Redux Toolkit + React Query
- **UI Framework**: Material-UI, Ant Design, or Chakra UI
- **Styling**: Tailwind CSS
- **Drag & Drop**: @dnd-kit/core (for visual seat arrangement)
- **Charts**: Recharts or ApexCharts
- **Forms**: React Hook Form + Zod/Yup validation
- **QR Code**: react-qr-code (display), html5-qrcode (scanning)
- **Alternative**: Jinja2 templates + Bootstrap 5 + Alpine.js + HTMX

### Infrastructure
- **Deployment**: Docker + Docker Compose
- **Web Server**: Nginx (reverse proxy) + Gunicorn (WSGI)
- **Cache/Session**: Redis
- **Monitoring**: Sentry (error tracking)

## Project Structure

```
rezervasyon-sistemi/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # SQLAlchemy models
│   │   ├── company.py           # Companies table
│   │   ├── user.py              # Users (Admin/Controller roles)
│   │   ├── event.py             # Events table
│   │   ├── template.py          # Seating & event templates
│   │   ├── seating.py           # Event seatings
│   │   └── reservation.py       # Reservations table
│   ├── routes/                  # Flask blueprints
│   │   ├── auth.py              # Login/logout
│   │   ├── admin.py             # Admin panel
│   │   ├── event.py             # Event management
│   │   ├── template.py          # Template management
│   │   ├── reservation.py       # Reservation CRUD
│   │   ├── report.py            # Advanced reporting
│   │   ├── controller.py        # Controller panel
│   │   └── checkin.py           # Check-in screen
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py
│   │   ├── event_service.py
│   │   ├── template_service.py
│   │   ├── reservation_service.py
│   │   ├── qr_service.py
│   │   └── report_service.py
│   ├── utils/                   # Helper functions
│   │   ├── validators.py        # Phone/email validation
│   │   ├── decorators.py        # @login_required, @admin_required
│   │   ├── chart_generator.py   # Chart generation utilities
│   │   └── helpers.py
│   ├── templates/               # Jinja2 templates (if using SSR)
│   ├── static/                  # CSS, JS, images
│   │   └── uploads/             # QR codes, logos
│   └── config.py                # Configuration classes
├── migrations/                  # Alembic database migrations
├── tests/                       # Unit and integration tests
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Environment variables template
└── run.py                       # Application entry point
```

## Core Architecture Concepts

### 1. User Roles & Permissions

**Admin (Sistem Yöneticisi)**:
- System setup and configuration
- Event creation with drag-and-drop visual seating arrangement
- Template management (seating layouts + event templates)
- Reservation management
- User (Controller) management
- Full access to all reports

**Controller (Kontrolör)**:
- Select active event after login
- View reservations for selected event
- View venue occupancy status
- Perform check-ins (QR code scan or manual search)
- View statistics and reports
- Read-only access to seating map

### 2. Template System (Critical Feature)

The system has two types of templates to speed up event creation:

**Seating Layout Templates** (seating_layout_templates table):
- Stores reusable seating arrangements
- Includes stage position, grid configuration, seat types/counts
- Saved as JSON configuration
- Can be marked as favorites
- Examples: "Wedding Hall Layout", "Concert Hall", "Conference Room"

**Event Templates** (event_templates table):
- Stores complete event configurations
- References a seating layout template
- Includes default event type, duration, venue type, pricing
- Quick event creation from templates

### 3. Visual Seating Planner

The drag-and-drop seating editor is a core feature:
- Define stage position (top/bottom/left/right)
- Drag and drop seats/tables to position them on a grid
- Automatic or manual seat numbering
- Color coding by seat type
- Real-time database synchronization
- Undo/redo functionality
- Save as template for reuse
- Grid system for easy alignment
- Zoom in/out capabilities

**Seat Types** (seating_types table - static data):
- Tables: 2, 4, 5, 6, 8, 10, 12-person capacity
- Single/double chairs
- VIP boxes
- Custom capacity seats

### 4. Reservation System

**Key Requirement**: Phone number is MANDATORY, name is optional
- Phone format: Turkish mobile (05XX XXX XX XX)
- Each reservation generates:
  - Unique reservation code
  - QR code image (stored in static/uploads/)
- Seat status updates automatically (available → reserved)
- Check-in tracking with timestamp and user

### 5. Advanced Reporting

Multiple report types with filters and export options:

**Report Types**:
1. General Summary (total events, reservations, check-in rate)
2. Event Detail Report (per-event reservation list)
3. Reservation Analysis (trends, patterns, cancellation rates)
4. Occupancy Analysis (seat type popularity, efficiency)
5. Customer Analysis (repeat customers by phone number)

**Export Formats**:
- PDF: Professional layout with company logo and charts
- Excel: Multi-sheet with pivot-ready data and charts
- CSV: Raw data export (UTF-8 for Turkish characters)

**Charts** (using pandas + matplotlib/plotly):
- Pie charts: Occupancy rate, event type distribution
- Bar charts: Event comparisons
- Line charts: Time-series trends
- Heat maps: Peak reservation times

### 6. Check-In System

**Two check-in methods**:
1. **QR Code Scanning**: Camera reads QR code → auto-finds reservation → shows customer info + seat location on visual map
2. **Manual Search**: Search by phone/name/reservation code → select customer → shows info + seat location

**Check-In Display**: Visual seating map highlights the customer's seat location

### 7. Customer Self-Service Kiosk (Optional Module)

Touchscreen kiosk at venue entrance:
- Large fonts for readability
- QR code reader or manual phone entry
- Shows reservation confirmation with seat number
- Highlights seat location on venue map
- Auto-reset after 30 seconds
- Full-screen kiosk mode

## Database Schema (Key Tables)

### companies
- Stores company info, logo, contact details
- Multi-tenant support (one installation, multiple companies)

### users
- Admin and Controller roles
- Belongs to company (company_id FK)
- Password hashing with werkzeug.security

### seating_layout_templates
- Reusable seating arrangements
- configuration: JSONB field with seat positions
- stage_position: ENUM
- category: For organizing templates (wedding, concert, etc.)

### event_templates
- Complete event presets
- References seating_layout_template_id
- settings: JSONB for defaults

### events
- Main event table
- References optional event_template_id
- status: draft/active/completed/cancelled
- venue dimensions (width/length in meters)
- stage_position

### seating_types
- Static lookup table for seat types
- Predefined capacity values

### event_seatings
- Actual seats for an event
- position_x, position_y: Grid coordinates
- status: available/reserved/disabled
- color_code: For visual distinction

### reservations
- phone: MANDATORY (VARCHAR 20)
- first_name, last_name: NULLABLE
- reservation_code: UNIQUE identifier
- qr_code_path: Path to generated QR image
- checked_in: BOOLEAN flag
- checked_in_at, checked_in_by: Audit fields
- status: active/cancelled

### activity_logs
- Audit trail for all actions
- User, event, action, IP address, timestamp

## Security Requirements

1. **Strong Password Policy**: Min 8 chars, uppercase/lowercase, numbers, special characters
2. **CSRF Protection**: Use Flask-WTF CSRFProtect
3. **SQL Injection Prevention**: SQLAlchemy ORM (never raw SQL)
4. **XSS Protection**: Jinja2 auto-escape enabled
5. **Rate Limiting**: Flask-Limiter on auth routes
6. **Input Validation**: Marshmallow schemas for all inputs
7. **Phone Number Validation**: Use phonenumbers library with Turkey locale
8. **Session Security**: Use Flask-Session with Redis backend
9. **Logging**: Log all sensitive operations to activity_logs table

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
# Edit .env with database credentials, secret keys, etc.

# Database setup
flask db init                  # First time only
flask db migrate -m "message"  # Create migration
flask db upgrade               # Apply migration

# Run development server
flask run
# or
python run.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_reservation.py
```

### Database Operations
```bash
# Create new migration
flask db migrate -m "Add templates table"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history
```

### Docker
```bash
# Build and run containers
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop containers
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## Important Implementation Notes

### 1. Phone Number Handling
Always use the phonenumbers library for validation:
```python
import phonenumbers
from phonenumbers import NumberParseException

def validate_turkish_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, "TR")
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        return False
```

### 2. QR Code Generation
QR codes should encode the reservation_code, not sensitive data:
```python
import qrcode
# QR code data format: "RES-{reservation_code}"
# Store in: static/uploads/qr/{reservation_id}.png
```

### 3. Seating Configuration JSON
Store seating layouts in JSONB format:
```json
{
  "grid": {"rows": 20, "cols": 30},
  "stage": {"position": "top", "size": {"width": 10, "height": 3}},
  "seats": [
    {
      "id": "M1",
      "type_id": 2,
      "capacity": 5,
      "position": {"x": 5, "y": 10},
      "color": "#FF5733"
    }
  ]
}
```

### 4. Multi-Tenant Isolation
Always filter queries by company_id from session:
```python
from flask_login import current_user

# In queries
Event.query.filter_by(company_id=current_user.company_id)
```

### 5. Turkish Language
- All UI text should be in Turkish
- Date formats: DD.MM.YYYY
- Number formats: 1.234,56 (dot for thousands, comma for decimal)
- Use Turkish collation for sorting (e.g., İ comes after I)

### 6. Report Generation Performance
- Use pandas for data aggregation before charting
- Cache report data in Redis for 5-10 minutes
- Generate PDFs asynchronously for large reports
- Implement pagination for long data tables

### 7. Drag-and-Drop State Management
- Store seat positions in database immediately on drop
- Use optimistic UI updates (update UI first, sync to DB)
- Implement debouncing for rapid position changes
- Validate positions don't overlap before saving

## Testing Strategy

1. **Unit Tests**: All service layer functions
2. **Integration Tests**: API endpoints with test database
3. **Security Tests**: Auth, CSRF, SQL injection attempts
4. **Phone Validation Tests**: Various Turkish phone formats
5. **Template System Tests**: Create/load/modify templates
6. **Report Generation Tests**: Verify data accuracy and export formats
7. **Drag-and-Drop Tests**: Position saving and collision detection

## Common Pitfalls to Avoid

1. **Don't make name/lastname required**: Only phone is mandatory in reservations
2. **Don't forget company_id filtering**: Prevents cross-company data leaks
3. **Don't store sensitive data in QR codes**: Only reservation code
4. **Don't use sequential reservation codes**: Use random alphanumeric (e.g., uuid4)
5. **Don't allow seat overbooking**: Check capacity before reservation
6. **Don't forget Turkish character support**: Use UTF-8 everywhere
7. **Don't skip input validation**: Always validate phone format
8. **Don't generate reports synchronously**: Use background tasks for large reports

## Environment Variables

Required `.env` configuration:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=<generate-random-key>
DATABASE_URL=postgresql://user:pass@localhost/rezervasyon_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<generate-random-key>
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Initial Setup Wizard

First-time users see a setup wizard to configure:
1. Company information (name, phone, email, address, logo)
2. First admin user (username, strong password, contact info)
3. Validation rules enforced (email format, Turkish phone, strong password)

## Localization Notes

- Use Flask-Babel for i18n if multi-language support is added later
- Currently Turkish-only, but structure code for future localization
- Store all UI strings in separate files/dictionaries for easy translation
