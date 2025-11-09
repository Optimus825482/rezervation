# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event, Reservation, EventSeating
from app.services.report_service import ReportService
from app.utils.decorators import controller_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

bp = Blueprint('controller', __name__)

@bp.route('/dashboard')
@login_required
@controller_required
def dashboard():
    """Gelişmiş kontrolör dashboard'ı"""
    # Aktif etkinlikler
    active_events = Event.query.filter_by(
        company_id=current_user.company_id,
        status='active'
    ).order_by(Event.event_date).all()
    
    # Eğer aktif etkinlik varsa, istatistiklerini hesapla
    dashboard_stats = {}
    selected_event = None
    
    if active_events:
        if 'active_event_id' in session:
            selected_event = Event.query.get(session['active_event_id'])
        else:
            selected_event = active_events[0]
            session['active_event_id'] = selected_event.id
            session['active_event_name'] = selected_event.name
        
        dashboard_stats = calculate_dashboard_stats(selected_event)
    
    return render_template('controller/dashboard.html',
                         events=active_events,
                         selected_event=selected_event,
                         stats=dashboard_stats)

@bp.route('/select-event/<int:event_id>', methods=['POST'])
@login_required
@controller_required
def select_event(event_id):
    """Etkinlik seçimi"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    session['active_event_id'] = event.id
    session['active_event_name'] = event.name
    flash(f'Aktif etkinlik: {event.name}', 'success')
    return redirect(url_for('controller.dashboard'))

@bp.route('/reservations')
@login_required
@controller_required
def reservations():
    """Rezervasyon listesi ve filtreleme"""
    if 'active_event_id' not in session:
        flash('Lütfen önce bir etkinlik seçin.', 'warning')
        return redirect(url_for('controller.dashboard'))
    
    event = Event.query.get(session['active_event_id'])
    
    # Filtreleme parametreleri
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    checked_in = request.args.get('checked_in', '').strip()
    
    # Base query
    query = Reservation.query.filter_by(event_id=event.id)
    
    # Filtreler
    if search:
        query = query.filter(
            Reservation.phone.like(f'%{search}%') |
            Reservation.first_name.like(f'%{search}%') |
            Reservation.last_name.like(f'%{search}%') |
            Reservation.reservation_code.like(f'%{search}%')
        )
    
    if status:
        query = query.filter(Reservation.status == status)
    
    if checked_in:
        if checked_in == 'true':
            query = query.filter(Reservation.checked_in == True)
        elif checked_in == 'false':
            query = query.filter(Reservation.checked_in == False)
    
    reservations = query.order_by(Reservation.created_at.desc()).all()
    
    return render_template('controller/reservations.html',
                         event=event,
                         reservations=reservations,
                         search=search,
                         status=status,
                         checked_in=checked_in)

@bp.route('/api/reservations/search')
@login_required
@controller_required
def api_search_reservations():
    """AJAX rezervasyon arama"""
    if 'active_event_id' not in session:
        return jsonify({'error': 'Aktif etkinlik seçilmedi'}), 400
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'reservations': []})
    
    reservations = Reservation.query.filter(
        Reservation.event_id == session['active_event_id'],
        Reservation.status == 'active',
        (
            Reservation.phone.like(f'%{query}%') |
            Reservation.first_name.like(f'%{query}%') |
            Reservation.last_name.like(f'%{query}%') |
            Reservation.reservation_code.like(f'%{query}%')
        )
    ).limit(10).all()
    
    results = []
    for r in reservations:
        results.append({
            'id': r.id,
            'name': r.customer_name,
            'phone': r.phone,
            'seating': r.seating.seat_number if r.seating else 'N/A',
            'checked_in': r.checked_in,
            'status': r.status.value
        })
    
    return jsonify({'reservations': results})

@bp.route('/seating-map')
@login_required
@controller_required
def seating_map():
    """Görsel oturum haritası"""
    if 'active_event_id' not in session:
        flash('Lütfen önce bir etkinlik seçin.', 'warning')
        return redirect(url_for('controller.dashboard'))
    
    event = Event.query.get(session['active_event_id'])
    seatings = EventSeating.query.filter_by(event_id=event.id).all()
    
    # Oturum durumlarını hesapla
    seating_data = []
    for seating in seatings:
        status = 'available'
        reservation = None
        
        if seating.status == 'reserved':
            active_res = Reservation.query.filter_by(
                seating_id=seating.id,
                status='active'
            ).first()
            if active_res:
                status = 'reserved'
                reservation = active_res
        elif seating.status == 'disabled':
            status = 'disabled'
        
        seating_data.append({
            'id': seating.id,
            'number': seating.seat_number,
            'type': seating.seating_type.name,
            'capacity': seating.seating_type.capacity,
            'status': status,
            'position_x': seating.position_x,
            'position_y': seating.position_y,
            'color': seating.color_code or seating.seating_type.color_code,
            'reservation': {
                'name': reservation.customer_name if reservation else None,
                'phone': reservation.phone if reservation else None,
                'checked_in': reservation.checked_in if reservation else None
            } if reservation else None
        })
    
    return render_template('controller/seating_map.html',
                         event=event,
                         seatings=seating_data)

@bp.route('/api/seating-status')
@login_required
@controller_required
def api_seating_status():
    """AJAX oturum durumu güncelleme"""
    if 'active_event_id' not in session:
        return jsonify({'error': 'Aktif etkinlik seçilmedi'}), 400
    
    seating_id = request.args.get('seating_id')
    
    if not seating_id:
        return jsonify({'error': 'Oturum ID gerekli'}), 400
    
    seating = EventSeating.query.filter_by(
        id=seating_id,
        event_id=session['active_event_id']
    ).first_or_404()
    
    # Rezervasyon bilgisi
    reservation = Reservation.query.filter_by(
        seating_id=seating.id,
        status='active'
    ).first()
    
    return jsonify({
        'seating': {
            'id': seating.id,
            'number': seating.seat_number,
            'type': seating.seating_type.name,
            'status': seating.status.value,
            'capacity': seating.seating_type.capacity
        },
        'reservation': {
            'name': reservation.customer_name if reservation else None,
            'phone': reservation.phone if reservation else None,
            'checked_in': reservation.checked_in if reservation else None
        } if reservation else None
    })

@bp.route('/checkin', methods=['GET', 'POST'])
@login_required
@controller_required
def checkin():
    """Kontrolör için check-in sayfası"""
    if 'active_event_id' not in session:
        flash('Lütfen önce bir etkinlik seçin.', 'warning')
        return redirect(url_for('controller.dashboard'))
    
    event = Event.query.get(session['active_event_id'])
    
    if request.method == 'POST':
        return handle_checkin()
    
    return render_template('controller/checkin.html', event=event)

@bp.route('/api/checkin', methods=['POST'])
@login_required
@controller_required
def api_checkin():
    """AJAX check-in işlemi"""
    if 'active_event_id' not in session:
        return jsonify({'error': 'Aktif etkinlik seçilmedi'}), 400
    
    data = request.get_json()
    code = data.get('code', '').strip()
    
    if not code:
        return jsonify({'error': 'Rezervasyon kodu gerekli'}), 400
    
    reservation = Reservation.query.filter_by(
        reservation_code=code,
        event_id=session['active_event_id']
    ).first()
    
    if not reservation:
        return jsonify({'error': 'Rezervasyon bulunamadı'}), 404
    
    if reservation.checked_in:
        return jsonify({
            'error': 'Bu rezervasyon zaten check-in yapılmış!',
            'reservation': {
                'name': reservation.customer_name,
                'phone': reservation.phone,
                'seating': reservation.seating.seat_number if reservation.seating else 'N/A',
                'checked_in_at': reservation.checked_in_at.strftime('%d.%m.%Y %H:%M') if reservation.checked_in_at else None
            }
        }), 400
    
    if reservation.status != 'active':
        return jsonify({'error': 'Bu rezervasyon iptal edilmiş'}), 400
    
    # Check-in yap
    reservation.checked_in = True
    reservation.checked_in_at = datetime.utcnow()
    reservation.checked_in_by = current_user.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Check-in başarıyla tamamlandı!',
        'reservation': {
            'name': reservation.customer_name,
            'phone': reservation.phone,
            'seating': reservation.seating.seat_number if reservation.seating else 'N/A',
            'people_count': reservation.number_of_people
        }
    })

# Yardımcı fonksiyonlar

def calculate_dashboard_stats(event):
    """Dashboard istatistiklerini hesaplar"""
    try:
        # Toplam kapasite
        total_capacity = 0
        for seating in event.seatings:
            total_capacity += seating.seating_type.capacity
        
        # Rezerve edilen koltuklar
        reserved_count = 0
        for seating in event.seatings:
            if seating.status == 'reserved':
                reservation = Reservation.query.filter_by(
                    seating_id=seating.id,
                    status='active'
                ).first()
                if reservation:
                    reserved_count += reservation.number_of_people
        
        # Boş koltuklar
        empty_seats = total_capacity - reserved_count
        
        # Doluluk oranı
        occupancy_rate = (reserved_count / total_capacity * 100) if total_capacity > 0 else 0
        
        # Güncel check-in sayısı
        checked_in_count = Reservation.query.filter_by(
            event_id=event.id,
            checked_in=True
        ).count()
        
        # Son 7 günün rezervasyon trendi
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        daily_reservations = db.session.query(
            func.date(Reservation.created_at).label('date'),
            func.count(Reservation.id).label('count')
        ).filter(
            Reservation.event_id == event.id,
            Reservation.created_at >= week_ago
        ).group_by('date').order_by('date').all()
        
        trend_data = []
        for i in range(7):
            date = week_ago + timedelta(days=i)
            count = 0
            for d in daily_reservations:
                if d.date == date:
                    count = d.count
                    break
            trend_data.append({
                'date': date.strftime('%d.%m'),
                'count': count
            })
        
        return {
            'total_capacity': total_capacity,
            'reserved_seats': reserved_count,
            'empty_seats': empty_seats,
            'occupancy_rate': round(occupancy_rate, 1),
            'checked_in_count': checked_in_count,
            'total_reservations': Reservation.query.filter_by(event_id=event.id).count(),
            'daily_trend': trend_data,
            'event_date': event.event_date.strftime('%d.%m.%Y'),
            'event_name': event.name
        }
        
    except Exception as e:
        return {}

def handle_checkin():
    """Check-in işleme"""
    code = request.form.get('code', '').strip()
    
    if not code:
        return redirect(url_for('controller.checkin'))
    
    reservation = Reservation.query.filter_by(
        reservation_code=code,
        event_id=session['active_event_id']
    ).first()
    
    if not reservation:
        flash('Rezervasyon bulunamadı', 'error')
        return redirect(url_for('controller.checkin'))
    
    if reservation.checked_in:
        flash('Bu rezervasyon zaten check-in yapılmış!', 'warning')
        return render_template('controller/already_checked_in.html',
                             reservation=reservation)
    
    if reservation.status != 'active':
        flash('Bu rezervasyon iptal edilmiş', 'error')
        return redirect(url_for('controller.checkin'))
    
    # Check-in yap
    reservation.checked_in = True
    reservation.checked_in_at = datetime.utcnow()
    reservation.checked_in_by = current_user.id
    db.session.commit()
    
    return render_template('controller/checkin_success.html',
                         reservation=reservation)
