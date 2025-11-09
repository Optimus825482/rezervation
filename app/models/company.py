from datetime import datetime
from app import db


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text)
    logo_path = db.Column(db.String(512))
    is_setup_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='company', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='company', lazy=True, cascade='all, delete-orphan')
    templates = db.relationship('SeatingLayoutTemplate', backref='company', lazy=True, cascade='all, delete-orphan')
    event_templates = db.relationship('EventTemplate', backref='company', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Company {self.name}>'
