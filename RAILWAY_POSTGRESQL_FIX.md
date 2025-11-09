# Railway PostgreSQL Bağlantı Sorunu - Çözüm Raporu

## 🐛 Sorun

Railway loglarında şu hata görülüyor:

```
psycopg2.OperationalError: connection to server at "rezervation.railway.internal" 
(fd12:859f:563f:1:1000:4:99ef:9ce5), port 5432 failed: Connection refused
```

## 🔍 Nedeni

1. **PostgreSQL servisi çalışmıyor** veya
2. **DATABASE_URL yanlış ayarlanmış** veya
3. **Network bağlantısı problemi var** veya
4. **PostgreSQL servisi başlatılmamış**

## ✅ Çözümler

### 1. Railway Dashboard'da Kontroller

#### PostgreSQL Servisini Kontrol Edin
1. Railway Dashboard → Services
2. PostgreSQL servisini bulun
3. Status: "Running" olmalı
4. Değilse → Settings → Restart

#### Environment Variables Kontrol
1. Settings → Variables
2. `DATABASE_URL` olmalı
3. Format: `postgresql://user:password@host:5432/dbname`
4. Otomatik ayarlanmalı: `${{Postgres.DATABASE_URL}}`

### 2. PostgreSQL Servisi Yoksa Ekleyin

```bash
# Railway CLI ile
railway add postgresql

# Veya Dashboard'dan
New → Database → PostgreSQL
```

### 3. Bağlantıyı Test Edin

```bash
# Railway CLI ile test
railway run python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.engine.connect(); print('✅ Bağlantı başarılı!')"
```

### 4. Migration Çalıştırın

Veritabanı bağlantısı çalışıyorsa:

```bash
# Migration'ları çalıştırın
railway run flask db upgrade

# Eğer ilk kez kuruluyorsa
railway run flask db init
railway run flask db migrate -m "Initial migration"
railway run flask db upgrade
```

### 5. Logs İnceleyin

```bash
# Tüm servislerin loglarını izleyin
railway logs --follow

# Sadece PostgreSQL
railway logs --service postgres
```

## 🔧 Yapılan Değişiklikler

### 1. `run.py` - Hata Yönetimi İyileştirildi

```python
# Veritabanı bağlantısı başarısız olursa uygulama crash olmaz
try:
    db.engine.connect()
    db.create_all()
except Exception as e:
    print(f"⚠️ WARNING: Database initialization failed: {e}")
    # Production'da exit yap
    if env == 'production':
        sys.exit(1)
```

### 2. `railway.json` - Deployment Yapılandırması

```json
{
  "deploy": {
    "startCommand": "flask db upgrade && gunicorn ...",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. `start.sh` - Başlangıç Scripti

```bash
# Veritabanı hazır olana kadar bekle
while [ $attempt -lt $max_attempts ]; do
    if python -c "...db.engine.connect()..." 2>/dev/null; then
        break
    fi
    sleep 2
done
```

### 4. `nixpacks.toml` - Build Yapılandırması

```toml
[start]
cmd = "flask db upgrade && gunicorn ..."
```

## 🎯 Yapılması Gerekenler

### Railway'de

1. ✅ PostgreSQL servisini ekleyin/başlatın
2. ✅ `DATABASE_URL` environment variable'ını kontrol edin
3. ✅ Redis servisini ekleyin (rate limiting için)
4. ✅ Diğer environment variable'ları ayarlayın:

```env
FLASK_ENV=production
SECRET_KEY=<güçlü-anahtar>
JWT_SECRET_KEY=<güçlü-jwt-anahtarı>
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

### Kod Tarafında

1. ✅ `run.py` güncellendi
2. ✅ `railway.json` eklendi
3. ✅ `nixpacks.toml` eklendi
4. ✅ `start.sh` eklendi
5. ✅ `README.railway.md` eklendi

## 📋 Kontrol Listesi

- [ ] Railway'de PostgreSQL servisi var ve çalışıyor
- [ ] `DATABASE_URL` environment variable doğru
- [ ] Redis servisi eklendi (opsiyonel ama önerilen)
- [ ] Kod değişiklikleri commit/push edildi
- [ ] Railway otomatik deploy başladı
- [ ] Loglar kontrol edildi - hata yok
- [ ] Migration'lar çalıştırıldı: `railway run flask db upgrade`
- [ ] Uygulama başarıyla deploy edildi
- [ ] Superadmin kullanıcısı oluşturuldu (gerekiyorsa)

## 🚀 Deployment Komutları

```bash
# 1. Kod değişikliklerini push edin
git add .
git commit -m "Railway deployment improvements"
git push

# 2. Railway'de migration çalıştırın
railway run flask db upgrade

# 3. Superadmin oluşturun (gerekiyorsa)
railway run python create_superadmin.py

# 4. Uygulamayı test edin
railway open
```

## 🔍 Debug Komutları

```bash
# Environment variables
railway variables

# Database connection test
railway run python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); print(db.engine.url)"

# PostgreSQL durumu
railway status

# Logları izle
railway logs --tail 100 --follow
```

## 📞 Yardım

Sorun devam ediyorsa:

1. **PostgreSQL logları**: Railway Dashboard → PostgreSQL → Logs
2. **Network ayarları**: Settings → Networking
3. **Service health**: Metrics → Health Checks
4. **Railway Discord**: https://discord.gg/railway

---

**Oluşturulma:** 9 Kasım 2025
**Durum:** PostgreSQL bağlantı sorunu tespit edildi, çözümler uygulandı
