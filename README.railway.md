# Railway Deployment Kılavuzu

Bu belge, Rezervasyon Sistemi'ni Railway platformuna nasıl deploy edeceğinizi açıklar.

## 🚂 Railway Nedir?

Railway, modern web uygulamalarını kolayca deploy etmenizi sağlayan bir Platform as a Service (PaaS) hizmetidir.

## 📋 Gereksinimler

1. **Railway Hesabı**: [railway.app](https://railway.app) üzerinden ücretsiz hesap oluşturun
2. **PostgreSQL Servisi**: Railway üzerinde PostgreSQL veritabanı eklemeniz gerekir
3. **Redis Servisi** (Opsiyonel ama önerilen): Cache ve session yönetimi için

## 🚀 Deployment Adımları

### 1. Railway'de Yeni Proje Oluşturun

```bash
# Railway CLI kurulumu (opsiyonel)
npm install -g @railway/cli

# Railway'e giriş yapın
railway login
```

### 2. PostgreSQL Servisini Ekleyin

Railway Dashboard'da:
1. "New" → "Database" → "PostgreSQL"
2. Veritabanı otomatik olarak oluşturulur
3. `DATABASE_URL` otomatik olarak ayarlanır

### 3. Redis Servisini Ekleyin (Opsiyonel)

Railway Dashboard'da:
1. "New" → "Database" → "Redis"
2. Redis otomatik olarak oluşturulur
3. `REDIS_URL` otomatik olarak ayarlanır

### 4. Ortam Değişkenlerini Ayarlayın

Railway Dashboard → Settings → Variables:

```env
# Flask Ayarları
FLASK_ENV=production
SECRET_KEY=<güçlü-rastgele-anahtar>
JWT_SECRET_KEY=<güçlü-jwt-anahtarı>

# Veritabanı (Otomatik ayarlanır)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Otomatik ayarlanır)
REDIS_URL=${{Redis.REDIS_URL}}
RATELIMIT_STORAGE_URL=${{Redis.REDIS_URL}}/2
SESSION_REDIS=${{Redis.REDIS_URL}}/1

# Upload Ayarları
UPLOAD_FOLDER=/app/app/static/uploads
MAX_CONTENT_LENGTH=16777216

# Güvenlik
WTF_CSRF_ENABLED=True
SESSION_TYPE=redis
SESSION_PERMANENT=False
SESSION_USE_SIGNER=True
SESSION_KEY_PREFIX=session_

# JWT Ayarları
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Gunicorn Ayarları
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=60
```

### 5. GitHub'dan Deploy Edin

Railway Dashboard'da:
1. "New" → "GitHub Repo"
2. Repository'nizi seçin
3. Branch'i seçin (genellikle `main`)
4. Otomatik deploy başlar

### 6. Manuel Deploy (CLI ile)

```bash
# Projeyi Railway'e bağlayın
railway link

# Deploy edin
railway up

# Logları izleyin
railway logs
```

## 🔧 Sorun Giderme

### Veritabanı Bağlantı Hatası

Yukarıdaki hata, PostgreSQL servisinin çalışmadığını gösteriyor. Çözüm:

1. **Railway Dashboard'da PostgreSQL servisini kontrol edin**:
   - Services → PostgreSQL → Status
   - "Running" durumunda olmalı

2. **DATABASE_URL'yi kontrol edin**:
   ```bash
   railway variables
   ```

3. **Veritabanı bağlantısını test edin**:
   ```bash
   railway run python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.engine.connect(); print('OK')"
   ```

4. **PostgreSQL servisini yeniden başlatın**:
   - Railway Dashboard → PostgreSQL → Settings → Restart

### Migration Hataları

```bash
# Railway'de migration çalıştırın
railway run flask db upgrade

# Eğer çalışmazsa, sıfırlayın
railway run flask db stamp head
railway run flask db migrate -m "Initial migration"
railway run flask db upgrade
```

### Redis Bağlantı Hatası

Rate limiting için Redis kullanılıyor. Eğer Redis yoksa:

```env
# In-memory storage kullanın (önerilmez)
RATELIMIT_STORAGE_URL=memory://
```

Ya da Redis servisini ekleyin.

### Disk Alanı Sorunları

Railway'de upload dosyaları geçici olarak saklanır. Production'da S3/Cloudinary kullanın:

```env
# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=your_bucket

# Cloudinary
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## 📊 İzleme ve Loglar

### Logları Görüntüleme

```bash
# Tüm loglar
railway logs

# Canlı takip
railway logs --follow

# Son 100 satır
railway logs --tail 100
```

### Metrikler

Railway Dashboard → Metrics:
- CPU kullanımı
- RAM kullanımı
- Network trafiği
- Request sayısı

## 🔒 Güvenlik

### HTTPS

Railway otomatik olarak SSL sertifikası sağlar. Custom domain eklerseniz:

1. Railway Dashboard → Settings → Domains
2. Domain'inizi ekleyin
3. DNS kayıtlarını güncelleyin
4. Railway otomatik SSL sertifikası oluşturur

### Ortam Değişkenleri

**Asla** şunları commit etmeyin:
- `.env` dosyası
- `SECRET_KEY`
- Veritabanı şifreleri
- API anahtarları

Tüm hassas bilgiler Railway Variables'da olmalı.

## 🎯 Production Checklist

- [ ] PostgreSQL servisi çalışıyor
- [ ] Redis servisi eklenmiş (rate limiting için)
- [ ] `FLASK_ENV=production` ayarlanmış
- [ ] Güçlü `SECRET_KEY` ve `JWT_SECRET_KEY` oluşturulmuş
- [ ] `DATABASE_URL` doğru
- [ ] HTTPS çalışıyor
- [ ] Custom domain eklenmiş (opsiyonel)
- [ ] Backup stratejisi var
- [ ] Monitoring kurulmuş
- [ ] Error tracking (Sentry) eklenmiş (opsiyonel)

## 📦 Yedekleme

Railway PostgreSQL otomatik yedekleme yapar, ancak manuel yedekleme için:

```bash
# Veritabanı yedeği al
railway run pg_dump $DATABASE_URL > backup.sql

# Geri yükle
railway run psql $DATABASE_URL < backup.sql
```

## 🆘 Destek

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Proje Issues**: GitHub Issues

## 📝 Notlar

1. **Ücretsiz Plan Limitleri**:
   - 500 saat/ay
   - $5 kredi/ay
   - Otomatik uyku modu yok (ücretli plana geç)

2. **Ölçeklendirme**:
   - Railway otomatik horizontal scaling yapmaz
   - Vertical scaling için: Settings → Resources

3. **Persistent Storage**:
   - Upload dosyaları için Volume kullanın
   - Ya da cloud storage (S3, Cloudinary) tercih edin

## 🔄 CI/CD

Railway, GitHub'a her push'ta otomatik deploy yapar:

1. GitHub → Settings → Webhooks → Railway webhook otomatik eklenir
2. Her commit'te yeni deploy başlar
3. Health check başarısızsa rollback yapar

---

**Son Güncelleme:** 9 Kasım 2025
**Railway Versiyon:** v2
