from datetime import datetime, date
from enum import Enum
from app import db


class EventStatus(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class StagePosition(Enum):
    TOP = 'top'
    BOTTOM = 'bottom'
    LEFT = 'left'
    RIGHT = 'right'


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    event_template_id = db.Column(db.Integer, db.ForeignKey('event_templates.id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    venue_name = db.Column(db.String(255))
    venue_type = db.Column(db.String(100))
    event_type = db.Column(db.String(100))
    status = db.Column(db.Enum(EventStatus), default=EventStatus.DRAFT)
    venue_width = db.Column(db.Float, default=0)  # meters
    venue_length = db.Column(db.Float, default=0)  # meters
    stage_position = db.Column(db.Enum(StagePosition), default=StagePosition.TOP)
    seating_config = db.Column(db.Text)  # JSON string
    stage_config = db.Column(db.Text)  # JSON string for stage placement
    canvas_width = db.Column(db.Integer, default=800)  # Canvas width in pixels
    canvas_height = db.Column(db.Integer, default=600)  # Canvas height in pixels
    grid_size = db.Column(db.Integer, default=20)  # Grid size for visual editor
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    seatings = db.relationship('EventSeating', backref='event', lazy=True, cascade='all, delete-orphan')
    reservations = db.relationship('Reservation', backref='event', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Event {self.name}>'

    @property
    def total_capacity(self):
        """Calculate total seating capacity for the event"""
        if not self.seatings:
            return 0
        return sum(seating.seating_type.capacity for seating in self.seatings)
