# Otomatik Başlatma Rehberi

## 🎯 Genel Bakış

Uygulama artık **tek tıkla** başlatılabilir! Redis otomatik olarak kontrol edilir ve gerekirse başlatılır.

---

## 🚀 Kullanım

### Windows

```bash
# Çift tıkla veya komut satırından:
start.bat
```

### Linux / Mac

```bash
# Terminal'de:
chmod +x start.sh
./start.sh
```

### Her Platform (Python)

```bash
python start_app.py
```

---

## 📋 Başlatma Süreci

### 1. Başlangıç Ekranı

```
========================================
  Rezervasyon Sistemi Başlatıcı
========================================

Redis kullanmak istiyor musunuz?
  1. Evet - Redis ile başlat (Önerilen - Yüksek performans)
  2. Hayır - Redis olmadan başlat (Basit - Düşük kaynak)

Seçiminiz (1/2) [1]:
```

### 2. Redis Seçilirse

**Docker Kontrolü:**
```
✅ Docker kurulu
```

**Redis Kontrolü:**
```
✅ Redis zaten çalışıyor
```
veya
```
🚀 Redis başlatılıyor...
📦 Yeni Redis container oluşturuluyor...
⏳ Redis hazırlanıyor...
✅ Redis başarıyla başlatıldı!
```

**Environment Güncelleme:**
```
📝 .env dosyası oluşturuluyor...
✅ .env dosyası güncellendi
```

### 3. Flask Başlatma

```
🚀 Flask uygulaması başlatılıyor...
📍 http://localhost:5000

⚠️  Durdurmak için Ctrl+C kullanın
```

---

## 🔧 Özellikler

### Otomatik Kontroller

✅ **Python Kontrolü**
- Python kurulu mu?
- Doğru versiyon mu?

✅ **Virtual Environment**
- Venv var mı?
- Yoksa oluştur
- Bağımlılıkları yükle

✅ **Docker Kontrolü**
- Docker kurulu mu?
- Docker çalışıyor mu?

✅ **Redis Kontrolü**
- Redis container var mı?
- Çalışıyor mu?
- Yoksa oluştur ve başlat

✅ **Environment Dosyası**
- .env var mı?
- Yoksa .env.example'dan oluştur
- Redis ayarlarını güncelle

### Akıllı Fallback

Redis başlatılamazsa:
```
⚠️ Redis başlatılamadı
Redis olmadan devam etmek istiyor musunuz? (e/h) [e]:
```

- **Evet:** Filesystem session ile devam
- **Hayır:** Çıkış

---

## 📊 Senaryo Örnekleri

### Senaryo 1: İlk Kurulum

```bash
# 1. Projeyi klonla
git clone <repo-url>
cd rezervasyon-sistemi

# 2. Başlat
start.bat  # veya ./start.sh

# Script otomatik olarak:
# - Virtual environment oluşturur
# - Bağımlılıkları yükler
# - .env dosyası oluşturur
# - Redis'i başlatır (seçilirse)
# - Flask'ı başlatır
```

### Senaryo 2: Normal Kullanım

```bash
# Her gün
start.bat  # veya ./start.sh

# Script otomatik olarak:
# - Redis'i kontrol eder
# - Gerekirse başlatır
# - Flask'ı başlatır
```

### Senaryo 3: Redis Olmadan

```bash
start.bat

# Seçim: 2 (Redis olmadan)

# Script:
# - Redis'i atlar
# - Filesystem session kullanır
# - Flask'ı başlatır
```

### Senaryo 4: Docker Yok

```bash
start.bat

# Seçim: 1 (Redis ile)

# Script:
❌ Docker kurulu değil!

Docker kurulumu için:
  Windows: https://docs.docker.com/desktop/install/windows-install/

Redis olmadan devam etmek istiyor musunuz? (e/h) [e]: e

# Filesystem session ile devam eder
```

---

## 🎨 Renkli Output

Script renkli çıktı kullanır:

- 🟢 **Yeşil:** Başarılı işlemler
- 🔵 **Mavi:** Bilgi mesajları
- 🟡 **Sarı:** Uyarılar
- 🔴 **Kırmızı:** Hatalar
- 🟣 **Mor:** Başlıklar

---

