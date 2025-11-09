"""
Schema Validation Tests
Tests for Marshmallow schemas including User, Reservation, and Event schemas.
"""

import pytest
from marshmallow import Schema, fields, validates, ValidationError
from app.utils.validators import validate_password_strength, sanitize_text_input, sanitize_html


# Simplified schema definitions for testing (avoiding DB dependencies)
class TestUserSchema(Schema):
    """Simplified UserSchema for testing"""
    email = fields.Email(required=True)
    name = fields.Str(required=True)
    phone = fields.Str(required=True)
    role = fields.Str(validate=lambda x: x in ['admin', 'controller', 'user'])
    
    @validates('phone')
    def validate_phone(self, value):
        import phonenumbers
        try:
            parsed = phonenumbers.parse(value, 'TR')
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError('Geçersiz telefon numarası')
        except phonenumbers.NumberParseException:
            raise ValidationError('Geçersiz telefon numarası formatı')


class TestPasswordChangeSchema(Schema):
    """Simplified PasswordChangeSchema for testing"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)
    
    @validates('new_password')
    def validate_new_password(self, value):
        is_valid, message = validate_password_strength(value)
        if not is_valid:
            raise ValidationError(message)


class TestReservationSchema(Schema):
    """Simplified ReservationSchema for testing"""
    guest_name = fields.Str(required=True)
    guest_phone = fields.Str(required=True)
    guest_count = fields.Int(required=True, validate=lambda x: x >= 1)
    notes = fields.Str()
    
    @validates('guest_phone')
    def validate_phone(self, value):
        import phonenumbers
        try:
            parsed = phonenumbers.parse(value, 'TR')
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError('Geçersiz telefon numarası')
        except phonenumbers.NumberParseException:
            raise ValidationError('Geçersiz telefon numarası formatı')


class TestEventSchema(Schema):
    """Simplified EventSchema for testing"""
    name = fields.Str(required=True)
    description = fields.Str()
    capacity = fields.Int(required=True, validate=lambda x: x >= 1)


class TestUserSchemaValidation:
    """Test UserSchema validation"""
    
    def test_valid_user_data(self):
        """Test UserSchema with valid data"""
        schema = TestUserSchema()
        data = {
            'email': 'test@example.com',
            'name': 'John Doe',
            'phone': '+905551234567',
            'role': 'user'
        }
        result = schema.load(data)
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'John Doe'
        assert result['phone'] == '+905551234567'
        assert result['role'] == 'user'
    
    def test_invalid_email(self):
        """Test UserSchema with invalid email"""
        schema = TestUserSchema()
        data = {
            'email': 'invalid-email',
            'name': 'John Doe',
            'phone': '+905551234567'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'email' in exc_info.value.messages
    
    def test_invalid_phone(self):
        """Test UserSchema with invalid phone"""
        schema = TestUserSchema()
        data = {
            'email': 'test@example.com',
            'name': 'John Doe',
            'phone': '123'  # Too short
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'phone' in exc_info.value.messages
    
    def test_invalid_role(self):
        """Test UserSchema with invalid role"""
        schema = TestUserSchema()
        data = {
            'email': 'test@example.com',
            'name': 'John Doe',
            'phone': '+905551234567',
            'role': 'invalid_role'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'role' in exc_info.value.messages
    
    def test_missing_required_fields(self):
        """Test UserSchema with missing required fields"""
        schema = TestUserSchema()
        data = {
            'email': 'test@example.com'
            # Missing name and phone
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        errors = exc_info.value.messages
        assert 'name' in errors or 'phone' in errors


class TestPasswordChangeSchemaValidation:
    """Test PasswordChangeSchema validation"""
    
    def test_valid_password_change(self):
        """Test PasswordChangeSchema with valid data"""
        schema = TestPasswordChangeSchema()
        data = {
            'current_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'confirm_password': 'NewPass123!'
        }
        result = schema.load(data)
        assert result['current_password'] == 'OldPass123!'
        assert result['new_password'] == 'NewPass123!'
        assert result['confirm_password'] == 'NewPass123!'
    
    def test_weak_new_password(self):
        """Test PasswordChangeSchema with weak password"""
        schema = TestPasswordChangeSchema()
        data = {
            'current_password': 'OldPass123!',
            'new_password': 'weak',
            'confirm_password': 'weak'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'new_password' in exc_info.value.messages


class TestReservationSchemaValidation:
    """Test ReservationSchema validation"""
    
    def test_valid_reservation_data(self):
        """Test ReservationSchema with valid data"""
        schema = TestReservationSchema()
        data = {
            'guest_name': 'John Doe',
            'guest_phone': '+905551234567',
            'guest_count': 2,
            'notes': 'Window seat preferred'
        }
        result = schema.load(data)
        assert result['guest_name'] == 'John Doe'
        assert result['guest_phone'] == '+905551234567'
        assert result['guest_count'] == 2
        assert result['notes'] == 'Window seat preferred'
    
    def test_invalid_guest_count(self):
        """Test ReservationSchema with invalid guest count"""
        schema = TestReservationSchema()
        data = {
            'guest_name': 'John Doe',
            'guest_phone': '+905551234567',
            'guest_count': 0  # Must be at least 1
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'guest_count' in exc_info.value.messages
    
    def test_invalid_phone_format(self):
        """Test ReservationSchema with invalid phone format"""
        schema = TestReservationSchema()
        data = {
            'guest_name': 'John Doe',
            'guest_phone': 'abc',
            'guest_count': 2
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'guest_phone' in exc_info.value.messages


class TestEventSchemaValidation:
    """Test EventSchema validation"""
    
    def test_valid_event_data(self):
        """Test EventSchema with valid data"""
        schema = TestEventSchema()
        data = {
            'name': 'Annual Gala',
            'description': 'Company annual gala event',
            'capacity': 100
        }
        result = schema.load(data)
        assert result['name'] == 'Annual Gala'
        assert result['description'] == 'Company annual gala event'
        assert result['capacity'] == 100
    
    def test_invalid_capacity(self):
        """Test EventSchema with invalid capacity"""
        schema = TestEventSchema()
        data = {
            'name': 'Annual Gala',
            'description': 'Company annual gala event',
            'capacity': 0  # Must be at least 1
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'capacity' in exc_info.value.messages
    
    def test_missing_required_name(self):
        """Test EventSchema with missing required name"""
        schema = TestEventSchema()
        data = {
            'description': 'Company annual gala event',
            'capacity': 100
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'name' in exc_info.value.messages


class TestPhoneValidation:
    """Test phone number validation across schemas"""
    
    def test_turkish_mobile_format(self):
        """Test Turkish mobile phone format"""
        schema = TestReservationSchema()
        valid_phones = [
            '+905551234567',
            '+90 555 123 45 67',
            '05551234567',
            '0555 123 45 67'
        ]
        for phone in valid_phones:
            data = {
                'guest_name': 'Test User',
                'guest_phone': phone,
                'guest_count': 1
            }
            result = schema.load(data)
            assert result['guest_phone'] is not None
    
    def test_invalid_phone_formats(self):
        """Test invalid phone formats"""
        schema = TestReservationSchema()
        invalid_phones = [
            '123',
            'abcdefg',
            '+1',
            '00000000000'
        ]
        for phone in invalid_phones:
            data = {
                'guest_name': 'Test User',
                'guest_phone': phone,
                'guest_count': 1
            }
            with pytest.raises(ValidationError) as exc_info:
                schema.load(data)
            assert 'guest_phone' in exc_info.value.messages
