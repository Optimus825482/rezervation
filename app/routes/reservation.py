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
    """Create reservation with schema validation"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    available_seatings = EventSeating.query.filter_by(
        event_id=event.id,
        status='available'
    ).all()
    
    if request.method == 'POST':
        schema = ReservationSchema()
        
        try:
            # Validate input data
            data = schema.load({
                'phone': request.form.get('phone'),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'seating_id': request.form.get('seating_id')
            })
        except ValidationError as err:
            # Log validation error for monitoring
            try:
                payload = {
                    'phone': request.form.get('phone'),
                    'first_name': request.form.get('first_name'),
                    'last_name': request.form.get('last_name'),
                    'seating_id': request.form.get('seating_id')
                }
                security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
            except Exception:
                pass

            for field, messages in err.messages.items():
                for message in messages:
                    flash(f'{field}: {message}', 'danger')
            return redirect(url_for('reservation.create', event_id=event_id))
        
        reservation_code = str(uuid.uuid4())
        
        reservation = Reservation(
            event_id=event.id,
            seating_id=data.get('seating_id'),
            phone=data['phone'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            reservation_code=reservation_code
        )
        db.session.add(reservation)
        
        # Update seating status
        if data.get('seating_id'):
            seating = EventSeating.query.get(data['seating_id'])
            if seating:
                seating.status = 'reserved'
        
        db.session.commit()
        
        # Generate QR code for the reservation
        try:
            reservation.generate_qr_code()
            db.session.commit()
        except Exception as e:
            # Log error but don't fail the reservation
            print(f"QR code generation error: {e}")
        
        flash('Rezervasyon oluşturuldu.', 'success')
        return redirect(url_for('reservation.index'))
    
    return render_template('reservation/create.html', 
                         event=event, 
                         seatings=available_seatings)

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
