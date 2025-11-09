"""
Tests for QR code check-in functionality
"""
import pytest
import os
from app import db
from app.models.reservation import Reservation
from app.models.event import Event
from datetime import datetime


class TestQRCodeGeneration:
    """Test QR code generation functionality"""
    
    def test_generate_qr_code_creates_file(self, app):
        """Test that QR code file is created"""
        with app.app_context():
            # Create reservation
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Test',
                last_name='User',
                reservation_code='TEST123'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Generate QR code
            filepath = reservation.generate_qr_code()
            
            # Check file exists
            assert os.path.exists(filepath)
            assert filepath.endswith('TEST123.png')
            
            # Check database updated
            assert reservation.qr_code_path == 'uploads/qr/TEST123.png'
            
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def test_generate_qr_code_bytes(self, app):
        """Test QR code generation as bytes"""
        with app.app_context():
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Test',
                last_name='User',
                reservation_code='TEST456'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Generate QR bytes
            qr_bytes = reservation.get_qr_code_bytes()
            
            # Check bytes are not empty
            assert qr_bytes.read() != b''
            assert qr_bytes.tell() > 0


class TestQRCodeCheckIn:
    """Test QR code check-in functionality"""
    
    def test_checkin_with_valid_qr_code(self, authenticated_client, app):
        """Test check-in with valid QR code"""
        with app.app_context():
            # Create reservation
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Valid',
                last_name='QR',
                reservation_code='VALID123'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Scan QR code
            response = authenticated_client.post('/checkin/scan',
                json={'code': 'VALID123'},
                content_type='application/json'
            )
            
            data = response.get_json()
            assert response.status_code == 200
            assert data['success'] is True
            assert data['reservation']['name'] == 'Valid QR'
            
            # Verify check-in in database
            reservation = Reservation.query.filter_by(reservation_code='VALID123').first()
            assert reservation.checked_in is True
            assert reservation.checked_in_at is not None
    
    def test_checkin_with_invalid_qr_code(self, authenticated_client):
        """Test check-in with invalid QR code"""
        response = authenticated_client.post('/checkin/scan',
            json={'code': 'INVALID999'},
            content_type='application/json'
        )
        
        data = response.get_json()
        assert response.status_code == 200
        assert 'error' in data
        assert 'bulunamadı' in data['error'].lower()
    
    def test_checkin_duplicate_prevention(self, authenticated_client, app):
        """Test that duplicate check-in is prevented"""
        with app.app_context():
            # Create and check-in reservation
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Duplicate',
                last_name='Test',
                reservation_code='DUP123',
                checked_in=True,
                checked_in_at=datetime.utcnow()
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Try to check-in again
            response = authenticated_client.post('/checkin/scan',
                json={'code': 'DUP123'},
                content_type='application/json'
            )
            
            data = response.get_json()
            assert 'error' in data
            assert 'zaten' in data['error'].lower()


class TestQRCodeDisplay:
    """Test QR code display in UI"""
    
    def test_reservation_view_shows_qr_code(self, admin_client, app):
        """Test that reservation view page shows QR code"""
        with app.app_context():
            # Create reservation with QR code
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Display',
                last_name='Test',
                reservation_code='DISPLAY123',
                qr_code_path='uploads/qr/DISPLAY123.png'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # View reservation page
            response = admin_client.get(f'/reservation/view/{reservation.id}')
            
            assert response.status_code == 200
            assert b'QR Kod' in response.data
            assert b'DISPLAY123.png' in response.data
    
    def test_generate_qr_endpoint(self, admin_client, app):
        """Test manual QR generation endpoint"""
        with app.app_context():
            # Create reservation without QR
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Manual',
                last_name='QR',
                reservation_code='MANUAL123'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Generate QR via endpoint
            response = admin_client.post(f'/reservation/generate-qr/{reservation.id}')
            
            data = response.get_json()
            assert response.status_code == 200
            assert data['success'] is True
            assert 'qr_path' in data
            
            # Verify in database
            reservation = Reservation.query.get(reservation.id)
            assert reservation.qr_code_path is not None
            
            # Cleanup
            filepath = os.path.join('app/static', reservation.qr_code_path)
            if os.path.exists(filepath):
                os.remove(filepath)


class TestManualCheckIn:
    """Test manual check-in functionality"""
    
    def test_manual_checkin_from_admin_panel(self, admin_client, app):
        """Test manual check-in from reservation view"""
        with app.app_context():
            # Create reservation
            event = Event.query.first()
            reservation = Reservation(
                event_id=event.id,
                phone='05001234567',
                first_name='Manual',
                last_name='CheckIn',
                reservation_code='MANUAL456'
            )
            db.session.add(reservation)
            db.session.commit()
            
            # Manual check-in
            response = admin_client.post(f'/checkin/manual/{reservation.id}')
            
            # Should redirect
            assert response.status_code == 302
            
            # Verify check-in
            reservation = Reservation.query.get(reservation.id)
            assert reservation.checked_in is True
            assert reservation.checked_in_at is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
