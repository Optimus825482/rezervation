"""Base schema with common validators."""
from marshmallow import Schema, ValidationError, validates_schema
from marshmallow import fields
import re


class BaseSchema(Schema):
    """Base schema class with common validators."""
    
    @staticmethod
    def validate_turkish_phone(phone: str) -> bool:
        """
        Validate Turkish phone number format: 05XX XXX XX XX
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If phone format is invalid
        """
        # Remove spaces and dashes
        clean_phone = re.sub(r'[\s\-]', '', phone)
        
        # Check format: 05XXXXXXXXX (11 digits starting with 05)
        if not re.match(r'^05\d{9}$', clean_phone):
            if not clean_phone.startswith('05'):
                raise ValidationError('Phone must start with 05')
            if len(clean_phone) != 11:
                raise ValidationError('Phone must be 11 digits')
            raise ValidationError('Invalid phone format. Use: 05XX XXX XX XX')
        
        return True
    
    @staticmethod
    def normalize_turkish_phone(phone: str) -> str:
        """
        Normalize Turkish phone number to 05XXXXXXXXX format.
        
        Args:
            phone: Phone number to normalize
            
        Returns:
            Normalized phone number
        """
        # Remove spaces and dashes
        return re.sub(r'[\s\-]', '', phone)
