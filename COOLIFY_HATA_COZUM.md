# 🔧 Coolify Healthcheck Hatası - ÇÖZÜLDÜ!

## ❌ Sorun

Coolify deployment sırasında şu hata alındı:
```
Failed to connect to localhost port 3000
```

## 🔍 Sebep

1. Coolify default olarak port 3000'i kontrol ediyor
2. Bizim uygulama port 5000'de çalışıyor
3. Nginx port 80'de çalışıyor

## ✅ Çözüm

### Yapılan Değişiklikler:

1. **`.coolify` dosyası silindi** - Yanlış port kullanıyordu
2. **`docker-compose.coolify.yml` oluşturuldu** - Coolify'a özel
3. **`nginx/nginx.coolify.conf` oluşturuldu** - Basitleştirilmiş nginx config

### Yeni Dosyalar:

- ✅ `docker-compose.coolify.yml` - Coolify için optimize edilmiş
- ✅ `nginx/nginx.coolify.conf` - Coolify için nginx config
- ✅ Bu dosya - Sorun giderme rehberi

## 🚀 Coolify'da Yeniden Deploy

### 1. Mevcut Deployment'ı Durdur (Varsa)
```
Coolify Dashboard → Projen → Stop
```

### 2. Ayarları Güncelle
```
Coolify Dashboard → Projen → Settings
- Docker Compose File: docker-compose.coolify.yml
→ Save
```

### 3. Yeniden Deploy Et
```
→ Deploy butonuna tıkla
→ Logs'u izle
```

## 📊 Healthcheck Kontrolü

### App Container
```bash
docker exec rezervasyon_app curl -f http://localhost:5000/health
```

Başarılı yanıt:
```json
{"status": "healthy", "database": "connected", "redis": "connected"}
```

### Nginx Container
```bash
docker exec rezervasyon_nginx wget -q -O- http://localhost/health
```

Başarılı yanıt:
```json
{"status": "healthy", "database": "connected", "redis": "connected"}
```

## 🎯 Yeni Mimari

```
Internet
   ↓
Coolify (Port 80)
   ↓
Nginx Container (Port 80)
   ↓
Flask App Container (Port 5000)
   ↓
PostgreSQL (Coolify Servisi)
   ↓
Redis (Coolify Servisi)
```

## ✅ Kontrol Listesi

Deployment başarılı olması için:

- [ ] PostgreSQL servisi "Running"
- [ ] Redis servisi "Running"
- [ ] App container "Running"
- [ ] Nginx container "Running"
- [ ] Healthcheck "healthy"
- [ ] Port 80 erişilebilir
- [ ] `/health` endpoint çalışıyor

## 🔍 Logs Kontrolü

### Tüm Container'ları Göster
```bash
docker ps
```

Görmek istediğin:
```
rezervasyon_app      Up (healthy)
rezervasyon_nginx    Up (healthy)
```

### App Logs
```bash
docker logs -f rezervasyon_app
```

Görmek istediğin:
```
✅ Database is ready and accepting connections!
✅ Migrations completed successfully!
🌐 Starting Gunicorn server...
[INFO] Booting worker with pid: ...
```

### Nginx Logs
```bash
docker logs -f rezervasyon_nginx
```

## 🆘 Hala Sorun Varsa

### 1. Environment Variables Kontrol
```bash
docker exec rezervasyon_app env | grep -E "DATABASE_URL|REDIS_URL|SECRET_KEY"
```

Hepsinin dolu olması gerekli!

### 2. Database Bağlantısı Test
```bash
docker exec rezervasyon_app python -c "
from app import create_app
app = create_app()
with app.app_context():
    from app import db
    print('Database:', db.engine.url)
    db.session.execute('SELECT 1')
    print('✅ Database OK!')
"
```

### 3. Redis Bağlantısı Test
```bash
docker exec rezervasyon_app python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
r.ping()
print('✅ Redis OK!')
"
```

## 📝 Notlar

### PostgreSQL ve Redis Coolify'da Ayrı Servisler

`docker-compose.coolify.yml` dosyasında PostgreSQL ve Redis tanımı YOK çünkü:
- Coolify'da ayrı servisler olarak ekliyoruz
- Internal network üzerinden bağlanıyorlar
- DATABASE_URL ve REDIS_URL environment variables ile bağlantı sağlanıyor

### Port Mapping

- **80** → Nginx (public)
- **5000** → Flask App (internal)
- PostgreSQL ve Redis → Internal network (port expose yok)

## 🎉 Başarılı Deployment

Şunları görüyorsan başarılı:

```bash
curl http://YOUR_SERVER_IP/health
```

Yanıt:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

Ve ana sayfa açılıyor:
```bash
curl http://YOUR_SERVER_IP/
```

HTML yanıt alıyorsan → ✅ BAŞARILI!

---

**Sorun çözüldü! Yeniden deploy et! 🚀**
