# 🔧 Railway Deployment Sorun Giderme

## ❌ Yaygın Hatalar ve Çözümleri

### 1. Database Bağlantı Hatası

**Hata:**
```
could not translate host name "rezervation.railway.internal" to address
```

**Sebep:** PostgreSQL servisi henüz hazır değil veya DATABASE_URL yanlış

**Çözüm:**

#### A. PostgreSQL Servisini Kontrol Et
```
1. Railway Dashboard → PostgreSQL servisine tıkla
2. Status: "Running" olmalı
3. Eğer "Crashed" ise → Restart et
```

#### B. DATABASE_URL Kontrol Et
```
1. Web servisine tıkla
2. Variables sekmesi
3. DATABASE_URL var mı kontrol et
4. Yoksa → PostgreSQL servisini yeniden bağla
```

#### C. Private Networking Kontrol Et
```
1. PostgreSQL servisine tıkla
2. Settings → Networking
3. "Private Networking" aktif olmalı
```

#### D. Servisleri Yeniden Bağla
```
1. Web servisine tıkla
2. Settings → Service Variables
3. PostgreSQL'i yeniden bağla
4. Deploy et
```

### 2. Health Check 503 Hatası

**Hata:**
```
GET /health HTTP/1.1" 503
```

**Sebep:** Database bağlantısı yok, health check başarısız

**Çözüm:**
```
1. Database bağlantısını düzelt (yukarıdaki adımlar)
2. Logs'da "Database connection successful" mesajını bekle
3. Health check otomatik düzelecek
```

### 3. Migration Hatası

**Hata:**
```
Migration failed
```

**Sebep:** Database bağlantısı yok veya migration dosyaları eksik

**Çözüm:**

#### A. Database Bağlantısını Kontrol Et
```bash
# Railway Shell'de
python -c "from app import db; print(db.engine.url)"
```

#### B. Manuel Migration
```bash
# Railway Shell'de
flask db upgrade
```

#### C. Migration Dosyalarını Kontrol Et
```bash
ls -la migrations/versions/
```

### 4. Redis Bağlantı Hatası

**Hata:**
```
Redis connection failed
```

**Sebep:** Redis servisi yok veya REDIS_URL yanlış

**Çözüm:**

#### A. Redis Olmadan Çalıştır (Geçici)
```
1. Web servisi → Variables
2. Ekle: REDIS_ENABLED=false
3. Ekle: SESSION_TYPE=filesystem
4. Deploy et
```

#### B. Redis Servisi Ekle (Kalıcı)
```
1. Proje → New → Database → Add Redis
2. Redis başlayana kadar bekle
3. REDIS_URL otomatik set edilecek
4. Variables'a ekle: REDIS_ENABLED=true
5. Deploy et
```

### 5. Port Hatası

**Hata:**
```
Address already in use
```

**Sebep:** PORT environment variable yanlış

**Çözüm:**
```
Railway otomatik PORT set eder, manuel ekleme!
Eğer eklediysen → Sil ve yeniden deploy et
```

### 6. Build Hatası

**Hata:**
```
pip install failed
```

**Sebep:** requirements.txt'de sorun var

**Çözüm:**

#### A. Requirements Kontrol
```bash
# Lokal test
pip install -r requirements.txt
```

#### B. Python Versiyonu
```
1. nixpacks.toml kontrol et
2. Python version: 3.11 olmalı
```

#### C. Cache Temizle
```
1. Railway Dashboard → Settings
2. "Clear Build Cache"
3. Yeniden deploy et
```

## 🔍 Logs Analizi

### Başarılı Deployment Logları

Görmek istediğin:
```
✅ Database connection successful!
✅ Database is ready!
✅ Migrations completed successfully!
✅ Starting Gunicorn server...
[INFO] Booting worker with pid: ...
```

### Hatalı Deployment Logları

Dikkat edilecekler:
```
❌ could not translate host name
❌ Connection refused
❌ Migration failed
❌ Health check failed
```

## 🎯 Adım Adım Kontrol Listesi

### 1. PostgreSQL Servisi
- [ ] Servis oluşturuldu
- [ ] Status: "Running"
- [ ] Private networking aktif
- [ ] DATABASE_URL set edildi

### 2. Redis Servisi (Opsiyonel)
- [ ] Servis oluşturuldu
- [ ] Status: "Running"
- [ ] REDIS_URL set edildi
- [ ] REDIS_ENABLED=true

### 3. Environment Variables
- [ ] FLASK_ENV=production
- [ ] SECRET_KEY set edildi
- [ ] JWT_SECRET_KEY set edildi
- [ ] DATABASE_URL var
- [ ] REDIS_URL var (Redis kullanıyorsan)

### 4. Deployment
- [ ] Build başarılı
- [ ] Migrations tamamlandı
- [ ] Gunicorn başladı
- [ ] Health check başarılı

## 🆘 Hala Çalışmıyor?

### 1. Tüm Servisleri Restart Et
```
1. PostgreSQL → Restart
2. Redis → Restart (varsa)
3. Web servisi → Redeploy
```

### 2. Environment Variables Yeniden Yükle
```
1. Web servisi → Variables
2. Tüm değişkenleri kontrol et
3. Eksik varsa ekle
4. Deploy et
```

### 3. Fresh Start
```
1. Web servisini sil
2. Yeni web servisi oluştur
3. PostgreSQL ve Redis'i yeniden bağla
4. Environment variables ekle
5. Deploy et
```

## 📞 Railway Support

Hala sorun varsa:
1. Railway Discord: https://discord.gg/railway
2. Railway Docs: https://docs.railway.app
3. GitHub Issues: Repository'deki issues

## 🎉 Başarılı Deployment Testi

```bash
# Health check
curl https://your-app.railway.app/health

# Başarılı yanıt:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}

# Ana sayfa
curl https://your-app.railway.app/

# HTML yanıt almalısın
```

---

**Not:** Railway'de her değişiklik otomatik deploy tetikler. Sabırlı ol! 🚀
