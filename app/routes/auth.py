# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from marshmallow import ValidationError
from app import db, limiter
from app.models import User, Company
from app.schemas.user_schema import UserSchema
from app.services.security_logger import security_logger

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Max 5 login attempts per minute
def login():
    """User login with rate limiting and security logging"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard' if current_user.is_admin else 'controller.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                # Log failed login - inactive account
                security_logger.log_failed_login(username, reason='Account disabled')
                flash('Hesabınız devre dışı. Yöneticinizle iletişime geçin.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            user.last_login = db.func.now()
            db.session.commit()
            
            # Log successful login
            security_logger.log_successful_login(username, user.id)
            
            # Clear any existing active event session
            session.pop('active_event_id', None)
            session.pop('active_event_name', None)
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_admin:
                    next_page = url_for('admin.dashboard')
                else:
                    next_page = url_for('controller.dashboard')
            
            return redirect(next_page)
        else:
            # Log failed login - invalid credentials
            security_logger.log_failed_login(username or 'Unknown', reason='Invalid credentials')
            flash('Kullanıcı adı veya şifre hatalı.', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Başarıyla çıkış yapıldı.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/setup', methods=['GET', 'POST'])
@limiter.limit("10 per hour")  # Max 10 setup attempts per hour
def setup():
    """Initial setup wizard with schema validation and rate limiting"""
    # Check if setup is already complete
    company = Company.query.first()
    if company and company.is_setup_complete:
        flash('Sistem zaten kurulmuş. Giriş yapın.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        schema = UserSchema()
        
        # Company info
        company_name = request.form.get('company_name')
        company_email = request.form.get('company_email')
        company_phone = request.form.get('company_phone')
        company_address = request.form.get('company_address')
        
        # Admin user info
        try:
            user_data = schema.load({
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'phone': request.form.get('phone')
            })
        except ValidationError as err:
            # Log validation error for monitoring
            try:
                payload = {
                    'username': request.form.get('username'),
                    'email': request.form.get('email')
                }
                security_logger.log_validation_error(schema.__class__.__name__, err.messages, payload)
            except Exception:
                pass

            for field, messages in err.messages.items():
                for message in messages:
                    flash(f'{field}: {message}', 'danger')
            return redirect(url_for('auth.setup'))
        
        # Validate company phone (using schema validator)
        from app.schemas import BaseSchema
        base_schema = BaseSchema()
        if company_phone:
            try:
                base_schema.validate_turkish_phone(company_phone)
            except ValidationError as e:
                flash(f'Şirket telefonu: {str(e)}', 'danger')
                return redirect(url_for('auth.setup'))
        
        # Create company
        company = Company(
            name=company_name,
            email=company_email,
            phone=company_phone,
            address=company_address,
            is_setup_complete=True
        )
        db.session.add(company)
        db.session.flush()  # Get company.id
        
        # Create admin user
        user = User(
            company_id=company.id,
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            phone=user_data.get('phone'),
            role='admin'
        )
        
        # Set password (validates in User.set_password)
        try:
            user.set_password(user_data['password'])
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.setup'))
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kurulum tamamlandı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/setup.html')
