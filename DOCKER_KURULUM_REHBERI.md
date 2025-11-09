# Docker ile Kurulum Rehberi

Bu rehber, Rezervasyon Sistemi projesini Docker kullanarak nasıl kuracağınızı adım adım açıklar.

## 📋 Gereksinimler

### Sistem Gereksinimleri
- **Docker Desktop** 20.10+ veya Docker Engine 20.10+
- **Docker Compose** 2.0+
- **Minimum 4GB RAM** (önerilen: 8GB)
- **10GB boş disk alanı**

### İşletim Sistemi Desteği
- ✅ Windows 10/11 (Docker Desktop)
- ✅ macOS 10.15+ (Docker Desktop)
- ✅ Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)

---

## 🚀 Hızlı Başlangıç (Quick Start)

### 1. Docker Kurulumu

#### Windows & macOS:
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) indirin ve kurun
2. Docker Desktop'ı başlatın
3. Terminalde doğrulayın:
```bash
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian):
```bash
# Docker kurulumu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose kurulumu
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER
newgrp docker

# Doğrulama
docker --version
docker-compose --version
```

### 2. Projeyi İndirin

```bash
# Git ile klonlama
git clone <repository-url>
cd rezervation

# veya ZIP olarak indirip açın
```

### 3. Ortam Değişkenlerini Ayarlayın

```bash
# .env dosyası oluşturun
cp .env.example .env
```

**.env dosyasını düzenleyin:**
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
# veya
vim .env
```

**Minimum Yapılandırma (.env):**
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=gizli-anahtar-buraya-uzun-rastgele-string
DATABASE_URL=postgresql://postgres:password@db:5432/rezervasyon_db
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=jwt-gizli-anahtar-buraya
JWT_ACCESS_TOKEN_EXPIRES=3600
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
WTF_CSRF_ENABLED=True
```

**⚠️ ÖNEMLİ:** Production ortamı için güçlü şifreler kullanın!

### 4. Docker Container'ları Başlatın

```bash
# Container'ları oluştur ve başlat
docker-compose up -d

# Logları izleyin
docker-compose logs -f
```

**İlk çalıştırma süresi:** 5-10 dakika (internet hızınıza bağlı)

### 5. Veritabanını Hazırlayın

```bash
# Veritabanı migration'ları çalıştırın
docker-compose exec app flask db upgrade

# (Opsiyonel) Örnek veriler yükleyin
docker-compose exec app python seed_data.py
```

### 6. Uygulamaya Erişin

Tarayıcınızda açın:
- **Uygulama:** http://localhost:5000
- **Health Check:** http://localhost:5000/health (varsa)

---

## 📦 Docker Container'ları

Proje 3 container kullanır:

### 1. **app** - Flask Uygulaması
- **Port:** 5000
- **Base Image:** python:3.11-slim
- **Açıklama:** Ana rezervasyon sistemi

### 2. **db** - PostgreSQL Veritabanı
- **Port:** 5432
- **Image:** postgres:15
- **Açıklama:** Tüm verileri saklar
- **Volume:** `postgres_data` (kalıcı veri)

### 3. **redis** - Redis Cache
- **Port:** 6379
- **Image:** redis:7-alpine
- **Açıklama:** Session ve cache yönetimi

---

## 🛠️ Temel Komutlar

### Container Yönetimi

```bash
# Tüm servisleri başlat
docker-compose up -d

# Tüm servisleri durdur
docker-compose down

# Tüm servisleri durdur ve verileri sil
docker-compose down -v

# Servisleri yeniden başlat
docker-compose restart

# Belirli bir servisi yeniden başlat
docker-compose restart app

# Container durumunu kontrol et
docker-compose ps

# Logları görüntüle
docker-compose logs

# Belirli servisten log al
docker-compose logs app

# Canlı log takibi
docker-compose logs -f app
```

### Uygulama Komutları

```bash
# Flask shell aç
docker-compose exec app flask shell

# Python shell aç
docker-compose exec app python

# Veritabanı migration oluştur
docker-compose exec app flask db migrate -m "açıklama"

# Migration'ları uygula
docker-compose exec app flask db upgrade

# Migration'ları geri al
docker-compose exec app flask db downgrade

# Testleri çalıştır
docker-compose exec app pytest

# QR kodlarını oluştur
docker-compose exec app python generate_qr_codes.py

# Bash terminali aç
docker-compose exec app bash

# Dosya listele
docker-compose exec app ls -la
```

### Veritabanı Komutları

```bash
# PostgreSQL shell aç
docker-compose exec db psql -U postgres -d rezervasyon_db

# Veritabanı yedeği al
docker-compose exec db pg_dump -U postgres rezervasyon_db > backup.sql

