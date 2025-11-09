# Railway Deployment Checklist

## 🔧 Yapılan Düzeltmeler

### 1. ✅ Config.py Düzeltmeleri
- **postgres:// → postgresql:// dönüşümü** eklendi
- Railway'in `postgres://` URL'ini SQLAlchemy'nin beklediği `postgresql://` formatına çeviriyor
- Connection pool ayarları eklendi
- Timeout ayarları eklendi

### 2. ✅ Run.py İyileştirmeleri
- Production modda table creation atlanıyor (migrations kullanılıyor)
- Database connection verification eklendi
- Daha iyi error handling
- Gunicorn ile uyumlu hale getirildi

### 3. ✅ Start.sh Güçlendirmeleri
- PostgreSQL bağlantı kontrolü (60 saniye timeout)
- Port açık mı kontrolü
- Python ile connection test
- Detaylı hata mesajları

### 4. ✅ .env Dosyası Düzeltildi
- `DATABASE_URLU` → `DATABASE_URL` (typo düzeltildi)

## 🚀 Railway'de Yapılması Gerekenler

### 1. PostgreSQL Servisi
```
✓ PostgreSQL servisi ekle
✓ Private networking aktif olmalı
✓ DATABASE_URL otomatik set edilecek
```

### 2. Redis Servisi (Opsiyonel ama Önerilen)
```
✓ Redis servisi ekle
✓ REDIS_URL otomatik set edilecek
✓ Session storage için gerekli
```

### 3. Environment Variables
Railway dashboard'da şu değişkenleri set et:

```bash
# Zorunlu
FLASK_ENV=production
SECRET_KEY=<güçlü-random-key-buraya>
JWT_SECRET_KEY=<güçlü-random-key-buraya>

# Opsiyonel (varsayılan değerler var)
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=60
JWT_ACCESS_TOKEN_EXPIRES=3600
WTF_CSRF_ENABLED=True
```

### 4. Güçlü Secret Key Oluşturma
```bash
# Terminal'de çalıştır:
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📋 Deployment Adımları

### 1. Railway'de Yeni Proje Oluştur
```
1. Railway.app'e giriş yap
2. "New Project" → "Deploy from GitHub repo"
3. Repository'ni seç
```

### 2. PostgreSQL Ekle
```
1. Proje içinde "New" → "Database" → "Add PostgreSQL"
2. Servis başlayana kadar bekle
3. DATABASE_URL otomatik set edilecek
```

### 3. Redis Ekle (Önerilen)
```
1. Proje içinde "New" → "Database" → "Add Redis"
2. Servis başlayana kadar bekle
3. REDIS_URL otomatik set edilecek
```

### 4. Environment Variables Set Et
```
1. Web servisine tıkla
2. "Variables" sekmesine git
3. Yukarıdaki değişkenleri ekle
```

### 5. Deploy
```
1. "Deploy" butonuna tıkla veya
2. GitHub'a push yap (otomatik deploy)
```

## 🔍 Deployment Sonrası Kontroller

### 1. Logs Kontrolü
```bash
# Railway CLI ile
railway logs

# Veya Dashboard'dan
Settings → Deployments → View Logs
```

### 2. Kontrol Edilecek Loglar
```
✓ "🚀 Starting Railway Deployment..."
✓ "✅ PostgreSQL port is open!"
✓ "✅ Database is ready and accepting connections!"
✓ "✅ Migrations completed successfully!"
✓ "🌐 Starting Gunicorn server..."
✓ "Booting worker with pid: ..."
```

### 3. Health Check
```bash
# Railway URL'ini al
curl https://your-app.railway.app/health

# Veya tarayıcıdan ziyaret et
```

## ⚠️ Yaygın Sorunlar ve Çözümleri

### Sorun 1: "Connection refused"
**Sebep**: PostgreSQL servisi henüz başlamamış
**Çözüm**: 
- PostgreSQL servisinin "Running" durumda olduğunu kontrol et
- Logs'da "database system is ready to accept connections" mesajını ara
- Servisi restart et

### Sorun 2: "postgres:// not supported"
**Sebep**: SQLAlchemy postgresql:// bekliyor
**Çözüm**: ✅ Config.py'de düzeltildi (otomatik dönüşüm yapılıyor)

### Sorun 3: "Migration failed"
**Sebep**: Database bağlantısı yok veya yetki sorunu
**Çözüm**:
- DATABASE_URL'in doğru olduğunu kontrol et
- PostgreSQL servisinin çalıştığını kontrol et
- Private networking aktif mi kontrol et

### Sorun 4: "Redis connection failed"
**Sebep**: Redis servisi yok veya REDIS_URL yanlış
**Çözüm**:
- Redis servisi ekle
- REDIS_URL'in doğru olduğunu kontrol et
- Geçici olarak in-memory session kullanabilirsin (önerilmez)

## 🎯 Production Optimizasyonları

### 1. Gunicorn Workers
```bash
# CPU sayısına göre ayarla
GUNICORN_WORKERS = (2 x CPU_COUNT) + 1

# Railway'de genelde 4 yeterli
GUNICORN_WORKERS=4
```

### 2. Database Connection Pool
```python
# config.py'de zaten ayarlandı
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 300
}
```

### 3. Redis Session Storage
```bash
# Production'da mutlaka Redis kullan
SESSION_TYPE=redis
REDIS_URL=redis://...
```

## 📊 Monitoring

### Railway Dashboard
```
1. Metrics sekmesinde CPU, Memory, Network kullanımını izle
2. Logs sekmesinde hataları takip et
3. Deployments sekmesinde deployment geçmişini gör
```

### Application Logs
```bash
# Gerçek zamanlı log izleme
railway logs --follow

# Son 100 satır
railway logs --tail 100
```

## 🔐 Güvenlik Kontrolleri

### ✅ Yapıldı
- [x] HTTPS zorunlu (Railway otomatik)
- [x] Secure cookies (production'da aktif)
- [x] CSRF protection
- [x] Rate limiting
- [x] SQL injection koruması (SQLAlchemy ORM)
- [x] XSS koruması (Jinja2 auto-escape)

### 📝 Yapılacaklar
- [ ] SECRET_KEY ve JWT_SECRET_KEY'i güçlü random değerlerle değiştir
- [ ] CORS ayarlarını production domain'e göre ayarla
- [ ] Rate limit değerlerini production trafiğine göre ayarla

## 🎉 Başarılı Deployment Göstergeleri

```
✅ PostgreSQL bağlantısı başarılı
✅ Migrations tamamlandı
✅ Gunicorn başladı
✅ Workers aktif
✅ Health check başarılı
✅ Ana sayfa açılıyor
✅ Login çalışıyor
✅ Database işlemleri çalışıyor
```

## 📞 Destek

Sorun yaşarsan:
1. Railway logs'u kontrol et
2. PostgreSQL servisinin durumunu kontrol et
3. Environment variables'ı kontrol et
4. Bu checklist'i tekrar gözden geçir

## 🔄 Güncelleme Yaparken

```bash
# 1. Değişiklikleri commit et
git add .
git commit -m "Update: ..."

# 2. GitHub'a push et
git push origin main

# 3. Railway otomatik deploy edecek
# 4. Logs'u izle
railway logs --follow
```

---

**Not**: Railway'de her push otomatik deploy tetikler. Test etmeden push yapma!
