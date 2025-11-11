# 🚀 Coolify Deployment Rehberi

## 📋 Ön Hazırlık

### Gereksinimler
- ✅ Coolify kurulu sunucu
- ✅ Domain (opsiyonel, IP ile de çalışır)
- ✅ En az 2GB RAM
- ✅ En az 20GB disk alanı

## 🎯 Coolify'da Yapılacaklar

### 1. Yeni Proje Oluştur

```
1. Coolify Dashboard → "New Resource"
2. "Public Repository" seç
3. Repository URL: https://github.com/Optimus825482/rezervation.git
4. Branch: main
5. Build Pack: Docker Compose
```

### 2. Environment Variables Ayarla

Coolify'da "Environment Variables" sekmesine git ve şunları ekle:

```bash
# Flask Ayarları
FLASK_ENV=production
SECRET_KEY=BURAYA_GÜÇLÜ_BİR_KEY_OLUŞTUR
JWT_SECRET_KEY=BURAYA_GÜÇLÜ_BİR_JWT_KEY_OLUŞTUR
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database (Coolify PostgreSQL kullanacaksan)
DB_USER=postgres
DB_PASSWORD=GÜÇLÜ_BİR_ŞİFRE_OLUŞTUR
DB_NAME=rezervasyon_db

# Redis (Coolify Redis kullanacaksan)
REDIS_PASSWORD=GÜÇLÜ_BİR_ŞİFRE_OLUŞTUR

# Upload Ayarları
UPLOAD_FOLDER=/app/app/static/uploads
MAX_CONTENT_LENGTH=16777216

# Güvenlik
WTF_CSRF_ENABLED=True
```

### 3. Güçlü Key Oluşturma

Sunucunda şunu çalıştır:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))"
```

### 4. PostgreSQL Servisi Ekle

```
1. Coolify Dashboard → "New Resource" → "Database"
2. PostgreSQL seç
3. Database Name: rezervasyon_db
4. Username: postgres
5. Password: (yukarıda oluşturduğun şifreyi kullan)
6. "Create" tıkla
```

PostgreSQL başladıktan sonra:
- Internal URL'i kopyala (örn: `postgresql://postgres:password@postgres:5432/rezervasyon_db`)
- Ana projeye dön
- Environment Variables'a ekle:
```bash
DATABASE_URL=postgresql://postgres:ŞİFREN@postgres:5432/rezervasyon_db
```

### 5. Redis Servisi Ekle (Önerilen)

```
1. Coolify Dashboard → "New Resource" → "Database"
2. Redis seç
3. Password: (yukarıda oluşturduğun şifreyi kullan)
4. "Create" tıkla
```

Redis başladıktan sonra:
- Internal URL'i kopyala (örn: `redis://:password@redis:6379/0`)
- Ana projeye dön
- Environment Variables'a ekle:
```bash
REDIS_URL=redis://:ŞİFREN@redis:6379/0
```

### 6. Docker Compose Dosyasını Seç

Coolify'da:
```
1. "Build" sekmesine git
2. "Docker Compose File": docker-compose.prod.yml
3. "Save" tıkla
```

### 7. Port Ayarları

```
1. "Ports" sekmesine git
2. Port 80'i expose et (Nginx için)
3. HTTPS istiyorsan SSL/TLS ayarlarını yap
```

### 8. Domain Ayarları (Opsiyonel)

```
1. "Domains" sekmesine git
2. Domain'ini ekle (örn: rezervasyon.example.com)
3. SSL/TLS otomatik aktif olacak (Let's Encrypt)
```

### 9. Deploy Et!

```
1. "Deploy" butonuna tıkla
2. Logs'u izle
3. İlk deployment 5-10 dakika sürebilir
```

## 🔍 Deployment Kontrolü

### Logs İzleme

Coolify Dashboard'da "Logs" sekmesinden şunları kontrol et:

```
✅ PostgreSQL başladı
✅ Redis başladı
✅ Flask app başladı
✅ Nginx başladı
✅ Migrations tamamlandı
✅ Gunicorn workers aktif
```

### Health Check

Tarayıcıdan veya curl ile:
```bash
curl https://your-domain.com/health
# veya
curl http://your-server-ip/health
```

Başarılı yanıt:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

## ⚠️ Yaygın Sorunlar ve Çözümler

### Sorun 1: Database bağlantı hatası
**Çözüm**:
- PostgreSQL servisinin çalıştığını kontrol et
- DATABASE_URL'in doğru olduğunu kontrol et
- Internal network bağlantısını kontrol et

