# ✅ Coolify Deployment Checklist

## 📋 Deployment Öncesi

### Hazırlık
- [ ] Coolify sunucusu hazır ve erişilebilir
- [ ] Domain var (opsiyonel) veya IP adresi belli
- [ ] GitHub repository erişilebilir
- [ ] En az 2GB RAM mevcut
- [ ] En az 20GB disk alanı mevcut

### Güvenlik Şifreleri
- [ ] `coolify-setup.sh` çalıştırıldı
- [ ] SECRET_KEY oluşturuldu
- [ ] JWT_SECRET_KEY oluşturuldu
- [ ] DB_PASSWORD oluşturuldu
- [ ] REDIS_PASSWORD oluşturuldu
- [ ] Şifreler güvenli bir yere kaydedildi

## 🗄️ Database Kurulumu

### PostgreSQL
- [ ] Coolify'da PostgreSQL servisi oluşturuldu
- [ ] Database name: `rezervasyon_db`
- [ ] Username: `postgres`
- [ ] Password ayarlandı
- [ ] Servis "Running" durumda
- [ ] Internal URL kopyalandı

### Redis
- [ ] Coolify'da Redis servisi oluşturuldu
- [ ] Password ayarlandı
- [ ] Servis "Running" durumda
- [ ] Internal URL kopyalandı

## 🚀 Proje Kurulumu

### Repository
- [ ] Coolify'da yeni resource oluşturuldu
- [ ] Repository URL eklendi: `https://github.com/Optimus825482/rezervation.git`
- [ ] Branch seçildi: `main`
- [ ] Build Pack: `Docker Compose`
- [ ] Docker Compose File: `docker-compose.prod.yml`

### Environment Variables
- [ ] FLASK_ENV=production
- [ ] SECRET_KEY eklendi
- [ ] JWT_SECRET_KEY eklendi
- [ ] DATABASE_URL eklendi
- [ ] REDIS_URL eklendi
- [ ] DB_USER=postgres
- [ ] DB_PASSWORD eklendi
- [ ] DB_NAME=rezervasyon_db
- [ ] REDIS_PASSWORD eklendi
- [ ] JWT_ACCESS_TOKEN_EXPIRES=3600
- [ ] UPLOAD_FOLDER=/app/app/static/uploads
- [ ] MAX_CONTENT_LENGTH=16777216
- [ ] WTF_CSRF_ENABLED=True

### Port ve Domain
- [ ] Port 80 expose edildi
- [ ] Port 443 expose edildi (HTTPS için)
- [ ] Domain eklendi (opsiyonel)
- [ ] SSL/TLS ayarlandı (domain varsa)

## 🎯 Deployment

### İlk Deploy
- [ ] "Deploy" butonuna tıklandı
- [ ] Logs açıldı ve izleniyor
- [ ] PostgreSQL bağlantısı başarılı
- [ ] Redis bağlantısı başarılı
- [ ] Migrations tamamlandı
- [ ] Gunicorn başladı
- [ ] Nginx başladı
- [ ] Tüm servisler "Running" durumda

### Health Check
- [ ] `/health` endpoint'i test edildi
- [ ] HTTP 200 yanıt alındı
- [ ] Database bağlantısı OK
- [ ] Redis bağlantısı OK

## 👤 İlk Kullanıcı

### Superadmin Oluşturma
- [ ] Container'a bağlanıldı
- [ ] `create_superadmin.py` çalıştırıldı
- [ ] Superadmin bilgileri kaydedildi
- [ ] Login test edildi

## 🔒 Güvenlik Kontrolleri

### Firewall
- [ ] Sadece 80, 443, 22 portları açık
- [ ] UFW veya iptables yapılandırıldı
- [ ] SSH key-based authentication aktif
- [ ] Root login devre dışı

### SSL/TLS
- [ ] HTTPS aktif (domain varsa)
- [ ] Let's Encrypt sertifikası alındı
- [ ] HTTP → HTTPS redirect çalışıyor
- [ ] SSL Labs test edildi (A+ hedef)

### Application Security
- [ ] CSRF protection aktif
- [ ] Secure cookies aktif
- [ ] Rate limiting çalışıyor
- [ ] SQL injection koruması var (ORM)
- [ ] XSS koruması var (Jinja2)

## 📊 Monitoring ve Backup

### Monitoring
- [ ] Coolify metrics kontrol edildi
- [ ] CPU kullanımı normal
- [ ] Memory kullanımı normal
- [ ] Disk kullanımı normal
- [ ] Log rotation ayarlandı

### Backup
- [ ] PostgreSQL otomatik backup ayarlandı
- [ ] Backup sıklığı belirlendi (günlük önerilen)
- [ ] Backup restore test edildi
- [ ] Uploads klasörü backup'a dahil

## 🔄 Otomatik Deployment

### GitHub Webhook
- [ ] Coolify webhook URL'i alındı
- [ ] GitHub'da webhook eklendi
- [ ] Push event seçildi
- [ ] Webhook test edildi
- [ ] Otomatik deploy çalışıyor

## ✅ Final Kontroller

### Fonksiyonellik
- [ ] Ana sayfa açılıyor
- [ ] Login çalışıyor
- [ ] Logout çalışıyor
- [ ] Rezervasyon oluşturma çalışıyor
- [ ] Rezervasyon listeleme çalışıyor
- [ ] QR kod oluşturma çalışıyor
- [ ] Masa düzeni çalışıyor
- [ ] Raporlar çalışıyor
- [ ] Admin paneli çalışıyor

### Performance
- [ ] Sayfa yükleme süreleri < 2 saniye
- [ ] Database query'leri optimize
- [ ] Static dosyalar cache'leniyor
- [ ] Gzip compression aktif

### Kullanıcı Deneyimi
- [ ] Mobil uyumlu
- [ ] Responsive tasarım çalışıyor
- [ ] Hata mesajları anlaşılır
- [ ] Loading indicator'lar var

## 📝 Dokümantasyon

### Ekip İçin
- [ ] Deployment süreci dokümante edildi
- [ ] Environment variables listelendi
- [ ] Backup/restore prosedürü yazıldı
- [ ] Troubleshooting rehberi hazır
- [ ] Acil durum planı var

### Kullanıcılar İçin
- [ ] Kullanım kılavuzu hazır
- [ ] Video tutorial (opsiyonel)
- [ ] SSS hazırlandı
- [ ] Destek kanalı belirlendi

## 🎉 Deployment Tamamlandı!

Tüm checklistler tamamlandıysa:
- ✅ Sistem production'da
- ✅ Güvenlik önlemleri alındı
- ✅ Monitoring aktif
- ✅ Backup stratejisi var
- ✅ Otomatik deployment çalışıyor

---

**Tarih**: _______________
**Deploy Eden**: Erkan
**Versiyon**: 3.0
**Notlar**: _______________
