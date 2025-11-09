# -*- coding: utf-8 -*-
import pytest
from app import db
from app.models import User, Company

def test_login_page(client):
    """Test login page loads"""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Giriş Yap' in response.data.decode('utf-8')

def test_user_creation(client):
    """Test user creation"""
    # Create a company first
    company = Company(
        name='Test Company',
        email='test@test.com',
        phone='05321234567'
    )
    db.session.add(company)
    db.session.flush()
    
    # Create user
    user = User(
        company_id=company.id,
        username='testuser',
        email='test@test.com',
        role='admin'
    )
    user.set_password('Test1234!')
    db.session.add(user)
    db.session.commit()
    
    assert user.check_password('Test1234!')
    assert user.is_admin
