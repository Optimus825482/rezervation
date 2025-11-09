# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db, limiter
from app.models import Reservation, Event
from app.utils.decorators import controller_required, admin_required

bp = Blueprint('checkin', __name__, url_prefix='/checkin')


@bp.route('/')
@login_required
@controller_required
def index():
    return render_template('checkin/index.html')


@bp.route('/scan', methods=['POST'])
@login_required
@controller_required
@limiter.limit("30 per minute")  # Max 30 QR scans per minute
def scan():
    data = request.get_json()
    code = data.get('code')
    
    reservation = Reservation.query.filter_by(
        reservation_code=code
    ).first()
    
    if reservation:
        if reservation.checked_in:
            return jsonify({'error': 'Bu rezervasyon zaten check-in yapılmış!'})
        
        reservation.checked_in = True
        reservation.checked_in_at = db.func.now()
        reservation.checked_in_by = current_user.id
        db.session.commit()
        
        return jsonify({'success': True, 'reservation': {
            'name': reservation.customer_name,
            'phone': reservation.phone,
            'seat_number': reservation.seating.seat_number if reservation.seating else 'N/A'
        }})
    
    return jsonify({'error': 'Rezervasyon bulunamadı!'})

@bp.route('/manual/<int:id>', methods=['POST'])
@login_required
@admin_required
def manual_checkin(id):
    """Manual check-in for a reservation (from admin panel)"""
    reservation = Reservation.query.get_or_404(id)
    
    if reservation.checked_in:
        flash('Bu rezervasyon zaten check-in yapılmış!', 'warning')
    else:
        reservation.checked_in = True
        reservation.checked_in_at = datetime.utcnow()
        reservation.checked_in_by = current_user.id
        db.session.commit()
        flash('Check-in başarıyla tamamlandı!', 'success')
    
    return redirect(url_for('reservation.view', id=id))
