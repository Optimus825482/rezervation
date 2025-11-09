# -*- coding: utf-8 -*-
from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def controller_required(f):
    """Decorator to require controller or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Lütfen giriş yapın.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin and not current_user.is_controller:
            abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def log_activity(action):
    """Decorator to log user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app import db
            from app.models import ActivityLog, User
            
            if current_user.is_authenticated:
                log = ActivityLog(
                    user_id=current_user.id,
                    action=action,
                    ip_address=request.remote_addr if hasattr(request, 'remote_addr') else None,
                    user_agent=request.headers.get('User-Agent') if hasattr(request, 'user_agent') else None
                )
                db.session.add(log)
                db.session.commit()
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
