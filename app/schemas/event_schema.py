"""Event schema for validation."""
from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from app.schemas import BaseSchema
from datetime import datetime, date


class EventSchema(BaseSchema):
    """Schema for event creation and updates."""
    
    name = fields.Str(required=True, validate=lambda x: len(x) >= 1 and len(x) <= 255)
    description = fields.Str(allow_none=True)
    event_date = fields.Date(required=True)
    event_time = fields.Time(allow_none=True, load_default=None)  # Alias for start_time from form
    start_time = fields.Time(allow_none=True)
    end_time = fields.Time(allow_none=True)
    venue_name = fields.Str(allow_none=True, validate=lambda x: len(x) <= 255 if x else True)
    venue_type = fields.Str(allow_none=True, validate=lambda x: len(x) <= 100 if x else True)
    event_type = fields.Str(allow_none=True, validate=lambda x: len(x) <= 100 if x else True)
    venue_width = fields.Float(allow_none=True, validate=lambda x: x > 0 if x else True)
    venue_length = fields.Float(allow_none=True, validate=lambda x: x > 0 if x else True)
    stage_position = fields.Str(validate=lambda x: x in ['top', 'bottom', 'left', 'right'] if x else True)
    
    # Visual editor configuration
    canvas_width = fields.Int(allow_none=True, validate=lambda x: 400 <= x <= 2000 if x else True)
    canvas_height = fields.Int(allow_none=True, validate=lambda x: 300 <= x <= 1500 if x else True)
    grid_size = fields.Int(allow_none=True, validate=lambda x: 10 <= x <= 100 if x else True)
    
    @validates('event_date')
    def validate_event_date(self, value):
        """Validate event date is not in the past."""
        if value < date.today():
            raise ValidationError('Event date cannot be in the past')
        return value
    
    @validates_schema
    def validate_times(self, data, **kwargs):
        """Validate start time is before end time."""
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] and data['end_time']:
                if data['start_time'] >= data['end_time']:
                    raise ValidationError('Start time must be before end time', 'start_time')

class VisualSeatingConfigSchema(Schema):
    """Schema for visual seating configuration."""
    
    canvas_width = fields.Int(required=True, validate=lambda x: 400 <= x <= 2000)
    canvas_height = fields.Int(required=True, validate=lambda x: 300 <= x <= 1500)
    grid_size = fields.Int(required=True, validate=lambda x: 10 <= x <= 100)
    stage_position = fields.Str(required=True, validate=lambda x: x in ['top', 'bottom', 'left', 'right'])
    stage = fields.Dict(allow_none=True)
    seats = fields.List(fields.Dict(), required=True)
    
    @validates('seats')
    def validate_seats(self, value):
        """Validate seating configuration."""
        for i, seat in enumerate(value):
            required_fields = ['seating_type_id', 'seat_number', 'position_x', 'position_y', 'width', 'height', 'color_code']
            for field in required_fields:
                if field not in seat:
                    raise ValidationError(f'Missing field {field} in seat {i}')
            
            # Validate coordinates
            if not isinstance(seat['position_x'], (int, float)) or seat['position_x'] < 0:
                raise ValidationError(f'Invalid position_x in seat {i}')
            if not isinstance(seat['position_y'], (int, float)) or seat['position_y'] < 0:
                raise ValidationError(f'Invalid position_y in seat {i}')
            
            # Validate dimensions
            if not isinstance(seat['width'], (int, float)) or seat['width'] <= 0:
                raise ValidationError(f'Invalid width in seat {i}')
            if not isinstance(seat['height'], (int, float)) or seat['height'] <= 0:
                raise ValidationError(f'Invalid height in seat {i}')
            
            # Validate color code
            if not isinstance(seat['color_code'], str) or not seat['color_code'].startswith('#'):
                raise ValidationError(f'Invalid color_code in seat {i}')