### Sorun 2: Redis bağlantı hatası
**Çözüm**:
- Redis servisinin çalıştığını kontrol et
- REDIS_URL'in doğru olduğunu kontrol et
- Şifrenin doğru olduğunu kontrol et

### Sorun 3: Port çakışması
**Çözüm**:
- Coolify'da farklı bir port kullan
- Veya çakışan servisi durdur

### Sorun 4: SSL sertifika hatası
**Çözüm**:
- Domain'in DNS ayarlarını kontrol et
- A kaydının sunucu IP'sine işaret ettiğinden emin ol
- Let's Encrypt rate limit'e takılmadığını kontrol et

## 🎯 Production Optimizasyonları

### 1. Resource Limits

docker-compose.prod.yml'de zaten ayarlı:
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### 2. Backup Stratejisi

PostgreSQL için otomatik backup:
```bash
# Coolify Dashboard → PostgreSQL → Backups
# Otomatik backup ayarla (günlük önerilen)
```

### 3. Monitoring

Coolify'ın built-in monitoring'ini kullan:
- CPU kullanımı
- Memory kullanımı
- Disk kullanımı
- Network trafiği

## 🔐 Güvenlik Kontrolleri

### ✅ Yapılması Gerekenler

- [ ] SECRET_KEY ve JWT_SECRET_KEY güçlü random değerler
- [ ] Database şifresi güçlü
- [ ] Redis şifresi güçlü
- [ ] HTTPS aktif (Let's Encrypt)
- [ ] Firewall ayarları yapıldı
- [ ] Sadece gerekli portlar açık (80, 443)
- [ ] SSH key-based authentication
- [ ] Fail2ban kurulu

### Firewall Ayarları (Sunucuda)

```bash
# UFW kullanıyorsan
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

## 📊 İlk Kullanıcı Oluşturma

Deployment başarılı olduktan sonra:

```bash
# Coolify'da "Terminal" sekmesine git
# Flask app container'ına bağlan
# Şunu çalıştır:

python create_superadmin.py
```

Veya manuel:
```bash
# Container'a gir
docker exec -it rezervasyon_app_prod bash

# Superadmin oluştur
python create_superadmin.py
```

## 🔄 Güncelleme Yaparken

### Otomatik Deployment

Coolify'da webhook ayarla:
```
1. "Settings" → "Webhooks"
2. GitHub webhook URL'ini kopyala
3. GitHub repo → Settings → Webhooks → Add webhook
4. URL'i yapıştır
5. Events: "Just the push event"
6. Save
```

Artık her push'ta otomatik deploy olacak!

### Manuel Deployment

```
1. Coolify Dashboard → Projen
2. "Deploy" butonuna tıkla
3. Logs'u izle
```

## 🎉 Başarılı Deployment Göstergeleri

```
✅ Tüm servisler "Running" durumda
✅ Health check başarılı
✅ Ana sayfa açılıyor
✅ Login çalışıyor
✅ Database işlemleri çalışıyor
✅ QR kod oluşturma çalışıyor
✅ Rezervasyon sistemi çalışıyor
```

## 📞 Destek ve Troubleshooting

### Logs Kontrolü

```bash
# Tüm servislerin logları
docker-compose -f docker-compose.prod.yml logs -f

# Sadece app logları
docker logs -f rezervasyon_app_prod

# Sadece database logları
docker logs -f rezervasyon_db_prod

# Sadece nginx logları
docker logs -f rezervasyon_nginx
```

### Container Durumu

```bash
# Çalışan container'ları göster
docker ps

# Tüm container'ları göster (durmuş olanlar dahil)
docker ps -a

# Resource kullanımı
docker stats
```

### Database Backup

```bash
# Manuel backup
docker exec rezervasyon_db_prod pg_dump -U postgres rezervasyon_db > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i rezervasyon_db_prod psql -U postgres rezervasyon_db < backup_20241105.sql
```

## 🚀 İleri Seviye

### Load Balancer Eklemek

Birden fazla instance çalıştırmak için:
```yaml
# docker-compose.prod.yml'de
app:
  deploy:
    replicas: 3  # 3 instance
```

### CDN Kullanımı

Static dosyalar için CDN:
```
1. Cloudflare kullan (ücretsiz)
2. Domain'i Cloudflare'e ekle
3. Proxy aktif et
4. Cache ayarlarını yap
```

---

**Hazır! Coolify'a yüklemeye başlayabilirsin! 🎯**

Sorular:
1. Domain var mı yoksa IP ile mi çalışacaksın?
2. SSL sertifikası gerekiyor mu?
3. Backup stratejisi ne olsun?
