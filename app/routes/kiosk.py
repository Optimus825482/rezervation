from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models.reservation import Reservation
from app.models.event import Event
from flask_login import current_user

bp = Blueprint('kiosk', __name__)

@bp.route('/checkin')
def checkin():
    """Müşteri self-service check-in kiosk ekranı"""
    return render_template('kiosk/checkin.html')

@bp.route('/api/kiosk/checkin', methods=['POST'])
def api_kiosk_checkin():
    """Kiosk için check-in API"""
    data = request.get_json()
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({
            'success': False,
            'error': 'Lütfen geçerli bir rezervasyon kodu girin.'
        })
    
    # Rezervasyonu bul
    reservation = Reservation.query.filter_by(reservation_code=code).first()
    
    if not reservation:
        return jsonify({
            'success': False,
            'error': 'Rezervasyon kodu bulunamadı. Lütfen kodu kontrol edin.'
        })
    
    if reservation.status == 'cancelled':
        return jsonify({
            'success': False,
            'error': 'Bu rezervasyon iptal edilmiştir.'
        })
    
    if reservation.checked_in:
        return jsonify({
            'success': False,
            'error': 'Bu rezervasyon zaten check-in yapılmıştır.'
        })
    
    # Check-in yap
    reservation.checked_in = True
    reservation.checked_in_at = db.func.now()
    if current_user.is_authenticated:
        reservation.checked_in_by = current_user.id
    
    db.session.commit()
    
    # Başarılı response
    return jsonify({
        'success': True,
        'message': 'Rezervasyon başarıyla onaylandı!',
        'reservation': {
            'name': reservation.customer_name,
            'phone': reservation.phone,
            'seat_number': reservation.seating.seat_number if reservation.seating else 'N/A',
            'people_count': reservation.number_of_people,
            'event_name': reservation.event.name if reservation.event else 'N/A',
            'checked_in_at': reservation.checked_in_at.strftime('%H:%M') if reservation.checked_in_at else ''
        }
    })
