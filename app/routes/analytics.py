"""
Analytics Routes - Gelişmiş raporlama ve analiz API endpoint'leri
"""

from flask import Blueprint, request, jsonify, send_file, render_template
from flask_login import login_required, current_user
from marshmallow import ValidationError
from app import db
from app.models import Event
from app.utils.decorators import admin_required
from app.services.analytics_service import AnalyticsService
from app.services.export_service import ExportService
from datetime import datetime
import io

bp = Blueprint('analytics', __name__)

@bp.route('/')
@login_required
@admin_required
def analytics_page():
    """Ana analytics sayfası"""
    return render_template('reports/analytics.html')

@bp.route('/export')
@login_required
@admin_required  
def export_page():
    """Export sayfası"""
    return render_template('reports/export.html')

@bp.route('/api/events/<int:event_id>/analytics', methods=['GET'])
@login_required
@admin_required
def get_event_analytics(event_id):
    """Etkinlik analitik verilerini getir"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    try:
        analytics_service = AnalyticsService()
        
        # Query parametreleri
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        report_type = request.args.get('type', 'overview')
        
        if report_type == 'overview':
            data = analytics_service.get_event_overview_analytics(event_id, start_date, end_date)
        elif report_type == 'trends':
            days = int(request.args.get('days', 30))
            data = analytics_service.get_reservation_trends(event_id, days)
        elif report_type == 'seating':
            data = analytics_service.get_seating_analysis(event_id)
        elif report_type == 'customers':
            data = analytics_service.get_customer_analysis(event_id)
        elif report_type == 'timing':
            data = analytics_service.get_time_based_analysis(event_id)
        elif report_type == 'comparative':
            comparison_days = int(request.args.get('comparison_days', 30))
            data = analytics_service.get_comparative_analysis(current_user.company_id, comparison_days)
        else:
            # Tam analiz
            data = {
                'overview': analytics_service.get_event_overview_analytics(event_id, start_date, end_date),
                'trends': analytics_service.get_reservation_trends(event_id),
                'seating': analytics_service.get_seating_analysis(event_id),
                'customers': analytics_service.get_customer_analysis(event_id),
                'timing': analytics_service.get_time_based_analysis(event_id)
            }
        
        return jsonify({
            'success': True,
            'data': data,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Analiz hatası: {str(e)}'
        }), 500

@bp.route('/api/events/<int:event_id>/analytics/summary', methods=['GET'])
@login_required
@admin_required
def get_analytics_summary(event_id):
    """Etkinlik için hızlı özet analiz"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    try:
        analytics_service = AnalyticsService()
        data = analytics_service.get_event_overview_analytics(event_id)
        
        # Sadece temel metrikleri döndür
        summary = {
            'event_info': data['event_info'],
            'key_metrics': {
                'total_capacity': data['capacity_metrics']['total_capacity'],
                'occupancy_rate': data['capacity_metrics']['occupancy_rate'],
                'checkin_rate': data['reservation_metrics']['checkin_rate'],
                'active_reservations': data['capacity_metrics']['active_reservations']
            },
            'trends': analytics_service.get_reservation_trends(event_id, days=7)
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Özet analiz hatası: {str(e)}'
        }), 500

@bp.route('/api/reports/export/pdf', methods=['POST'])
@login_required
@admin_required
def export_pdf():
    """PDF rapor oluştur"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        report_type = data.get('report_type', 'comprehensive')
        
        if not event_id:
            return jsonify({
                'success': False,
                'message': 'event_id parametresi gerekli'
            }), 400
        
        # Yetki kontrolü
        event = Event.query.filter_by(
            id=event_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        export_service = ExportService()
        pdf_file = export_service.export_to_pdf(event_id, report_type)
        
        return pdf_file
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'PDF export hatası: {str(e)}'
        }), 500

@bp.route('/api/reports/export/excel', methods=['POST'])
@login_required
@admin_required
def export_excel():
    """Excel rapor oluştur"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        include_analytics = data.get('include_analytics', True)
        
        if not event_id:
            return jsonify({
                'success': False,
                'message': 'event_id parametresi gerekli'
            }), 400
        
        # Yetki kontrolü
        event = Event.query.filter_by(
            id=event_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        export_service = ExportService()
        excel_file = export_service.export_to_excel(event_id, include_analytics)
        
        return excel_file
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Excel export hatası: {str(e)}'
        }), 500

