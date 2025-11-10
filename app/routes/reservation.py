from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from marshmallow import ValidationError
from app import db
from app.models import Reservation, Event, EventSeating
from app.utils.decorators import admin_required
from app.schemas.reservation_schema import ReservationSchema
from app.services.security_logger import security_logger
import uuid

bp = Blueprint('reservation', __name__)

@bp.route('/')
@login_required
@admin_required
def index():
    reservations = Reservation.query.join(Event).filter(
        Event.company_id == current_user.company_id
    ).all()
    return render_template('reservation/index.html', reservations=reservations)

@bp.route('/create/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create(event_id):
    """Create reservation with schema validation - Visual or Form based"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    # Görsel yerleşim planı varsa görsel rezervasyon sayfasını göster
    has_visual_layout = event.canvas_width and event.canvas_height
    
    if request.method == 'GET':
        if has_visual_layout:
            return render_template('reservation/create_visual.html', event=event)
        else:
            available_seatings = EventSeating.query.filter_by(
                event_id=event.id,
                status='available'
            ).all()
            return render_template('reservation/create.html', 
                                 event=event, 
                                 seatings=available_seatings)
    
    # POST request - JSON veya Form data
    if request.is_json:
        data_input = request.get_json()
    else:
        data_input = {
            'phone': request.form.get('phone'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'seating_id': request.form.get('seating_id'),
            'number_of_people': request.form.get('number_of_people', 1),
            'notes': request.form.get('notes')
        }
    
    try:
        # Validate seating availability
        seating_id = data_input.get('seating_id')
        if not seating_id:
            raise ValueError('Oturum seçilmedi')
        
        seating = EventSeating.query.filter_by(
            id=seating_id,
            event_id=event.id
        ).first()
        
        if not seating:
            raise ValueError('Geçersiz oturum')
        
        if seating.status != 'available':
            raise ValueError('Bu oturum müsait değil')
        
        # Kapasite kontrolü
        number_of_people = int(data_input.get('number_of_people', 1))
        if number_of_people > seating.seating_type.capacity:
            raise ValueError(f'Kişi sayısı oturum kapasitesini ({seating.seating_type.capacity}) aşıyor')
        
        # Rezervasyon oluştur
        reservation_code = str(uuid.uuid4())
        
        reservation = Reservation(
            event_id=event.id,
            seating_id=seating.id,
            phone=data_input['phone'],
            first_name=data_input['first_name'],
            last_name=data_input['last_name'],
            number_of_people=number_of_people,
            notes=data_input.get('notes'),
            reservation_code=reservation_code
        )
        db.session.add(reservation)
        
        # Oturum durumunu güncelle
        seating.status = 'reserved'
        
        db.session.commit()
        
        # QR kod oluştur
        try:
            reservation.generate_qr_code()
            db.session.commit()
        except Exception as e:
            print(f"QR code generation error: {e}")
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Rezervasyon başarıyla oluşturuldu',
                'reservation_id': reservation.id,
                'reservation_code': reservation.reservation_code
            })
        else:
            flash('Rezervasyon oluşturuldu.', 'success')
            return redirect(url_for('reservation.index'))
            
    except ValueError as e:
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 400
        else:
            flash(str(e), 'danger')
            return redirect(url_for('reservation.create', event_id=event_id))
    except Exception as e:
        db.session.rollback()
        print(f"Reservation creation error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'message': 'Rezervasyon oluşturulamadı'}), 500
        else:
            flash('Rezervasyon oluşturulurken hata oluştu', 'danger')
            return redirect(url_for('reservation.create', event_id=event_id))

@bp.route('/view/<int:id>')
@login_required
@admin_required
def view(id):
    """View reservation details"""
    reservation = Reservation.query.join(Event).filter(
        Reservation.id == id,
        Event.company_id == current_user.company_id
    ).first_or_404()
    
    return render_template('reservation/view.html', reservation=reservation)

@bp.route('/generate-qr/<int:id>', methods=['POST'])
@login_required
@admin_required
def generate_qr(id):
    """Generate QR code for a reservation"""
    reservation = Reservation.query.join(Event).filter(
        Reservation.id == id,
        Event.company_id == current_user.company_id
    ).first_or_404()
    
    try:
        reservation.generate_qr_code()
        db.session.commit()
        return jsonify({'success': True, 'qr_path': reservation.qr_code_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
