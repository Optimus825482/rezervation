#!/usr/bin/env python3
import os
from app import create_app, db
from app.models.reservation import Reservation
from sqlalchemy import text

app = create_app()
with app.app_context():
    print('Current database connection:', db.engine.url)
    print('Reservations table columns:', [c.name for c in Reservation.__table__.columns])
    result = db.session.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = "reservations"'))
    db_columns = [row[0] for row in result.fetchall()]
    print('Database columns:', db_columns)
    print('number_of_people in columns:', 'number_of_people' in db_columns)