# Veritabanını geri yükle
docker-compose exec -T db psql -U postgres rezervasyon_db < backup.sql

# Redis CLI aç
docker-compose exec redis redis-cli

# Redis cache temizle
docker-compose exec redis redis-cli FLUSHALL
```

---

## 🔧 Gelişmiş Yapılandırma

### Production Ortamı

**docker-compose.prod.yml** oluşturun:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: rezervasyon_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    networks:
      - backend

  redis:
    image: redis:7-alpine
    restart: always
    networks:
      - backend

  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/rezervasyon_db
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./app/static/uploads:/app/app/static/uploads
    depends_on:
      - db
      - redis
    restart: always
    networks:
      - backend
      - frontend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./app/static:/app/static:ro
    depends_on:
      - app
    restart: always
    networks:
      - frontend

volumes:
  postgres_data:

networks:
  frontend:
  backend:
```

**Dockerfile.prod** oluşturun:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Uygulama dosyaları
COPY . .

# Upload klasörünü oluştur
RUN mkdir -p /app/app/static/uploads/qr
RUN mkdir -p /app/app/static/uploads/logos

# Güvenlik için kullanıcı oluştur
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Gunicorn ile çalıştır
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "60", "run:app"]
```

**Production'da çalıştırma:**

```bash
# Production ortamı için .env.prod oluşturun
cp .env.example .env.prod

# Güçlü şifreler ayarlayın
vim .env.prod

# Production container'ları başlatın
docker-compose -f docker-compose.prod.yml up -d

# Migration'ları çalıştırın
docker-compose -f docker-compose.prod.yml exec app flask db upgrade
```

### HTTPS/SSL Yapılandırması

**nginx.conf** oluşturun:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 16M;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            alias /app/static;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**SSL sertifikası oluşturma (self-signed test için):**

```bash
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem
```

### Otomatik Yedekleme

**backup.sh** oluşturun:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_BACKUP="$BACKUP_DIR/db_backup_$DATE.sql"
UPLOADS_BACKUP="$BACKUP_DIR/uploads_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Veritabanı yedeği
echo "Veritabanı yedekleniyor..."
docker-compose exec -T db pg_dump -U postgres rezervasyon_db > $DB_BACKUP

# Upload dosyaları yedeği
echo "Upload dosyaları yedekleniyor..."
tar -czf $UPLOADS_BACKUP app/static/uploads/

# Eski yedekleri sil (30 günden eski)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Yedekleme tamamlandı!"
```

Çalıştırılabilir yapın:
```bash
chmod +x backup.sh
./backup.sh
```

**Otomatik yedekleme (crontab):**
```bash
# Crontab düzenle
crontab -e

# Her gün saat 02:00'da yedek al
0 2 * * * /path/to/backup.sh
```

---

## 🐛 Sorun Giderme

### Container Başlamıyor

```bash
# Container loglarını kontrol et
docker-compose logs app
docker-compose logs db

# Container durumunu kontrol et
docker-compose ps

# Container'ı yeniden başlat
docker-compose restart app

# Container'ı sil ve yeniden oluştur
docker-compose down
docker-compose up -d --force-recreate
```

### Veritabanı Bağlantı Hatası

```bash
# PostgreSQL çalışıyor mu?
docker-compose ps db

# PostgreSQL loglarını kontrol et
docker-compose logs db

# Veritabanına manuel bağlan
docker-compose exec db psql -U postgres -d rezervasyon_db

# Health check
docker-compose exec db pg_isready -U postgres
```

### Port Zaten Kullanımda

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Docker container port değiştirme (docker-compose.yml)
ports:
  - "5001:5000"  # 5001 portunu kullan
```

### Disk Alanı Doldu

```bash
# Kullanılmayan image'leri temizle
docker image prune -a

# Kullanılmayan volume'leri temizle
docker volume prune

# Kullanılmayan container'ları temizle
docker container prune

# Her şeyi temizle (DİKKAT: Tüm veriler silinir!)
docker system prune -a --volumes
```

### Migration Hataları

```bash
# Migration durumunu kontrol et
docker-compose exec app flask db current

# Migration history
docker-compose exec app flask db history

# Migration'ları sıfırla (DİKKAT: Veriler silinir!)
docker-compose exec app flask db downgrade base
docker-compose exec app flask db upgrade
```

### Permission (İzin) Hataları

**Linux/macOS:**
```bash
# Upload klasörü izinleri
sudo chown -R $USER:$USER app/static/uploads
chmod -R 755 app/static/uploads

# Docker socket izinleri
sudo chmod 666 /var/run/docker.sock
```

**Windows:**
- Docker Desktop → Settings → Resources → File Sharing
- Proje klasörünü paylaşıma ekleyin

### Yavaş Performans

```bash
# Resource kullanımını kontrol et
docker stats

