#!/usr/bin/env python3
import os
from app import create_app, db
from flask_migrate import upgrade, migrate, stamp

# Create Flask app and configure it
app = create_app()
with app.app_context():
    try:
        # Stamp current database as the head
        stamp('head')
        print('Successfully stamped database as current head')
        
        # Now run the upgrade
        upgrade()
        print('Successfully upgraded database to latest version')
        
        # Verify that number_of_people column exists
        result = db.session.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'reservations' AND column_name = 'number_of_people'")
        exists = result.fetchone() is not None
        print(f'number_of_people column exists: {exists}')
        
    except Exception as e:
        print(f'Error during migration: {e}')
        raise
