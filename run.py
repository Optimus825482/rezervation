from app import create_app, db
from app.models import *

app = create_app('development')

with app.app_context():
    # Import all models to ensure they are registered
    from app import models
    
    # Create all tables
    db.create_all()
    
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
