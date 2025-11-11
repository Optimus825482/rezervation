#!/bin/bash
# Coolify Deployment Helper Script
# Erkan için hazırlandı

set -e

echo "🚀 Coolify Deployment Helper"
echo "=============================="
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Güçlü şifreler oluştur
echo "📝 Güçlü şifreler oluşturuluyor..."
echo ""

SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
REDIS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo -e "${GREEN}✅ Şifreler oluşturuldu!${NC}"
echo ""
echo "Bu değerleri Coolify'a kopyala:"
echo "================================"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
echo "DATABASE_URL=postgresql://postgres:$DB_PASSWORD@postgres:5432/rezervasyon_db"
echo "REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0"
echo ""

# .env.coolify dosyasını güncelle
echo "📄 .env.coolify dosyası güncelleniyor..."

cat > .env.coolify.generated << EOF
# Coolify Environment Variables - Otomatik Oluşturuldu
# Tarih: $(date)

# Flask Secret Keys
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

# Database
DB_USER=postgres
DB_PASSWORD=$DB_PASSWORD
DB_NAME=rezervasyon_db
DATABASE_URL=postgresql://postgres:$DB_PASSWORD@postgres:5432/rezervasyon_db

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# Flask Ayarları
FLASK_ENV=production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Upload
UPLOAD_FOLDER=/app/app/static/uploads
MAX_CONTENT_LENGTH=16777216

# Güvenlik
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
EOF

echo -e "${GREEN}✅ .env.coolify.generated dosyası oluşturuldu!${NC}"
echo ""
echo -e "${YELLOW}📋 Sonraki Adımlar:${NC}"
echo "1. Coolify'da PostgreSQL servisi ekle"
echo "2. Coolify'da Redis servisi ekle"
echo "3. .env.coolify.generated içeriğini Coolify Environment Variables'a kopyala"
echo "4. Deploy et!"
echo ""
echo -e "${GREEN}🎉 Hazır!${NC}"
