FROM python:3.11-slim

# Metadata
LABEL maintainer="Rezervasyon Sistemi"
LABEL description="Flask Rezervasyon Yönetim Sistemi"
LABEL version="1.0"

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Upload klasörlerini oluştur
RUN mkdir -p /app/app/static/uploads/qr && \
    mkdir -p /app/app/static/uploads/logos && \
    chmod -R 755 /app/app/static/uploads

# Port tanımla
EXPOSE 5000

# start.sh'ı executable yap
RUN chmod +x /app/start.sh

# Health check ekle
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/ || exit 1

# Uygulamayı başlat (Railway'de start.sh kullan)
CMD ["bash", "/app/start.sh"]
