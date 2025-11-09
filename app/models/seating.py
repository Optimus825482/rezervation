from datetime import datetime
from enum import Enum
from app import db


class SeatStatus(Enum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    DISABLED = 'disabled'


class SeatingType(db.Model):
    __tablename__ = 'seating_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Masa - 4 Kişilik"
    seat_type = db.Column(db.String(50), nullable=False)  # "table" or "chair"
    capacity = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50))  # İkon alanı eklendi
    color_code = db.Column(db.String(7), default='#3498db')  # Hex color
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    seatings = db.relationship('EventSeating', backref='seating_type', lazy=True)

    def __repr__(self):
        return f'<SeatingType {self.name}>'


class EventSeating(db.Model):
    __tablename__ = 'event_seatings'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    seating_type_id = db.Column(db.Integer, db.ForeignKey('seating_types.id'), nullable=False)
    seat_number = db.Column(db.String(20), nullable=False)  # "M1", "M2", etc.
    position_x = db.Column(db.Float, nullable=False)  # Grid position
    position_y = db.Column(db.Float, nullable=False)  # Grid position
    width = db.Column(db.Float, default=60)  # Oturum genişliği
    height = db.Column(db.Float, default=40)  # Oturum yüksekliği
    color_code = db.Column(db.String(7))  # Renk kodu eklendi
    status = db.Column(db.Enum(SeatStatus), default=SeatStatus.AVAILABLE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reservations = db.relationship('Reservation', backref='seating', lazy=True)

    def __repr__(self):
        return f'<EventSeating {self.seat_number}>'


class SeatingLayoutTemplate(db.Model):
    __tablename__ = 'seating_layout_templates'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # wedding, concert, conference, etc.
    stage_position = db.Column(db.String(20), nullable=True)  # top, bottom, left, right, center, none
    canvas_width = db.Column(db.Integer, default=800)  # Canvas genişliği
    canvas_height = db.Column(db.Integer, default=600)  # Canvas yüksekliği
    grid_size = db.Column(db.Integer, default=20)  # Grid boyutu
    configuration = db.Column(db.Text, nullable=True, default='{}')  # JSON
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event_templates = db.relationship('EventTemplate', backref='seating_layout', lazy=True)

    def __repr__(self):
        return f'<SeatingLayoutTemplate {self.name}>'


class EventTemplate(db.Model):
    __tablename__ = 'event_templates'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    seating_layout_template_id = db.Column(db.Integer, db.ForeignKey('seating_layout_templates.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    default_event_type = db.Column(db.String(100))
    default_venue_type = db.Column(db.String(100))
    default_duration_hours = db.Column(db.Integer, default=4)
    default_pricing = db.Column(db.Text)  # JSON
    settings = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EventTemplate {self.name}>'
