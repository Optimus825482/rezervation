from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from marshmallow import ValidationError
from app import db
from app.models import Event, EventSeating, SeatingType
from app.models.event import StagePosition, EventStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.seating import SeatingLayoutTemplate
from app.utils.decorators import admin_required
from app.schemas.event_schema import EventSchema
from app.services.security_logger import security_logger
import json

bp = Blueprint('event', __name__)

@bp.route('/')
@login_required
@admin_required
def index():
    events = Event.query.filter_by(company_id=current_user.company_id).all()
    return render_template('event/index.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create event with schema validation"""
    if request.method == 'POST':
        schema = EventSchema()
        
        try:
            # Validate input data
            data = schema.load({
                'name': request.form.get('name'),
                'event_date': request.form.get('event_date'),
                'event_time': request.form.get('event_time'),
                'event_type': request.form.get('event_type'),
                'venue_name': request.form.get('venue_name')
            })
        except ValidationError as err:
            # Log validation error for monitoring
            try:
                payload = {
                    'name': request.form.get('name'),
                    'event_date': request.form.get('event_date')
                }
                security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
            except Exception:
                pass

            for field, messages in err.messages.items():
                for message in messages:
                    flash(f'{field}: {message}', 'danger')
            return redirect(url_for('event.create'))
        
        event = Event(
            company_id=current_user.company_id,
            name=data['name'],
            event_date=data['event_date'],
            start_time=data.get('event_time'),
            event_type=data.get('event_type'),
            venue_name=data.get('venue_name'),
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        flash('Etkinlik oluşturuldu.', 'success')
        return redirect(url_for('event.edit', event_id=event.id))
    
    return render_template('event/create.html')

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(event_id):
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    seatings = EventSeating.query.filter_by(event_id=event.id).all()
    seating_types = SeatingType.query.all()
    
    if request.method == 'POST':
        # Handle status changes and general updates
        try:
            # Update basic information
            event.name = request.form.get('name', event.name)
            event.description = request.form.get('description', event.description)
            event.event_date = datetime.strptime(request.form.get('event_date'), '%Y-%m-%d').date() if request.form.get('event_date') else event.event_date
            event.start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time() if request.form.get('start_time') else None
            event.end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time() if request.form.get('end_time') else None
            event.venue_name = request.form.get('venue_name', event.venue_name)
            event.venue_type = request.form.get('venue_type', event.venue_type)
            event.event_type = request.form.get('event_type', event.event_type)
            
            # Safely convert venue dimensions (handle empty strings)
            venue_width_str = request.form.get('venue_width', '').strip()
            venue_length_str = request.form.get('venue_length', '').strip()
            event.venue_width = float(venue_width_str) if venue_width_str else (event.venue_width or 0)
            event.venue_length = float(venue_length_str) if venue_length_str else (event.venue_length or 0)
            
            # Stage position - convert string to Enum
            stage_pos_str = request.form.get('stage_position')
            if stage_pos_str:
                try:
                    event.stage_position = StagePosition(stage_pos_str)
                except ValueError:
                    # Keep existing value if invalid
                    pass
            
            # Handle status change - convert string to Enum
            new_status = request.form.get('status')
            if new_status and new_status in ['draft', 'active', 'completed', 'cancelled']:
                old_status = event.status
                try:
                    event.status = EventStatus(new_status.upper())
                except ValueError:
                    event.status = EventStatus.DRAFT
                
                # If cancelling event, also cancel all active reservations
                if new_status == 'cancelled' and old_status != 'cancelled':
                    active_reservations = Reservation.query.filter_by(
                        event_id=event.id,
                        status=ReservationStatus.ACTIVE
                    ).all()
                    
                    for reservation in active_reservations:
                        reservation.status = ReservationStatus.CANCELLED
                        db.session.add(reservation)
            
            db.session.commit()
            flash('Etkinlik başarıyla güncellendi.', 'success')
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Geçersiz veri formatı: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Güncelleme sırasında hata oluştu: {str(e)}', 'danger')
    
    return render_template('event/edit.html', 
                         event=event, 
                         seatings=seatings, 
                         seating_types=seating_types)

@bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel(event_id):
    """Cancel an event and all its active reservations"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    if event.status == 'cancelled':
        flash('Bu etkinlik zaten iptal edilmiş.', 'warning')
        return redirect(url_for('event.edit', event_id=event.id))
    
    try:
        # Cancel the event
        event.status = 'cancelled'
        
        # Cancel all active reservations
        active_reservations = Reservation.query.filter_by(
            event_id=event.id,
            status=ReservationStatus.ACTIVE
        ).all()
        
        cancelled_count = 0
        for reservation in active_reservations:
            reservation.status = ReservationStatus.CANCELLED
            db.session.add(reservation)
            cancelled_count += 1
        
        db.session.commit()
        flash(f'Etkinlik iptal edildi. {cancelled_count} aktif rezervasyon da iptal edildi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'İptal işlemi sırasında hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('event.edit', event_id=event.id))

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(event_id):
    """Delete an event (only if no reservations exist)"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    # Check if event has any reservations
    reservation_count = Reservation.query.filter_by(event_id=event.id).count()
    
    if reservation_count > 0:
        flash('Bu etkinliğe ait rezervasyonlar bulunduğu için silinemez. Önce rezervasyonları iptal edin.', 'danger')
        return redirect(url_for('event.edit', event_id=event.id))
    
    try:
        # Delete the event (cascading will delete seatings)
        db.session.delete(event)
        db.session.commit()
        flash('Etkinlik başarıyla silindi.', 'success')
        return redirect(url_for('event.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Silme işlemi sırasında hata oluştu: {str(e)}', 'danger')
        return redirect(url_for('event.edit', event_id=event.id))

@bp.route('/<int:event_id>/add-seating', methods=['POST'])
@login_required
@admin_required
def add_seating(event_id):
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    data = request.get_json()
    
    seating = EventSeating(
        event_id=event.id,
        seating_type_id=data['seating_type_id'],
        seat_number=data['seat_number'],
        position_x=data['position_x'],
        position_y=data['position_y']
    )
    db.session.add(seating)
    db.session.commit()
    
    return jsonify({'success': True, 'seating_id': seating.id})

@bp.route('/<int:event_id>/save-layout', methods=['POST'])
@login_required
@admin_required
def save_layout(event_id):
    """Save complete venue layout (stage + seats) - Enhanced for visual editor"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    data = request.get_json()
    print(f"🔍 save_layout called for event {event_id}")
    print(f"📥 Received data: {data}")
    
    try:
        # Delete existing seatings
        deleted_count = EventSeating.query.filter_by(event_id=event.id).delete()
        print(f"🗑️ Deleted {deleted_count} existing seatings")
        
        # Save stage configuration
        if data.get('stage'):
            event.stage_config = json.dumps(data['stage'])
            print(f"🎭 Stage config saved")
        
        # Save stage position (convert string to Enum)
        stage_pos = data.get('stage_position', 'top')
        if isinstance(stage_pos, str):
            event.stage_position = StagePosition(stage_pos)
        else:
            event.stage_position = stage_pos
        print(f"📍 Stage position: {event.stage_position.value if event.stage_position else 'None'}")
        
        # Save canvas dimensions and grid settings
        event.canvas_width = data.get('canvas_width', 800)
        event.canvas_height = data.get('canvas_height', 600)
        event.grid_size = data.get('grid_size', 20)
        print(f"📐 Canvas: {event.canvas_width}x{event.canvas_height}, Grid: {event.grid_size}")
        
        # Save enhanced seatings with visual editor properties
        seats_data = data.get('seats', [])
        print(f"💺 Saving {len(seats_data)} seatings")
        
        for idx, seat_data in enumerate(seats_data):
            print(f"  {idx+1}. {seat_data.get('seat_number')}: type_id={seat_data.get('seating_type_id')}, pos=({seat_data.get('position_x')}, {seat_data.get('position_y')})")
            seating = EventSeating(
                event_id=event.id,
                seating_type_id=seat_data['seating_type_id'],
                seat_number=seat_data['seat_number'],
                position_x=seat_data['position_x'],
                position_y=seat_data['position_y'],
                width=seat_data.get('width', 60),
                height=seat_data.get('height', 40),
                color_code=seat_data.get('color_code', '#3498db')
            )
            db.session.add(seating)
        
        db.session.commit()
        print(f"✅ Layout saved successfully!")
        return jsonify({'success': True, 'message': 'Görsel yerleşim planı kaydedildi'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error saving layout: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:event_id>/seating-config', methods=['GET', 'POST'])
@login_required
@admin_required
def seating_config(event_id):
    """Get or save visual seating configuration"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    if request.method == 'GET':
        # Return current configuration
        seatings = EventSeating.query.filter_by(event_id=event.id).all()
        seating_types = SeatingType.query.all()
        
        return jsonify({
            'success': True,
            'data': {
                'canvas': {
                    'width': event.canvas_width or 800,
                    'height': event.canvas_height or 600,
                    'grid_size': event.grid_size or 20
                },
                'stage': {
                    'position': event.stage_position.value if event.stage_position else 'top',
                    'config': json.loads(event.stage_config) if event.stage_config else {}
                },
                'seatings': [{
                    'id': s.id,
                    'seating_type_id': s.seating_type_id,
                    'seat_number': s.seat_number,
                    'position_x': s.position_x,
                    'position_y': s.position_y,
                    'width': s.width or 60,
                    'height': s.height or 40,
                    'capacity': s.seating_type.capacity if s.seating_type else 4,
                    'color_code': s.color_code or '#3498db',
                    'icon': s.seating_type.icon if s.seating_type else '🪑',
                    'name': s.seating_type.name if s.seating_type else f'Masa {s.seat_number}'
                } for s in seatings],
                'seating_types': [{
                    'id': st.id,
                    'name': st.name,
                    'seat_type': st.seat_type,
                    'capacity': st.capacity,
                    'icon': st.icon,
                    'color_code': st.color_code
                } for st in seating_types]
            }
        })
    
    elif request.method == 'POST':
        # Save configuration via visual editor
        result = save_layout(event_id)
        return result

@bp.route('/<int:event_id>/template/save', methods=['POST'])
@login_required
@admin_required
def save_as_template(event_id):
    """Save current seating layout as template"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    data = request.get_json()
    
    try:
        # Create template
        template = SeatingLayoutTemplate(
            company_id=current_user.company_id,
            name=data['name'],
            description=data.get('description', ''),
            category=data.get('category', 'general'),
            stage_position=event.stage_position.value if event.stage_position else 'top',
            canvas_width=event.canvas_width or 800,
            canvas_height=event.canvas_height or 600,
            grid_size=event.grid_size or 20,
            configuration=json.dumps({
                'stage_config': json.loads(event.stage_config) if event.stage_config else {},
                'seatings': [{
                    'seating_type_id': s.seating_type_id,
                    'seat_number': s.seat_number,
                    'position_x': s.position_x,
                    'position_y': s.position_y,
                    'width': s.width,
                    'height': s.height,
                    'color_code': s.color_code
                } for s in event.seatings]
            })
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Şablon başarıyla kaydedildi',
            'template_id': template.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/template/<int:template_id>/load', methods=['POST'])
@login_required
@admin_required
def load_template(template_id):
    """Load seating layout from template"""
    template = SeatingLayoutTemplate.query.filter_by(
        id=template_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    try:
        config = json.loads(template.configuration)
        
        return jsonify({
            'success': True,
            'data': {
                'stage_position': template.stage_position,
                'canvas_width': template.canvas_width,
                'canvas_height': template.canvas_height,
                'grid_size': template.grid_size,
                'stage_config': config.get('stage_config', {}),
                'seatings': config.get('seatings', [])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
