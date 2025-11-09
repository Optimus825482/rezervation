"""User schema for validation."""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from app.schemas import BaseSchema
import re


class UserSchema(BaseSchema):
    """Schema for user registration and updates."""
    
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3 and len(x) <= 80)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    first_name = fields.Str(required=True, validate=lambda x: len(x) >= 1 and len(x) <= 50)
    last_name = fields.Str(required=True, validate=lambda x: len(x) >= 1 and len(x) <= 50)
    phone = fields.Str(allow_none=True)
    role = fields.Str(validate=lambda x: x in ['admin', 'controller'])
    
    @validates('username')
    def validate_username(self, value):
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username can only contain letters, numbers, and underscores')
        return value
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate Turkish phone number."""
        if value:
            self.validate_turkish_phone(value)
        return value
    
    @validates('password')
    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', value):
            raise ValidationError('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)')
        
        return value


class UserUpdateSchema(BaseSchema):
    """Schema for user updates (without password)."""
    
    username = fields.Str(validate=lambda x: len(x) >= 3 and len(x) <= 80)
    email = fields.Email()
    first_name = fields.Str(validate=lambda x: len(x) >= 1 and len(x) <= 50)
    last_name = fields.Str(validate=lambda x: len(x) >= 1 and len(x) <= 50)
    phone = fields.Str(allow_none=True)
    is_active = fields.Bool()
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate Turkish phone number."""
        if value:
            self.validate_turkish_phone(value)
        return value


class PasswordChangeSchema(Schema):
    """Schema for password change."""
    
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, load_only=True)
    
    @validates('new_password')
    def validate_new_password(self, value):
        """Validate new password strength."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters')
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', value):
            raise ValidationError('Password must contain at least one special character')
        
        return value
