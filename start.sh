#!/bin/bash
set -e

echo "🚀 Starting Railway Deployment..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.engine.connect()" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts - Database not ready yet..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ERROR: Could not connect to database after $max_attempts attempts"
    echo "Please check your DATABASE_URL environment variable and PostgreSQL service"
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."
flask db upgrade || {
    echo "⚠️  Migration failed, trying to initialize..."
    flask db init || echo "Database already initialized"
    flask db migrate -m "Initial migration" || echo "No changes detected"
    flask db upgrade || {
        echo "❌ Migration failed completely"
        exit 1
    }
}

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
