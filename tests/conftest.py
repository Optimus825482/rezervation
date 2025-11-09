import pytest
import os
from app import create_app, db
from app.models import Company, User, Event
from datetime import datetime, timedelta

@pytest.fixture
def app():
    # Set testing environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Create test company
        company = Company(
            name='Test Company',
            email='test@example.com',
            phone='05001234567'
        )
        db.session.add(company)
        db.session.commit()
        
        # Create test admin user
        admin = User(
            username='admin',
            email='admin@test.com',
            company_id=company.id,
            role='admin'
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        
        # Create test controller user
        controller = User(
            username='controller',
            email='controller@test.com',
            company_id=company.id,
            role='controller'
        )
        controller.set_password('Controller123!')
        db.session.add(controller)
        
        # Create test event
        event = Event(
            name='Test Event',
            event_date=(datetime.now() + timedelta(days=7)).date(),
            company_id=company.id
        )
        db.session.add(event)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Client with authenticated controller user"""
    client.post('/auth/login', data={
        'username': 'controller',
        'password': 'Controller123!'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client):
    """Client with authenticated admin user"""
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'Admin123!'
    }, follow_redirects=True)
    return client
