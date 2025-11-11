# ⚡ Coolify Hızlı Başlangıç

## 🎯 5 Dakikada Deploy Et!

### 1️⃣ Güçlü Şifreler Oluştur (1 dk)

Sunucunda çalıştır:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))"
```

Çıktıları bir yere kaydet!

### 2️⃣ Coolify'da PostgreSQL Ekle (1 dk)

```
Dashboard → New Resource → Database → PostgreSQL
- Name: rezervasyon-db
- Username: postgres
- Password: (yukarıda oluşturduğun DB_PASSWORD)
- Database: rezervasyon_db
→ Create
```

Internal URL'i kopyala (örn: `postgresql://postgres:pass@postgres:5432/rezervasyon_db`)

### 3️⃣ Coolify'da Redis Ekle (1 dk)

```
Dashboard → New Resource → Database → Redis
- Name: rezervasyon-redis
- Password: (yukarıda oluşturduğun REDIS_PASSWORD)
→ Create
```

Internal URL'i kopyala (örn: `redis://:pass@redis:6379/0`)

### 4️⃣ Projeyi Ekle (1 dk)

```
Dashboard → New Resource → Public Repository
- Repository: https://github.com/Optimus825482/rezervation.git
- Branch: main
- Build Pack: Docker Compose
- Docker Compose File: docker-compose.coolify.yml
→ Create
```

### 5️⃣ Environment Variables Ekle (1 dk)

Proje → Environment Variables → Şunları ekle:

```bash
# Zorunlu
FLASK_ENV=production
SECRET_KEY=ADIM_1_DEN_KOPYALA
JWT_SECRET_KEY=ADIM_1_DEN_KOPYALA
DATABASE_URL=ADIM_2_DEN_KOPYALA
REDIS_URL=ADIM_3_DEN_KOPYALA

# Database
DB_USER=postgres
DB_PASSWORD=ADIM_1_DEN_KOPYALA
DB_NAME=rezervasyon_db

# Redis
REDIS_PASSWORD=ADIM_1_DEN_KOPYALA

# Diğerleri (varsayılan değerler)
JWT_ACCESS_TOKEN_EXPIRES=3600
UPLOAD_FOLDER=/app/app/static/uploads
MAX_CONTENT_LENGTH=16777216
WTF_CSRF_ENABLED=True
```

### 6️⃣ Deploy Et!

```
→ Deploy butonuna tıkla
→ Logs'u izle (5-10 dakika sürer)
```

## ✅ Kontrol Et

### Health Check
```bash
curl http://YOUR_SERVER_IP/health
```

Başarılı yanıt:
```json
{"status": "healthy"}
```

### İlk Giriş

1. Tarayıcıda aç: `http://YOUR_SERVER_IP`
2. Superadmin oluştur:
```bash
# Coolify Terminal'de
docker exec -it rezervasyon_app_prod python create_superadmin.py
```

## 🎉 Hazır!

Sistem çalışıyor! Artık:
- ✅ Rezervasyon sistemi aktif
- ✅ QR kod oluşturma çalışıyor
- ✅ Database bağlantısı var
- ✅ Redis cache aktif

## 🔧 Sorun mu var?

### Database bağlanamıyor
```bash
# PostgreSQL çalışıyor mu?
docker ps | grep postgres

# Logs kontrol et
docker logs rezervasyon_db_prod
```

### Redis bağlanamıyor
```bash
# Redis çalışıyor mu?
docker ps | grep redis

# Logs kontrol et
docker logs rezervasyon_redis_prod
```

### App başlamıyor
```bash
# App logs
docker logs rezervasyon_app_prod

# Tüm servisler
docker-compose -f docker-compose.prod.yml logs
```

## 📚 Detaylı Bilgi

Daha fazla bilgi için:
- `COOLIFY_DEPLOYMENT.md` - Detaylı deployment rehberi
- `TROUBLESHOOTING.md` - Sorun giderme
- `DOCKER_SORUN_GIDERME.md` - Docker sorunları

---

**Başarılar Erkan! 🚀**
