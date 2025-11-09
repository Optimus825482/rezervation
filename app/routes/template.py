from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from marshmallow import ValidationError
from app import db
from app.models import SeatingLayoutTemplate, EventTemplate
from app.utils.decorators import admin_required
from app.schemas.template_schema import SeatingTemplateSchema, EventTemplateSchema
from app.services.security_logger import security_logger
import json

bp = Blueprint('template', __name__)

# Legacy route redirects for backward compatibility
@bp.route('/seating-templates')
@login_required
@admin_required
def seating_templates_legacy():
    """Legacy redirect to new route"""
    return redirect(url_for('template.seating_templates'))

@bp.route('/seating')
@login_required
@admin_required
def seating_templates():
    templates = SeatingLayoutTemplate.query.filter_by(
        company_id=current_user.company_id
    ).all()
    return render_template('template/seating.html', templates=templates)

@bp.route('/seating/create', methods=['POST'])
@login_required
@admin_required
def create_seating_template():
    schema = SeatingTemplateSchema()
    
    try:
        # Validate and sanitize input data
        validated_data = schema.load({
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'stage_position': request.form.get('stage_position'),
            'configuration': request.form.get('configuration')
        })
        
        template = SeatingLayoutTemplate()
        template.company_id = current_user.company_id
        template.name = validated_data['name']
        template.category = validated_data['category']
        template.stage_position = validated_data.get('stage_position')
        template.configuration = validated_data.get('configuration', '{}')
        
        db.session.add(template)
        db.session.commit()
        flash('Şablon oluşturuldu.', 'success')
        
    except ValidationError as e:
        # Log validation error for monitoring
        try:
            payload = {
                'name': request.form.get('name'),
                'category': request.form.get('category'),
                'stage_position': request.form.get('stage_position'),
                'configuration': request.form.get('configuration')
            }
            security_logger.log_validation_error(schema.__class__.__name__, e.messages, payload)
        except Exception:
            pass

        for field, messages in e.messages.items():
            for message in messages if isinstance(messages, list) else [messages]:
                flash(f'{field}: {message}', 'danger')
        return redirect(url_for('template.seating_templates'))
    
    return redirect(url_for('template.seating_templates'))

@bp.route('/seating/<int:template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_seating_template(template_id):
    """Delete a seating template"""
    template = SeatingLayoutTemplate.query.filter_by(
        id=template_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    db.session.delete(template)
    db.session.commit()
    flash('Şablon silindi.', 'success')
    return redirect(url_for('template.seating_templates'))

@bp.route('/event')
@login_required
@admin_required
def event_templates():
    templates = EventTemplate.query.filter_by(
        company_id=current_user.company_id
    ).all()
    return render_template('template/event.html', templates=templates)

@bp.route('/event/create', methods=['POST'])
@login_required
@admin_required
def create_event_template():
    """Create a new event template"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Şablon adı gerekli', 'error')
        return redirect(url_for('template.event_templates'))
    
    template = EventTemplate()
    template.company_id = current_user.company_id
    template.name = name
    template.description = description if description else None
    
    db.session.add(template)
    db.session.commit()
    
    flash('Etkinlik şablonu başarıyla oluşturuldu', 'success')
    return redirect(url_for('template.event_templates'))

@bp.route('/event/<int:template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event_template(template_id):
    """Delete an event template"""
    template = EventTemplate.query.filter_by(
        id=template_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    db.session.delete(template)
    db.session.commit()
    flash('Şablon silindi.', 'success')
    return redirect(url_for('template.event_templates'))

@bp.route('/api/list', methods=['GET'])
@login_required
@admin_required
def api_list_templates():
    """API endpoint to list all seating layout templates"""
    try:
        templates = SeatingLayoutTemplate.query.filter_by(
            company_id=current_user.company_id
        ).order_by(SeatingLayoutTemplate.created_at.desc()).all()
        
        template_list = []
        for template in templates:
            # Parse configuration to get seating count
            seating_count = 0
            try:
                config = json.loads(template.configuration) if template.configuration else {}
                seatings = config.get('seatings', [])
                seating_count = len(seatings)
            except:
                pass
            
            template_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'category': template.category,
                'stage_position': template.stage_position,
                'seating_count': seating_count,
                'created_at': template.created_at.strftime('%d.%m.%Y %H:%M') if template.created_at else None
            })
        
        return jsonify({
            'success': True,
            'templates': template_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

