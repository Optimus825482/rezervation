from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from marshmallow import ValidationError
from sqlalchemy import func
from app import db
from app.models import (
    User,
    Company,
    Event,
    SeatingType,
    EventSeating,
    Reservation,
    ReservationStatus,
    SeatingLayoutTemplate,
    EventTemplate,
)
from app.utils.decorators import admin_required
from app.schemas.user_schema import UserSchema, PasswordChangeSchema
from app.services.security_logger import security_logger

bp = Blueprint('admin', __name__)

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    company = Company.query.get(current_user.company_id)
    
    # Temel sayılar
    users_count = User.query.filter_by(company_id=current_user.company_id).count()
    events_count = Event.query.filter_by(company_id=current_user.company_id).count()
    reservations_count = (
        db.session.query(db.func.count(Reservation.id))
        .join(Event, Reservation.event_id == Event.id)
        .filter(Event.company_id == current_user.company_id)
        .scalar()
    ) or 0
    layout_templates_count = SeatingLayoutTemplate.query.filter_by(
        company_id=current_user.company_id
    ).count()
    event_templates_count = EventTemplate.query.filter_by(
        company_id=current_user.company_id
    ).count()
    templates_count = layout_templates_count + event_templates_count

    # 🚨 KRİTİK DASHBOARD İSTATİSTİKLERİ (Yüksek Öncelik)
    
    # 1. TOPLAM KAPASİTE (Tüm etkinliklerdeki oturma kapasitesi toplamı)
    total_capacity = db.session.query(func.sum(SeatingType.capacity)).join(
        EventSeating, SeatingType.id == EventSeating.seating_type_id
    ).join(Event, EventSeating.event_id == Event.id).filter(Event.company_id == current_user.company_id).scalar() or 0

    # 2. REZERVE EDİLEN KOLTUK (Aktif rezervasyonlardaki toplam kişi sayısı)
    reserved_seats = db.session.query(func.sum(Reservation.number_of_people)).filter(
        Reservation.status == ReservationStatus.ACTIVE
    ).scalar() or 0

    # 3. BOŞ KOLTUK
    available_seats = total_capacity - reserved_seats

    # 4. DOLULUK ORANI (%)
    occupancy_rate = (reserved_seats / total_capacity * 100) if total_capacity > 0 else 0

    # 5. GÜNCEL CHECK-IN SAYISI (Bugün)
    today_checkins = db.session.query(func.count(Reservation.id)).filter(
        Reservation.checked_in == True,
        func.date(Reservation.checked_in_at) == func.current_date()
    ).scalar() or 0

    # 6. SON 7 GÜN CHECK-IN SAYISI
    week_checkins = db.session.query(func.count(Reservation.id)).filter(
        Reservation.checked_in == True,
        Reservation.checked_in_at >= func.current_date() - 7
    ).scalar() or 0

    # 7. AKTİF REZERVASYON SAYISI
    active_reservations = db.session.query(func.count(Reservation.id)).filter(
        Reservation.status == ReservationStatus.ACTIVE
    ).scalar() or 0

    return render_template(
        'admin/dashboard.html',
        company=company,
        users_count=users_count,
        events_count=events_count,
        reservations_count=reservations_count,
        templates_count=templates_count,
        # 🚨 YENİ KRİTİK İSTATİSTİKLER
        total_capacity=total_capacity,
        reserved_seats=reserved_seats,
        available_seats=available_seats,
        occupancy_rate=occupancy_rate,
        today_checkins=today_checkins,
        week_checkins=week_checkins,
        active_reservations=active_reservations,
    )

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(company_id=current_user.company_id).all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create new user with schema validation"""
    schema = UserSchema()
    
    try:
        # Validate input data
        data = schema.load({
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'role': request.form.get('role', 'controller'),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone')
        })
    except ValidationError as err:
        # Log validation error for monitoring
        try:
            payload = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'role': request.form.get('role')
            }
            security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
        except Exception:
            pass

        for field, messages in err.messages.items():
            for message in messages:
                flash(f'{field}: {message}', 'danger')
        return redirect(url_for('admin.users'))
    
    # Check for duplicate username
    if User.query.filter_by(username=data['username']).first():
        flash('Bu kullanıcı adı zaten kullanılıyor.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Create user
    user = User(
        company_id=current_user.company_id,
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'controller'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone')
    )
    
    # Set password (will validate strength in User.set_password)
    try:
        user.set_password(data['password'])
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.add(user)
    db.session.commit()
    flash('Kullanıcı oluşturuldu.', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:user_id>/change-password', methods=['POST'])
@login_required
@admin_required
def change_user_password(user_id):
    """
    Change password for a user.
    Admin can change any user's password in their company.
    """
    # Get user from same company
    user = User.query.filter_by(
        id=user_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    schema = PasswordChangeSchema()
    
    try:
        # Validate new password
        data = schema.load({
            'new_password': request.form.get('new_password'),
            'confirm_password': request.form.get('confirm_password')
        })
    except ValidationError as err:
        # Log validation error
        try:
            payload = {
                'new_password': request.form.get('new_password')
            }
            security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
        except Exception:
            pass

        for field, messages in err.messages.items():
            for message in messages:
                flash(f'{field}: {message}', 'danger')
        return redirect(url_for('admin.users'))
    
    # Set new password (validates strength in User.set_password)
    try:
        user.set_password(data['new_password'])
        db.session.commit()
        flash(f'{user.username} kullanıcısının şifresi başarıyla değiştirildi.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.users'))


@bp.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_own_password():
    """
    Allow users to change their own password.
    Requires current password verification.
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Mevcut şifre hatalı.', 'danger')
            return redirect(url_for('admin.change_own_password'))
        
        # Validate new password with schema
        schema = PasswordChangeSchema()
        try:
            data = schema.load({
                'new_password': new_password,
                'confirm_password': confirm_password
            })
        except ValidationError as err:
            # Log validation error
            try:
                payload = {
                    'new_password': new_password,
                    'confirm_password': confirm_password
                }
                security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
            except Exception:
                pass

            for field, messages in err.messages.items():
                for message in messages:
                    flash(f'{field}: {message}', 'danger')
            return redirect(url_for('admin.change_own_password'))
        
        # Set new password
        try:
            current_user.set_password(data['new_password'])
            db.session.commit()
            flash('Şifreniz başarıyla değiştirildi.', 'success')
            return redirect(url_for('admin.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('admin.change_own_password'))
    
    return render_template('admin/change_password.html')


@bp.route('/seating-types')
@login_required
@admin_required
def seating_types():
    """List all seating types"""
    types = SeatingType.query.all()
    return render_template('admin/seating_types.html', seating_types=types)


@bp.route('/seating-types/create', methods=['POST'])
@admin_required
def create_seating_type():
    """Yeni koltuk türü oluştur"""
    name = request.form.get('name', '').strip()
    seat_type = request.form.get('seat_type', 'table')
    capacity = request.form.get('capacity', 4, type=int)
    color_code = request.form.get('color_code', '#3498db')
    
    if not name:
        flash('Koltuk türü adı gerekli', 'error')
        return redirect(url_for('admin.seating_types'))
    
    seating_type = SeatingType()
    seating_type.name = name
    seating_type.seat_type = seat_type
    seating_type.capacity = capacity
    seating_type.color_code = color_code
    
    db.session.add(seating_type)
    db.session.commit()
    
    flash(f'{name} başarıyla eklendi', 'success')
    return redirect(url_for('admin.seating_types'))


@bp.route('/seating-types/<int:type_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_seating_type(type_id):
    """Delete seating type"""
    seating_type = SeatingType.query.get_or_404(type_id)
    
    # Check if type is used
    if seating_type.seatings:
        flash('Bu koltuk türü kullanılıyor, silinemez.', 'danger')
        return redirect(url_for('admin.seating_types'))
    
    db.session.delete(seating_type)
    db.session.commit()
    flash('Koltuk türü silindi.', 'success')
    return redirect(url_for('admin.seating_types'))


@bp.route('/test-modal')

def test_modal():
    """Modal system test sayfası"""
    return render_template('test_modal.html')
