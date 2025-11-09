#!/bin/bash
set -e

echo "🚀 Starting Railway Deployment..."

# Railway'de PostgreSQL private network üzerinden erişilebilir
# Servis başlayana kadar bekle
echo "⏳ Waiting for PostgreSQL service..."

# DATABASE_URL'den host ve port bilgisini çıkar
# Python ile parse et (daha güvenilir ve tire içeren hostname'leri destekler)
echo "   Parsing DATABASE_URL..."

DB_INFO=$(python3 -c "
import os
from urllib.parse import urlparse

database_url = os.environ.get('DATABASE_URL', '')
if not database_url:
    print('ERROR:NO_URL')
    exit(1)

try:
    url = urlparse(database_url)
    if url.hostname and url.port:
        print(f'{url.hostname}:{url.port}')
    else:
        print('ERROR:INVALID_URL')
        exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    exit(1)
" 2>&1)

if [[ "$DB_INFO" == ERROR:* ]]; then
    echo "❌ Failed to parse DATABASE_URL: $DB_INFO"
    echo "   DATABASE_URL value: ${DATABASE_URL:0:50}..."
    echo "   Please check your DATABASE_URL environment variable!"
    exit 1
fi

DB_HOST=$(echo "$DB_INFO" | cut -d: -f1)
DB_PORT=$(echo "$DB_INFO" | cut -d: -f2)

echo "   ✅ Parsed successfully"
echo "   Checking connection to $DB_HOST:$DB_PORT"

# PostgreSQL'in hazır olmasını bekle (max 60 saniye)
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # nc (netcat) ile port kontrolü - daha hızlı ve güvenilir
    if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$DB_HOST/$DB_PORT" 2>/dev/null; then
        echo "✅ PostgreSQL port is open!"
        
        # Port açık ama PostgreSQL hazır mı? Python ile kontrol et
        if python3 -c "
import sys
import psycopg2
from urllib.parse import urlparse
import os

try:
    url = urlparse(os.environ['DATABASE_URL'])
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path[1:],
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'   Connection test failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
            echo "✅ Database is ready and accepting connections!"
            break
        fi
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - Waiting for database..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ERROR: Could not connect to database after $max_attempts attempts"
    echo "DATABASE_URL: ${DATABASE_URL:0:30}..." # Sadece başını göster (güvenlik)
    echo "Please check:"
    echo "  1. PostgreSQL service is running in Railway"
    echo "  2. DATABASE_URL environment variable is correct"
    echo "  3. Private networking is enabled"
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."

# Check if alembic_version table exists
TABLE_EXISTS=$(python3 -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('yes' if 'alembic_version' in tables else 'no')
" 2>/dev/null)

if [ "$TABLE_EXISTS" = "no" ]; then
    echo "   📦 Fresh database detected, creating initial schema..."
    
    # Create all tables directly from models
    python3 -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('✅ Tables created successfully')
" || {
        echo "❌ Failed to create tables"
        exit 1
    }
    
    # Stamp the database with the latest migration
    flask db stamp head || {
        echo "⚠️  Could not stamp database"
    }
    
    echo "✅ Initial schema created!"
else
    echo "   📊 Existing database detected, running migrations..."
    flask db upgrade || {
        echo "⚠️  Migration failed, trying to fix..."
        
        # Try to stamp and upgrade again
        flask db stamp head
        flask db upgrade || {
            echo "❌ Migration failed completely"
            exit 1
        }
    }
fi

echo "✅ Database is ready!"

echo "✅ Migrations completed successfully!"

# Start the application with Gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    run:app
