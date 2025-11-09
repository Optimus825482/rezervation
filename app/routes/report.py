from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event, Reservation
from app.services.report_service import ReportService
from app.utils.decorators import admin_required, controller_required
from datetime import datetime, timedelta
import json
import os

bp = Blueprint('report', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('report/index.html')

@bp.route('/summary')
@login_required
@admin_required
def summary():
    """Gelişmiş özet raporu"""
    try:
        # Tarih filtresi
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_filter_start = None
        date_filter_end = None
        
        if start_date:
            date_filter_start = datetime.fromisoformat(start_date)
        if end_date:
            date_filter_end = datetime.fromisoformat(end_date)
        
        # Rapor servisi
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_summary_report(date_filter_start, date_filter_end)
        
        return render_template('report/summary.html',
                             report_data=report_data,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        flash(f'Özet raporu oluşturulurken hata: {str(e)}', 'error')
        return render_template('report/summary.html', report_data={})

@bp.route('/event/<int:event_id>')
@login_required
@admin_required
def event_detail(event_id):
    """Etkinlik detay raporu"""
    try:
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_event_detail_report(event_id)
        
        if 'error' in report_data:
            flash('Etkinlik bulunamadı veya erişim yetkiniz yok.', 'error')
            return redirect(url_for('report.index'))
        
        return render_template('report/event_detail.html', report_data=report_data)
        
    except Exception as e:
        flash(f'Etkinlik raporu oluşturulurken hata: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/reservations/analysis')
@login_required
@admin_required
def reservation_analysis():
    """Rezervasyon analiz raporu"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'daily')
        
        date_filter_start = None
        date_filter_end = None
        
        if start_date:
            date_filter_start = datetime.fromisoformat(start_date)
        if end_date:
            date_filter_end = datetime.fromisoformat(end_date)
        
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_reservation_analysis_report(
            date_filter_start, date_filter_end, group_by
        )
        
        return render_template('report/reservation_analysis.html',
                             report_data=report_data,
                             start_date=start_date,
                             end_date=end_date,
                             group_by=group_by)
                             
    except Exception as e:
        flash(f'Rezervasyon analizi oluşturulurken hata: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/occupancy/analysis')
@login_required
@admin_required
def occupancy_analysis():
    """Doluluk analiz raporu"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_filter_start = None
        date_filter_end = None
        
        if start_date:
            date_filter_start = datetime.fromisoformat(start_date)
        if end_date:
            date_filter_end = datetime.fromisoformat(end_date)
        
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_occupancy_analysis_report(
            date_filter_start, date_filter_end
        )
        
        return render_template('report/occupancy_analysis.html',
                             report_data=report_data,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        flash(f'Doluluk analizi oluşturulurken hata: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/customer/analysis')
@login_required
@admin_required
def customer_analysis():
    """Müşteri analiz raporu"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_filter_start = None
        date_filter_end = None
        
        if start_date:
            date_filter_start = datetime.fromisoformat(start_date)
        if end_date:
            date_filter_end = datetime.fromisoformat(end_date)
        
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_customer_analysis_report(
            date_filter_start, date_filter_end
        )
        
        return render_template('report/customer_analysis.html',
                             report_data=report_data,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        flash(f'Müşteri analizi oluşturulurken hata: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/export/excel')
@login_required
@admin_required
def export_excel():
    """Excel formatında export"""
    try:
        report_type = request.args.get('type', 'summary')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        date_filter_start = None
        date_filter_end = None
        
        if start_date:
            date_filter_start = datetime.fromisoformat(start_date)
        if end_date:
            date_filter_end = datetime.fromisoformat(end_date)
        
        report_service = ReportService(current_user.company_id)
        
        # Uygun rapor verilerini al
        if report_type == 'summary':
            report_data = report_service.get_summary_report(date_filter_start, date_filter_end)
        elif report_type == 'reservation':
            report_data = report_service.get_reservation_analysis_report(date_filter_start, date_filter_end)
        else:
            report_data = report_service.get_summary_report(date_filter_start, date_filter_end)
        
        # Excel dosyası oluştur
        filepath = report_service.export_to_excel(report_data, report_type)
        
        # Dosya indirme için redirect
        return redirect(f'/static/uploads/reports/{os.path.basename(filepath)}')
        
    except Exception as e:
        flash(f'Excel export hatası: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/export/csv')
@login_required
@admin_required
def export_csv():
    """CSV formatında export"""
    try:
        report_type = request.args.get('type', 'reservations')
        event_id = request.args.get('event_id')
        
        report_service = ReportService(current_user.company_id)
        
        if report_type == 'reservations' and event_id:
            # Belirli etkinliğin rezervasyonlarını export et
            report_data = report_service.get_event_detail_report(int(event_id))
            if 'reservations' in report_data:
                data = report_data['reservations']
                filename = f'reservations_event_{event_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            else:
                data = []
                filename = f'reservations_event_{event_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:
            # Tüm rezervasyonlar
            reservations = Reservation.query.join(Event).filter(
                Event.company_id == current_user.company_id
            ).all()
            
            data = [
                {
                    'ID': r.id,
                    'Müşteri Adı': r.customer_name,
                    'Telefon': r.phone,
                    'Etkinlik': r.event.name,
                    'Oturum': r.seating.seat_number if r.seating else 'N/A',
                    'Kişi Sayısı': r.number_of_people,
                    'Check-in': 'Evet' if r.checked_in else 'Hayır',
                    'Durum': r.status.value
                }
                for r in reservations
            ]
            filename = f'reservations_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        filepath = report_service.export_to_csv(data, filename)
        
        return redirect(f'/static/uploads/reports/{filename}')
        
    except Exception as e:
        flash(f'CSV export hatası: {str(e)}', 'error')
        return redirect(url_for('report.index'))

@bp.route('/api/summary')
@login_required
@admin_required
def api_summary():
    """JSON API: Özet rapor verileri"""
    try:
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_summary_report()
        
        return jsonify({
            'success': True,
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@bp.route('/api/event/<int:event_id>')
@login_required
@admin_required
def api_event_detail(event_id):
    """JSON API: Etkinlik detay verileri"""
    try:
        report_service = ReportService(current_user.company_id)
        report_data = report_service.get_event_detail_report(event_id)
        
        if 'error' in report_data:
            return jsonify({
                'success': False,
                'error': 'Etkinlik bulunamadı'
            })
        
        return jsonify({
            'success': True,
            'data': report_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