@bp.route('/api/reports/export/csv', methods=['POST'])
@login_required
@admin_required
def export_csv():
    """CSV rapor oluştur"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        file_format = data.get('format', 'utf-8')
        
        if not event_id:
            return jsonify({
                'success': False,
                'message': 'event_id parametresi gerekli'
            }), 400
        
        # Yetki kontrolü
        event = Event.query.filter_by(
            id=event_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        export_service = ExportService()
        csv_file = export_service.export_to_csv(event_id, file_format)
        
        return csv_file
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'CSV export hatası: {str(e)}'
        }), 500

@bp.route('/api/reports/export/json', methods=['POST'])
@login_required
@admin_required
def export_json():
    """JSON rapor oluştur"""
    try:
        data = request.get_json()
        event_id = data.get('event_id')
        
        if not event_id:
            return jsonify({
                'success': False,
                'message': 'event_id parametresi gerekli'
            }), 400
        
        # Yetki kontrolü
        event = Event.query.filter_by(
            id=event_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        export_service = ExportService()
        json_file = export_service.create_json_export(event_id)
        
        return json_file
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'JSON export hatası: {str(e)}'
        }), 500

@bp.route('/api/events/<int:event_id>/dashboard-data', methods=['GET'])
@login_required
@admin_required
def get_dashboard_data(event_id):
    """Dashboard için hızlı veri"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    try:
        analytics_service = AnalyticsService()
        
        # Dashboard metrikleri
        overview = analytics_service.get_event_overview_analytics(event_id)
        trends = analytics_service.get_reservation_trends(event_id, days=7)
        seating = analytics_service.get_seating_analysis(event_id)
        
        # Dashboard için özet veri
        dashboard_data = {
            'event_info': {
                'id': event.id,
                'name': event.name,
                'date': event.event_date.isoformat() if event.event_date else None,
                'status': event.status.value if event.status else None
            },
            'quick_stats': {
                'total_capacity': overview['capacity_metrics']['total_capacity'],
                'active_reservations': overview['capacity_metrics']['active_reservations'],
                'available_seats': overview['capacity_metrics']['available_seats'],
                'occupancy_rate': overview['capacity_metrics']['occupancy_rate'],
                'checkin_rate': overview['reservation_metrics']['checkin_rate'],
                'checked_in': overview['reservation_metrics']['checked_in']
            },
            'recent_trends': trends['daily_trends'][-7:] if trends['daily_trends'] else [],
            'seating_status': {
                'total_seats': len(seating),
                'full_seats': len([s for s in seating if s['status'] == 'full']),
                'available_seats': len([s for s in seating if s['status'] == 'available'])
            }
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Dashboard veri hatası: {str(e)}'
        }), 500

@bp.route('/api/company/analytics', methods=['GET'])
@login_required
@admin_required
def get_company_analytics():
    """Şirket genelinde analitik veriler"""
    try:
        analytics_service = AnalyticsService()
        
        # Query parametreleri
        period_days = int(request.args.get('period_days', 30))
        
        data = analytics_service.get_comparative_analysis(current_user.company_id, period_days)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Şirket analiz hatası: {str(e)}'
        }), 500

@bp.route('/api/events/<int:event_id>/report-preview', methods=['GET'])
@login_required
@admin_required
def get_report_preview(event_id):
    """Rapor önizlemesi için veri hazırla"""
    event = Event.query.filter_by(
        id=event_id,
        company_id=current_user.company_id
    ).first_or_404()
    
    try:
        analytics_service = AnalyticsService()
        
        # Önizleme verileri
        overview = analytics_service.get_event_overview_analytics(event_id)
        trends = analytics_service.get_reservation_trends(event_id, days=7)
        seating = analytics_service.get_seating_analysis(event_id)[:5]  # İlk 5 oturum
        customers = analytics_service.get_customer_analysis(event_id)
        
        preview_data = {
            'event': {
                'name': event.name,
                'date': event.event_date.isoformat() if event.event_date else None,
                'status': event.status.value if event.status else None
            },
            'summary': {
                'total_reservations': overview['reservation_metrics']['total_reservations'],
                'occupancy_rate': overview['capacity_metrics']['occupancy_rate'],
                'checkin_rate': overview['reservation_metrics']['checkin_rate'],
                'unique_customers': customers['total_unique_customers']
            },
            'trends_data': trends['daily_trends'][-5:] if trends['daily_trends'] else [],
            'sample_seating': seating,
            'customer_segments': customers['segments']
        }
        
        return jsonify({
            'success': True,
            'data': preview_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Önizleme hatası: {str(e)}'
        }), 500
