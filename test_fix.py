#!/usr/bin/env python3
import os
from app import create_app, db
from app.models.reservation import Reservation
from app.models.event import Event
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        print('Testing the reservation query that was failing...')
        
        # This is the query that was failing from the error traceback
        result = db.session.query(Reservation).join(Event).filter(Event.company_id == 1).all()
        
        print(f'Successfully queried {len(result)} reservations')
        print('First reservation details:')
        if result:
            first_res = result[0]
            print(f'  ID: {first_res.id}')
            print(f'  Number of people: {first_res.number_of_people}')
            print(f'  Reservation code: {first_res.reservation_code}')
        else:
            print('  No reservations found')
            
        print('✅ Fix successful! The number_of_people column is now working.')
        
    except Exception as e:
        print(f'❌ Error still exists: {e}')
        raise