# Container resource limitlerini ayarla (docker-compose.yml)
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          memory: 1G
```

---

## 📊 İzleme ve Loglama

### Container Logları

```bash
# Tüm loglar
docker-compose logs

# Son 100 satır
docker-compose logs --tail=100

# Son 5 dakika
docker-compose logs --since 5m

# Canlı takip
docker-compose logs -f

# Belirli servis
docker-compose logs -f app

# Zaman damgalı
docker-compose logs -t app
```

### Resource Kullanımı

```bash
# Anlık kullanım
docker stats

# Disk kullanımı
docker system df

# Detaylı bilgi
docker system df -v
```

### Health Checks

**docker-compose.yml'ye ekleyin:**

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Health status kontrol:**
```bash
docker-compose ps
```

---

## 🔐 Güvenlik

### Güvenli Şifre Oluşturma

```bash
# Python ile
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL ile
openssl rand -hex 32
```

### Docker Secrets (Production)

```bash
# Secret oluştur
echo "my-secret-password" | docker secret create db_password -

# docker-compose.yml'de kullan
services:
  db:
    secrets:
      - db_password

secrets:
  db_password:
    external: true
```

### Güvenlik Checklist

- [ ] `.env` dosyası `.gitignore`'da
- [ ] Production'da güçlü şifreler
- [ ] HTTPS/SSL yapılandırması
- [ ] Container'lar root olmayan kullanıcıyla çalışıyor
- [ ] Güvenlik güncellemeleri düzenli yapılıyor
- [ ] Loglar izleniyor
- [ ] Yedekleme sistemi kurulu
- [ ] Firewall yapılandırılmış

---

## 📚 Faydalı Kaynaklar

### Resmi Dokümantasyon
- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Redis Docker](https://hub.docker.com/_/redis)

### Komut Referansları
```bash
# Docker komutları
docker --help
docker-compose --help

# Flask komutları
docker-compose exec app flask --help

# PostgreSQL komutları
docker-compose exec db psql --help
```

---

## 🚨 Acil Durum Kurtarma

### Tüm Sistemi Sıfırlama

```bash
# 1. Container'ları durdur ve sil
docker-compose down -v

# 2. Image'leri temizle
docker rmi $(docker images -q rezervation*)

# 3. Yeniden başlat
docker-compose up -d --build

# 4. Veritabanını kurtar (eğer yedek varsa)
docker-compose exec -T db psql -U postgres rezervasyon_db < backup.sql

# 5. Migration'ları çalıştır
docker-compose exec app flask db upgrade
```

### Veritabanı Kurtarma

```bash
# Yedekten geri yükle
docker-compose exec -T db psql -U postgres rezervasyon_db < backup.sql

# Belirli bir tabloyu kurtar
docker-compose exec -T db psql -U postgres rezervasyon_db \
  -c "\COPY users FROM 'users_backup.csv' CSV HEADER"
```

---

## 📞 Destek ve Yardım

### Hata Raporlama

Hata bulduğunuzda aşağıdaki bilgileri toplayın:

```bash
# Sistem bilgisi
docker version
docker-compose version

# Container durumu
docker-compose ps

# Loglar
docker-compose logs > error-logs.txt

# Resource kullanımı
docker stats --no-stream > resource-usage.txt
```

### Sık Sorulan Sorular

**S: Docker Desktop yerine Docker Engine kullanabilir miyim?**
C: Evet, Linux'ta Docker Engine tercih edilir.

**S: Windows'ta WSL2 gerekli mi?**
C: Docker Desktop için önerilir ancak zorunlu değil.

**S: Veritabanı verileri nerede saklanıyor?**
C: Docker volume'ünde: `postgres_data`

**S: Production'da Gunicorn kullanmalı mıyım?**
C: Evet, Flask development server production için uygun değil.

**S: SSL sertifikası nasıl alırım?**
C: Let's Encrypt ile ücretsiz sertifika alabilirsiniz.

---

## 🎯 Sonraki Adımlar

1. ✅ Docker kurulumunu tamamlayın
2. ✅ Uygulamayı başlatın
3. ✅ İlk kullanıcıyı oluşturun
4. ✅ QR kod sistemini test edin
5. ✅ Yedekleme sistemini kurun
6. ✅ Production yapılandırmasını hazırlayın
7. ✅ SSL sertifikası ekleyin
8. ✅ İzleme ve loglama sistemini kurun

---

**Son Güncelleme:** 7 Kasım 2025

**Versiyon:** 1.0.0

**Lisans:** [Proje Lisansı]
