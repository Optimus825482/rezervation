from datetime import datetime
from enum import Enum
import os
import qrcode
from io import BytesIO
from app import db


class ReservationStatus(Enum):
    ACTIVE = 'active'
    CANCELLED = 'cancelled'


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    seating_id = db.Column(db.Integer, db.ForeignKey('event_seatings.id'))
    phone = db.Column(db.String(20), nullable=False)  # Mandatory
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    reservation_code = db.Column(db.String(100), unique=True, nullable=False)
    qr_code_path = db.Column(db.String(512))
    number_of_people = db.Column(db.Integer, default=1)  # Kişi sayısı eklendi
    status = db.Column(db.Enum(ReservationStatus), default=ReservationStatus.ACTIVE)
    checked_in = db.Column(db.Boolean, default=False)
    checked_in_at = db.Column(db.DateTime)
    checked_in_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    cancelled_at = db.Column(db.DateTime)  # İptal tarihi eklendi
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # İptal eden kullanıcı eklendi
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Reservation {self.reservation_code}>'

    @property
    def customer_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return "İsimsiz"

    def generate_qr_code(self, save_path='app/static/uploads/qr'):
        """Generate QR code for this reservation"""
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.reservation_code)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        filename = f"{self.reservation_code}.png"
        filepath = os.path.join(save_path, filename)
        
        with open(filepath, 'wb') as f:
            img.save(f)
        
        # Update database path (relative path for web access)
        self.qr_code_path = f"uploads/qr/{filename}"
        
        return filepath
    
    def get_qr_code_bytes(self):
        """Get QR code as bytes (for email attachments)"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.reservation_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_bytes = BytesIO()
        img.save(img_bytes)
        img_bytes.seek(0)
        
        return img_bytes


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    action = db.Column(db.String(255), nullable=False)  # created_event, made_reservation, checked_in, etc.
    details = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityLog {self.action}>'
