import os
import sys
from app import create_app, db
from app.models import *

# Determine environment
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

# Only create tables in development or if explicitly requested
if env == 'development' or os.environ.get('AUTO_CREATE_TABLES') == 'true':
    with app.app_context():
        try:
            # Import all models to ensure they are registered
            from app import models
            
            # Test database connection first
            db.engine.connect()
            print("✅ Database connection successful!")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
        except Exception as e:
            print(f"⚠️  WARNING: Database initialization failed: {str(e)}")
            print("⚠️  Application will start but database operations may fail.")
            print("⚠️  Please check your DATABASE_URL and ensure PostgreSQL is running.")
            
            # In production, we might want to exit
            if env == 'production':
                print("❌ Cannot start in production without database connection.")
                sys.exit(1)

if __name__ == '__main__':
    # Get port from environment (Railway sets PORT)
    port = int(os.environ.get('PORT', 5000))
    debug = env == 'development'
    
    print(f"🚀 Starting Flask app on port {port} (env: {env})")
    app.run(debug=debug, host='0.0.0.0', port=port)
