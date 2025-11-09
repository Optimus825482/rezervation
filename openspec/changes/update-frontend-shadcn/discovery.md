# Frontend Discovery

## Template Inventory

### Global Layout

- `app/templates/base.html`
- `app/templates/partials/` (headers, footers, forms, tables)
- `app/templates/partials/macros.html`

### Authentication

- `app/templates/auth/login.html`
- `app/templates/auth/register.html`
- `app/templates/auth/reset_password.html`
- `app/templates/auth/forgot_password.html`

### Dashboard & Admin

- `app/templates/admin/dashboard.html`
- `app/templates/admin/users.html`
- `app/templates/admin/create_user.html`
- `app/templates/admin/edit_user.html`
- `app/templates/admin/seating_types.html`

### Events

- `app/templates/event/index.html`
- `app/templates/event/create.html`
- `app/templates/event/edit.html`
- `app/templates/event/detail.html`

### Reservations

- `app/templates/reservation/index.html`
- `app/templates/reservation/create.html`
- `app/templates/reservation/edit.html`
- `app/templates/reservation/detail.html`

### Check-in & Controller

- `app/templates/checkin/index.html`
- `app/templates/checkin/scan.html`
- `app/templates/controller/index.html`

### Templates Feature

- `app/templates/template/seating_templates.html`
- `app/templates/template/create.html`
- `app/templates/template/edit.html`

### Reports

- `app/templates/report/index.html`
- `app/templates/report/detail.html`

### Static/PWA

- `app/templates/offline.html`
- `app/templates/partials/pwa/install.html`

## Static Asset Inventory

### CSS

- `app/static/css/main.css` (Bootstrap-inspired responsive styles)
- `app/static/css/shadcn.css` (Tailwind layer placeholders)
- `app/static/css/auth.css`, `app/static/css/checkin.css` (feature-specific)

### JavaScript

- `app/static/js/main.js` (bootstrap nav, install prompt)
- `app/static/js/shadcn-utils.js` (placeholder)
- `app/static/js/checkin.js`, `app/static/js/event.js`, `app/static/js/reservation.js`

### Service Worker & Manifest

- `app/static/service-worker.js`
- `app/static/manifest.json`

### Assets

- `app/static/icons/**`
- `app/static/uploads/logos/**`

## Kullanıcı Akışları

- Dashboard → Hızlı yönetim linkleri, istatistik kartları.
- Event yönetimi → Liste, oluşturma/düzenleme formları.
- Reservation akışı → Listeler, filtre, detay, QR üretimi.
- Check-in → QR tarama, manuel arama, rez detayları.
- Auth → Giriş/kayıt/reset, mobil uyumlu formlar.
- PWA → Offline sayfası, install prompt, loading overlay.
