#!/usr/bin/env python3
import os
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print('Current database connection:', db.engine.url)
    
    # Check what tables exist
    result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
    tables = [row[0] for row in result.fetchall()]
    print('Existing tables:', tables)
    
    # Check if reservations table exists
    print('reservations table exists:', 'reservations' in tables)
    
    # Try to see if we can query the model
    from app.models.reservation import Reservation
    try:
        count = db.session.query(Reservation).count()
        print(f'Can query Reservation model: {count} records found')
    except Exception as e:
        print(f'Cannot query Reservation model: {e}')
