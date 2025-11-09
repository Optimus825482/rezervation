from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.utils.validators import validate_password_strength


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='controller')  # admin or controller
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    checkins = db.relationship('Reservation', foreign_keys='Reservation.checked_in_by', lazy=True)

    def set_password(self, password):
        """
        Set user password with strength validation.
        
        Args:
            password: Plain text password
            
        Raises:
            ValueError: If password does not meet security requirements
        """
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            raise ValueError(message)
        
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_controller(self):
        return self.role == 'controller'

    def __repr__(self):
        return f'<User {self.username}>'
