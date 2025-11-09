# 🚀 Docker Hızlı Başlangıç

Rezervasyon sistemini Docker ile 5 dakikada çalıştırın!

## Adım 1: Docker Kurulumu

### Windows / macOS
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) indirin
2. Kurun ve başlatın
3. Doğrulayın:
```bash
docker --version
```

### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

## Adım 2: Projeyi Hazırlayın

```bash
# Proje dizinine gidin
cd rezervation

# Ortam değişkenlerini ayarlayın
cp .env.example .env
```

**.env dosyasını düzenleyin** (en azından SECRET_KEY değiştirin):
```env
SECRET_KEY=uzun-rastgele-gizli-anahtar-buraya
JWT_SECRET_KEY=baska-uzun-rastgele-anahtar
```

## Adım 3: Başlatın

```bash
# Container'ları başlat
docker-compose up -d

# Veritabanını hazırla
docker-compose exec app flask db upgrade

# (Opsiyonel) Test verileri yükle
docker-compose exec app python seed_data.py
```

## Adım 4: Tarayıcıda Açın

🌐 http://localhost:5000

---

## Temel Komutlar

```bash
# Container'ları durdur
docker-compose down

# Logları gör
docker-compose logs -f

# Container durumu
docker-compose ps

# Yeniden başlat
docker-compose restart
```

## Sorun mu var?

```bash
# Hata loglarını kontrol et
docker-compose logs app

# Veritabanını kontrol et
docker-compose exec db psql -U postgres -d rezervasyon_db

# Her şeyi sıfırla
docker-compose down -v
docker-compose up -d --build
```

**Detaylı bilgi için:** [DOCKER_KURULUM_REHBERI.md](DOCKER_KURULUM_REHBERI.md)
