import pytest
from datetime import date
from app import db
from app.models import Company, User, Event, Reservation, SeatingType, EventSeating

def test_company_creation():
    """Test company model"""
    company = Company(
        name='Test Company',
        email='test@test.com',
        phone='05321234567'
    )
    assert company.name == 'Test Company'
    assert company.is_setup_complete == False

def test_user_creation():
    """Test user model"""
    user = User(
        username='testuser',
        email='test@test.com',
        role='admin'
    )
    user.set_password('Test1234!')
    assert user.check_password('Test1234!')
    assert user.is_admin == True
    assert user.is_controller == False

def test_reservation_creation():
    """Test reservation model"""
    from datetime import datetime
    reservation = Reservation(
        phone='05321234567',
        first_name='John',
        last_name='Doe',
        reservation_code='test-code-123'
    )
    assert reservation.phone == '05321234567'
    assert reservation.customer_name == 'John Doe'
