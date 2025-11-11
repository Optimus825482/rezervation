#!/bin/bash
set -e

echo "🚀 Starting Railway Deployment..."
echo "=================================="

# Database bağlantısını kontrol et
echo "📊 Checking database connection..."

# PostgreSQL'in hazır olmasını bekle (max 60 saniye)
timeout=60
counter=0

while [ $counter -lt $timeout ]; do
    if python3 -c "
import os
import psycopg2
from urllib.parse import urlparse

try:
    # DATABASE_URL'i parse et
    url = urlparse(os.environ.get('DATABASE_URL', ''))
    
    # postgres:// -> postgresql:// dönüşümü
    if url.scheme == 'postgres':
        db_url = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://', 1)
    else:
        db_url = os.environ.get('DATABASE_URL', '')
    
    # Bağlantı test et
    conn = psycopg2.connect(db_url)
    conn.close()
    print('✅ Database connection successful!')
    exit(0)
except Exception as e:
    print(f'⏳ Waiting for database... ({e})')
    exit(1)
" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    fi
    
    counter=$((counter + 5))
    if [ $counter -lt $timeout ]; then
        echo "⏳ Waiting for database... ($counter/$timeout seconds)"
        sleep 5
    fi
done

if [ $counter -ge $timeout ]; then
    echo "❌ Database connection timeout!"
    echo "⚠️  Starting anyway, migrations will be attempted..."
fi

# Migrations çalıştır
echo ""
echo "📦 Running database migrations..."
if flask db upgrade; then
    echo "✅ Migrations completed successfully!"
else
    echo "⚠️  Migration failed, but continuing..."
fi

# Gunicorn ile başlat
echo ""
echo "🌐 Starting Gunicorn server..."
echo "=================================="

exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    run:app
