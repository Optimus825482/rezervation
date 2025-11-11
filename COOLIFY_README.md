# 🚀 Coolify Deployment - Rezervasyon Sistemi

## 📦 Hazırlanan Dosyalar

Coolify'a deployment için tüm gerekli dosyalar hazır:

### 📄 Dokümantasyon
- **COOLIFY_QUICKSTART.md** - 5 dakikada deploy et (başla buradan!)
- **COOLIFY_DEPLOYMENT.md** - Detaylı deployment rehberi
- **COOLIFY_CHECKLIST.md** - Adım adım kontrol listesi
- **COOLIFY_README.md** - Bu dosya

### ⚙️ Konfigürasyon Dosyaları
- **.coolify** - Coolify otomatik tanıma dosyası
- **.env.coolify** - Environment variables template
- **coolify-setup.sh** - Otomatik şifre oluşturma scripti
- **docker-compose.prod.yml** - Production Docker Compose (zaten vardı)
- **Dockerfile.prod** - Production Dockerfile (zaten vardı)

## 🎯 Hızlı Başlangıç

### 1. Şifreleri Oluştur
```bash
bash coolify-setup.sh
```

Bu komut:
- ✅ Güçlü SECRET_KEY oluşturur
- ✅ Güçlü JWT_SECRET_KEY oluşturur
- ✅ Güçlü DB_PASSWORD oluşturur
- ✅ Güçlü REDIS_PASSWORD oluşturur
- ✅ `.env.coolify.generated` dosyası oluşturur

### 2. Coolify'da Kurulum

#### PostgreSQL Ekle
```
Dashboard → New Resource → Database → PostgreSQL
- Name: rezervasyon-db
- Username: postgres
- Password: (coolify-setup.sh'den kopyala)
- Database: rezervasyon_db
```

#### Redis Ekle
```
Dashboard → New Resource → Database → Redis
- Name: rezervasyon-redis
- Password: (coolify-setup.sh'den kopyala)
```

#### Projeyi Ekle
```
Dashboard → New Resource → Public Repository
- Repository: https://github.com/Optimus825482/rezervation.git
- Branch: main
- Build Pack: Docker Compose
- Docker Compose File: docker-compose.prod.yml
```

#### Environment Variables
`.env.coolify.generated` dosyasındaki tüm değişkenleri Coolify'a kopyala

#### Deploy
"Deploy" butonuna tıkla ve logs'u izle!

## 📚 Detaylı Rehberler

### Yeni Başlıyorsan
👉 **COOLIFY_QUICKSTART.md** - 5 dakikada deploy et

### Detaylı Bilgi İstiyorsan
👉 **COOLIFY_DEPLOYMENT.md** - Her şey burada

### Adım Adım İlerlemek İstiyorsan
👉 **COOLIFY_CHECKLIST.md** - Hiçbir şeyi atlama

## 🔧 Sistem Gereksinimleri

### Minimum
- 2GB RAM
- 20GB Disk
- 2 CPU Core

### Önerilen
- 4GB RAM
- 50GB Disk
- 4 CPU Core

## 🎯 Özellikler

### Hazır Gelen
- ✅ Docker Compose production yapılandırması
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Nginx reverse proxy
- ✅ SSL/TLS desteği
- ✅ Otomatik migrations
- ✅ Health check endpoint
- ✅ Güvenlik önlemleri
- ✅ Resource limits
- ✅ Persistent volumes

### Güvenlik
- ✅ HTTPS zorunlu
- ✅ Secure cookies
- ✅ CSRF protection
- ✅ Rate limiting
- ✅ SQL injection koruması
- ✅ XSS koruması
- ✅ Güçlü şifreleme

## 🔍 Health Check

Deployment sonrası kontrol:
```bash
curl http://YOUR_SERVER_IP/health
```

Başarılı yanıt:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

## 👤 İlk Kullanıcı Oluşturma

```bash
# Coolify Terminal'de
docker exec -it rezervasyon_app_prod python create_superadmin.py
```

## 🔄 Güncelleme

### Otomatik (Önerilen)
GitHub'a push yap, Coolify otomatik deploy eder (webhook kuruluysa)

### Manuel
Coolify Dashboard → Projen → Deploy

## 📊 Monitoring

Coolify Dashboard'da:
- CPU kullanımı
- Memory kullanımı
- Disk kullanımı
- Network trafiği
- Container durumu
- Logs

## 🆘 Sorun Giderme

### Logs Kontrolü
```bash
# Tüm servisler
docker-compose -f docker-compose.prod.yml logs -f

# Sadece app
docker logs -f rezervasyon_app_prod

# Sadece database
docker logs -f rezervasyon_db_prod
```

### Container Durumu
```bash
docker ps
docker stats
```

### Database Backup
```bash
# Backup
docker exec rezervasyon_db_prod pg_dump -U postgres rezervasyon_db > backup.sql

# Restore
docker exec -i rezervasyon_db_prod psql -U postgres rezervasyon_db < backup.sql
```

## 📞 Destek

Sorun yaşarsan:
1. **COOLIFY_DEPLOYMENT.md** - Yaygın sorunlar bölümüne bak
2. **TROUBLESHOOTING.md** - Genel sorun giderme
3. **DOCKER_SORUN_GIDERME.md** - Docker sorunları
4. Logs'u kontrol et
5. Container durumlarını kontrol et

## 🎉 Başarı Kriterleri

Deployment başarılı sayılır:
- ✅ Tüm servisler "Running" durumda
- ✅ Health check başarılı
- ✅ Ana sayfa açılıyor
- ✅ Login çalışıyor
- ✅ Database işlemleri çalışıyor
- ✅ QR kod oluşturma çalışıyor
- ✅ Rezervasyon sistemi çalışıyor

## 📈 Sonraki Adımlar

Deployment sonrası:
1. ✅ Superadmin oluştur
2. ✅ Sistem ayarlarını yap
3. ✅ Backup stratejisi kur
4. ✅ Monitoring ayarla
5. ✅ Domain ve SSL ayarla (varsa)
6. ✅ Kullanıcı eğitimi ver

## 🔐 Güvenlik Notları

- 🔒 Şifreleri asla GitHub'a commit etme
- 🔒 `.env.coolify.generated` dosyasını `.gitignore`'a ekle
- 🔒 Düzenli olarak şifreleri değiştir
- 🔒 Backup'ları güvenli bir yerde sakla
- 🔒 Firewall ayarlarını kontrol et
- 🔒 SSL sertifikasını düzenli yenile

## 📝 Versiyon

- **Proje**: Rezervasyon Sistemi v3.0
- **Deployment**: Coolify
- **Tarih**: 11.11.2025
- **Hazırlayan**: Kiro AI (Erkan için)

---

**Hazır! Coolify'a yüklemeye başlayabilirsin! 🚀**

Sorular için: COOLIFY_DEPLOYMENT.md dosyasına bak