## ⚙️ Yapılandırma

### start_app.py Parametreleri

Script içinde değiştirebileceğiniz ayarlar:

```python
# Redis container adı
CONTAINER_NAME = 'redis-rezervasyon'

# Redis portu
REDIS_PORT = '6379'

# Redis image
REDIS_IMAGE = 'redis:alpine'

# Timeout süreleri
DOCKER_TIMEOUT = 5
REDIS_START_TIMEOUT = 30
REDIS_READY_WAIT = 2
```

### Manuel Yapılandırma

.env dosyasını manuel düzenleyebilirsiniz:

```bash
# Redis ile
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
SESSION_TYPE=redis

# Redis olmadan
REDIS_ENABLED=false
SESSION_TYPE=filesystem
```

---

## 🐛 Sorun Giderme

### Sorun 1: Python Bulunamadı

**Windows:**
```bash
# Python PATH'e ekli mi kontrol et
python --version

# Yoksa Python'u yeniden kur ve "Add to PATH" seç
```

**Linux/Mac:**
```bash
# Python3 kur
sudo apt-get install python3  # Ubuntu/Debian
brew install python3          # macOS
```

### Sorun 2: Docker Bulunamadı

```bash
# Docker Desktop'ı indir ve kur
# Windows/Mac: https://www.docker.com/products/docker-desktop
# Linux: https://docs.docker.com/engine/install/
```

### Sorun 3: Port 6379 Kullanımda

```bash
# Hangi process kullanıyor?
netstat -ano | findstr :6379  # Windows
lsof -i :6379                 # Linux/Mac

# Redis container'ını durdur
docker stop redis-rezervasyon

# Veya farklı port kullan (start_app.py'de değiştir)
```

### Sorun 4: Permission Denied (Linux/Mac)

```bash
# Script'e execute izni ver
chmod +x start.sh
chmod +x start_app.py

# Sudo ile çalıştır (gerekirse)
sudo ./start.sh
```

### Sorun 5: Virtual Environment Hatası

```bash
# Manuel oluştur
python -m venv venv

# Aktifleştir
# Windows:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

---

## 📝 Manuel Başlatma

Script kullanmak istemezseniz:

### 1. Redis'i Manuel Başlat

```bash
docker run -d --name redis-rezervasyon -p 6379:6379 redis:alpine
```

### 2. Environment Ayarla

```bash
# .env dosyasında
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

### 3. Flask'ı Başlat

```bash
python run.py
# veya
flask run
```

---

## 🎯 Avantajlar

### Kullanıcı Dostu
- ✅ Tek tıkla başlatma
- ✅ Otomatik kurulum
- ✅ Akıllı hata yönetimi
- ✅ Renkli ve açıklayıcı mesajlar

### Esnek
- ✅ Redis ile veya olmadan
- ✅ Otomatik fallback
- ✅ Manuel override mümkün

### Güvenilir
- ✅ Tüm kontroller yapılır
- ✅ Hata durumunda alternatif
- ✅ Graceful degradation

---

## 🚀 Hızlı Başlangıç

### İlk Kez Kullanım

```bash
# 1. Projeyi aç
cd rezervasyon-sistemi

# 2. Başlat
start.bat  # Windows
./start.sh # Linux/Mac

# 3. Seçim yap
# Redis ile: 1
# Redis olmadan: 2

# 4. Tarayıcıda aç
http://localhost:5000
```

### Günlük Kullanım

```bash
# Sadece çift tıkla
start.bat

# Veya terminal'de
./start.sh
```

---

## 📊 Karşılaştırma

| Yöntem | Adım Sayısı | Hata Riski | Kullanım Kolaylığı |
|--------|-------------|------------|-------------------|
| **Manuel** | 5-7 adım | Yüksek | Zor |
| **Script** | 1 adım | Düşük | Çok Kolay |

---

## 🎉 Sonuç

Artık uygulamayı başlatmak için:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

**Hepsi bu kadar!** 🚀

Script otomatik olarak:
- ✅ Gereksinimleri kontrol eder
- ✅ Redis'i başlatır (seçilirse)
- ✅ Environment'ı yapılandırır
- ✅ Flask'ı başlatır

**Tek tıkla hazır!** 🎯
