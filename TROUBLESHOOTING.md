# Sorun Giderme Rehberi

## Tarayıcı Uyarıları

### "Tracking Prevention blocked access to storage"

**Nedir?**
- Edge ve Safari tarayıcılarının gizlilik koruması özelliğinden kaynaklanır
- localStorage/sessionStorage erişimini engeller
- Genellikle zararsızdır ve göz ardı edilebilir

**Çözümler:**

1. **Edge için:**
   ```
   Ayarlar → Gizlilik, arama ve hizmetler → 
   İzleme önleme → Temel (veya kapalı)
   ```

2. **Safari için:**
   ```
   Preferences → Privacy → 
   Prevent cross-site tracking → Kapat
   ```

3. **Geliştirme için:**
   - Chrome veya Firefox kullanın (daha az kısıtlama)
   - Localhost için "Tracking Prevention" genelde sorun çıkarmaz

## URL Hataları

### 404 Not Found Hatası

**Olası Nedenler:**

1. **Blueprint URL Prefix Eksik**
   ```python
   # app/__init__.py
   app.register_blueprint(event.bp, url_prefix='/event')
   ```

2. **Route Tanımı Yanlış**
   ```python
   # Doğru
   @bp.route('/<int:event_id>/save-layout', methods=['POST'])
   
   # Yanlış
   @app.route('/event/<int:event_id>/save-layout')
   ```

3. **JavaScript'te Hardcoded URL**
   ```javascript
   // Doğru
   fetch("{{ url_for('event.save_layout', event_id=event.id) }}")
   
   // Yanlış
   fetch('/event/' + eventId + '/save-layout')
   ```

**Kontrol:**
```bash
docker-compose exec app flask routes | grep event
```

## CORS Hataları

### "Access-Control-Allow-Origin" hatası

**Çözüm:**
```python
# app/__init__.py
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

## CSP (Content Security Policy) Hataları

### "Refused to load ... because it violates CSP directive"

**Çözüm:**
```python
# app/security_config.py
CSP_SCRIPT_SRC = "'self' 'unsafe-inline' https://cdn.example.com"
CSP_STYLE_SRC = "'self' 'unsafe-inline' https://cdn.example.com"
```

## Database Hataları

### Migration Hatası

```bash
# Reset migrations
docker-compose exec app flask db init
docker-compose exec app flask db migrate -m "Initial migration"
docker-compose exec app flask db upgrade
```

### "relation does not exist" hatası

```bash
# Tüm tabloları yeniden oluştur
docker-compose exec app python
>>> from app import db
>>> db.create_all()
```

## Docker Hataları

### Container başlamıyor

```bash
# Logları kontrol et
docker-compose logs app

# Containerı yeniden başlat
docker-compose restart app

# Tümünü yeniden oluştur
docker-compose down
docker-compose up --build
```

### Port zaten kullanımda

```bash
# Windows'da portu kontrol et
netstat -ano | findstr :5000

# İşlemi sonlandır
taskkill /PID <PID> /F
```

## Genel İpuçları

1. **Her zaman logları kontrol edin:**
   ```bash
   docker-compose logs -f app
   ```

2. **Tarayıcı cache'ini temizleyin:**
   - Ctrl+Shift+Delete
   - Hard refresh: Ctrl+F5

3. **Flask debug modunu kullanın:**
   ```python
   # .env
   FLASK_DEBUG=1
   ```

4. **Flask routes'u listeleyin:**
   ```bash
   docker-compose exec app flask routes
   ```

5. **Database'i kontrol edin:**
   ```bash
   docker-compose exec db psql -U postgres -d rezervasyon
   \dt  # Tabloları listele
   ```
