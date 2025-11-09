"""Reservation schema for validation."""
from marshmallow import Schema, fields, validates, ValidationError
from app.schemas import BaseSchema


class ReservationSchema(BaseSchema):
    """Schema for reservation creation and updates."""
    
    phone = fields.Str(required=True)
    first_name = fields.Str(allow_none=True, validate=lambda x: len(x) <= 100 if x else True)
    last_name = fields.Str(allow_none=True, validate=lambda x: len(x) <= 100 if x else True)
    event_id = fields.Int(required=True)
    event_seating_id = fields.Int(required=True)
    number_of_people = fields.Int(required=True, validate=lambda x: x > 0)
    notes = fields.Str(allow_none=True, validate=lambda x: len(x) <= 1000 if x else True)
    
    @validates('phone')
    def validate_phone(self, value):
        """Validate Turkish phone number."""
        self.validate_turkish_phone(value)
        return value
    
    @validates('first_name')
    def validate_first_name(self, value):
        """Validate first name - no special characters."""
        if value and not value.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError('First name can only contain letters, spaces, hyphens, and apostrophes')
        return value
    
    @validates('last_name')
    def validate_last_name(self, value):
        """Validate last name - no special characters."""
        if value and not value.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValidationError('Last name can only contain letters, spaces, hyphens, and apostrophes')
        return value
