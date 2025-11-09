#!/usr/bin/env python3
import os
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        print('Adding missing columns to reservations table...')
        
        # Add number_of_people column
        db.session.execute(text('ALTER TABLE reservations ADD COLUMN number_of_people INTEGER DEFAULT 1'))
        print('Added number_of_people column')
        
        # Add cancelled_at column
        db.session.execute(text('ALTER TABLE reservations ADD COLUMN cancelled_at TIMESTAMP'))
        print('Added cancelled_at column')
        
        # Add cancelled_by column
        db.session.execute(text('ALTER TABLE reservations ADD COLUMN cancelled_by INTEGER'))
        db.session.execute(text('ALTER TABLE reservations ADD CONSTRAINT fk_cancelled_by FOREIGN KEY (cancelled_by) REFERENCES users(id)'))
        print('Added cancelled_by column and foreign key')
        
        # Commit changes
        db.session.commit()
        print('Migration completed successfully')
        
        # Verify columns exist
        result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'reservations' AND column_name = 'number_of_people'"))
        exists = result.fetchone() is not None
        print(f'number_of_people column exists: {exists}')
        
    except Exception as e:
        print(f'Error during migration: {e}')
        db.session.rollback()
        raise
