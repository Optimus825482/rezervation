"""
Template Schemas
Marshmallow schemas for seating and event template validation
"""

from marshmallow import Schema, fields, validates, ValidationError
from app.schemas import BaseSchema
from app.utils.validators import sanitize_text_input


class SeatingTemplateSchema(BaseSchema):
    """Schema for seating layout template validation"""
    
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    category = fields.Str(required=True)
    stage_position = fields.Str(required=False, allow_none=True, load_default=None)
    configuration = fields.Str(required=False, allow_none=True, load_default='{}')
    
    @validates('name')
    def validate_name(self, value):
        """Sanitize template name"""
        if not value or not value.strip():
            raise ValidationError('Şablon adı boş olamaz')
        if len(value.strip()) > 100:
            raise ValidationError('Şablon adı çok uzun (max 100 karakter)')
    
    @validates('category')
    def validate_category(self, value):
        """Validate category"""
        valid_categories = ['wedding', 'conference', 'concert', 'theater', 'restaurant', 'classroom', 'other']
        if value not in valid_categories:
            raise ValidationError(f'Geçersiz kategori. Geçerli değerler: {", ".join(valid_categories)}')
    
    @validates('stage_position')
    def validate_stage_position(self, value):
        """Validate stage position"""
        if not value:  # Allow empty/none
            return
        valid_positions = ['top', 'bottom', 'left', 'right', 'center', 'none']
        if value not in valid_positions:
            raise ValidationError(f'Geçersiz sahne pozisyonu. Geçerli değerler: {", ".join(valid_positions)}')


class EventTemplateSchema(BaseSchema):
    """Schema for event template validation"""
    
    name = fields.Str(required=True)
    description = fields.Str()
    default_capacity = fields.Int(validate=lambda x: x > 0)
    default_duration = fields.Int(validate=lambda x: x > 0)  # in minutes
    
    @validates('name')
    def validate_name(self, value):
        """Sanitize template name"""
        if not value or not value.strip():
            raise ValidationError('Şablon adı boş olamaz')
        if len(value.strip()) > 100:
            raise ValidationError('Şablon adı çok uzun (max 100 karakter)')
    
    @validates('description')
    def validate_description(self, value):
        """Sanitize description"""
        if value and len(value) > 500:
            raise ValidationError('Açıklama çok uzun (max 500 karakter)')
