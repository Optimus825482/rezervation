"""
Analytics Service - Veri analizi ve hesaplamalar
Gelişmiş raporlama sistemi için veri işleme servisleri
"""

from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from collections import defaultdict
from app import db
from app.models import Event, EventSeating, Reservation, SeatingType
from app.models.reservation import ReservationStatus
import pandas as pd


class AnalyticsService:
    """Etkinlik analitik verilerini işleyen servis"""
    
    def __init__(self):
        pass
    
    def get_event_overview_analytics(self, event_id, start_date=None, end_date=None):
        """Etkinlik genel özet analitikleri"""
        event = Event.query.get_or_404(event_id)
        
        # Temel metrikler
        total_seats = EventSeating.query.filter_by(event_id=event_id).count()
        total_capacity = db.session.query(func.sum(EventSeating.seating_type.has(capacity=SeatingType.capacity))).join(
            SeatingType, EventSeating.seating_type_id == SeatingType.id
        ).filter(EventSeating.event_id == event_id).scalar() or 0
        
        # Rezervasyon metrikleri
        total_reservations = Reservation.query.filter_by(event_id=event_id).count()
        active_reservations = Reservation.query.filter_by(
            event_id=event_id, status=ReservationStatus.ACTIVE
        ).count()
        checked_in = Reservation.query.filter_by(
            event_id=event_id, checked_in=True
        ).count()
        cancelled = Reservation.query.filter_by(
            event_id=event_id, status=ReservationStatus.CANCELLED
        ).count()
        
        # Hesaplamalar
        occupancy_rate = (active_reservations / total_capacity * 100) if total_capacity > 0 else 0
        checkin_rate = (checked_in / active_reservations * 100) if active_reservations > 0 else 0
        
        return {
            'event_info': {
                'id': event.id,
                'name': event.name,
                'date': event.event_date.isoformat() if event.event_date else None,
                'status': event.status.value if event.status else None
            },
            'capacity_metrics': {
                'total_seats': total_seats,
                'total_capacity': total_capacity,
                'active_reservations': active_reservations,
                'available_seats': total_capacity - active_reservations,
                'occupancy_rate': round(occupancy_rate, 2)
            },
            'reservation_metrics': {
                'total_reservations': total_reservations,
                'active_reservations': active_reservations,
                'checked_in': checked_in,
                'cancelled': cancelled,
                'checkin_rate': round(checkin_rate, 2)
            }
        }
    
    def get_reservation_trends(self, event_id, days=30):
        """Rezervasyon trend analizi"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Günlük rezervasyon trendleri
        daily_trends = db.session.query(
            func.date(Reservation.created_at).label('date'),
            func.count(Reservation.id).label('count'),
            func.sum(func.case([(Reservation.checked_in == True, 1)], else_=0)).label('checkins')
        ).filter(
            and_(
                Reservation.event_id == event_id,
                Reservation.created_at >= start_date,
                Reservation.created_at <= end_date
            )
        ).group_by(func.date(Reservation.created_at)).all()
        
        # Haftalık trendler
        weekly_trends = db.session.query(
            func.strftime('%Y-%W', Reservation.created_at).label('week'),
            func.count(Reservation.id).label('count')
        ).filter(
            and_(
                Reservation.event_id == event_id,
                Reservation.created_at >= start_date,
                Reservation.created_at <= end_date
            )
        ).group_by(func.strftime('%Y-%W', Reservation.created_at)).all()
        
        return {
            'daily_trends': [
                {
                    'date': trend.date.isoformat(),
                    'reservations': trend.count,
                    'checkins': trend.checkins
                } for trend in daily_trends
            ],
            'weekly_trends': [
                {
                    'week': trend.week,
                    'reservations': trend.count
                } for trend in weekly_trends
            ]
        }
    
    def get_seating_analysis(self, event_id):
        """Oturum bazında doluluk analizi"""
        seating_analysis = db.session.query(
            EventSeating.id,
            EventSeating.seat_number,
            SeatingType.name.label('seating_type'),
            SeatingType.capacity,
            func.count(Reservation.id).label('reservations')
        ).join(
            SeatingType, EventSeating.seating_type_id == SeatingType.id
        ).outerjoin(
            Reservation, EventSeating.id == Reservation.seating_id
        ).filter(
            EventSeating.event_id == event_id
        ).group_by(
            EventSeating.id, EventSeating.seat_number, SeatingType.name, SeatingType.capacity
        ).all()
        
        return [
            {
                'seating_id': seating.id,
                'seat_number': seating.seat_number,
                'seating_type': seating.seating_type,
                'capacity': seating.capacity,
                'reservations': seating.reservations,
                'occupancy_rate': (seating.reservations / seating.capacity * 100) if seating.capacity > 0 else 0,
                'status': 'full' if seating.reservations >= seating.capacity else 'available'
            }
            for seating in seating_analysis
        ]
    
    def get_customer_analysis(self, event_id):
        """Müşteri analiz raporu"""
        # Müşteri istatistikleri
        customer_stats = db.session.query(
            Reservation.phone,
            Reservation.first_name,
            Reservation.last_name,
            func.count(Reservation.id).label('reservation_count'),
            func.sum(Reservation.number_of_people).label('total_people')
        ).filter(
            and_(
                Reservation.event_id == event_id,
                Reservation.status != ReservationStatus.CANCELLED
            )
        ).group_by(
            Reservation.phone, Reservation.first_name, Reservation.last_name
        ).all()
        
        # Müşteri segmentasyonu
        segments = {
            'new_customers': 0,
            'returning_customers': 0,
            'group_bookings': 0,
            'individual_bookings': 0
        }
        
        for customer in customer_stats:
            if customer.reservation_count == 1:
                segments['new_customers'] += 1
            else:
                segments['returning_customers'] += 1
            
            if customer.total_people and customer.total_people > 1:
                segments['group_bookings'] += 1
            else:
                segments['individual_bookings'] += 1
        
        return {
            'customer_list': [
                {
                    'phone': customer.phone,
                    'name': f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
                    'reservation_count': customer.reservation_count,
                    'total_people': customer.total_people or 0
                }
                for customer in customer_stats
            ],
            'segments': segments,
            'total_unique_customers': len(customer_stats)
        }
    
    def get_time_based_analysis(self, event_id):
        """Zaman bazlı rezervasyon analizi"""
        # Saatlik dağılım
        hourly_distribution = db.session.query(
            func.strftime('%H', Reservation.created_at).label('hour'),
            func.count(Reservation.id).label('count')
        ).filter(
            Reservation.event_id == event_id
        ).group_by(func.strftime('%H', Reservation.created_at)).all()
        
        # Günlük dağılım
        daily_distribution = db.session.query(
            func.strftime('%w', Reservation.created_at).label('day_of_week'),
            func.count(Reservation.id).label('count')
        ).filter(
            Reservation.event_id == event_id
        ).group_by(func.strftime('%w', Reservation.created_at)).all()
        
        day_names = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
        
        return {
            'hourly_distribution': [
                {
                    'hour': int(dist.hour),
                    'count': dist.count
                } for dist in hourly_distribution
            ],
            'daily_distribution': [
                {
                    'day': day_names[int(dist.day_of_week)],
                    'day_number': int(dist.day_of_week),
                    'count': dist.count
                } for dist in daily_distribution
            ]
        }
    
    def get_comparative_analysis(self, company_id, comparison_period_days=30):
        """Şirket bazında karşılaştırmalı analiz"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=comparison_period_days)
        
        # Bu dönem
        current_period = db.session.query(
            func.count(Reservation.id).label('reservations'),
            func.sum(Reservation.number_of_people).label('people')
        ).join(
            Event, Reservation.event_id == Event.id
        ).filter(
            and_(
                Event.company_id == company_id,
                Reservation.created_at >= start_date,
                Reservation.created_at <= end_date
            )
        ).first()
        
        # Önceki dönem
        prev_start = start_date - timedelta(days=comparison_period_days)
        prev_end = start_date
        
        previous_period = db.session.query(
            func.count(Reservation.id).label('reservations'),
            func.sum(Reservation.number_of_people).label('people')
        ).join(
            Event, Reservation.event_id == Event.id
        ).filter(
            and_(
                Event.company_id == company_id,
                Reservation.created_at >= prev_start,
                Reservation.created_at <= prev_end
            )
        ).first()
        
        # Etkinlik performansı
        event_performance = db.session.query(
            Event.name,
            func.count(Reservation.id).label('reservations'),
            func.sum(Reservation.number_of_people).label('people')
        ).join(
            Reservation, Event.id == Reservation.event_id
        ).filter(
            and_(
                Event.company_id == company_id,
                Event.event_date >= start_date,
                Event.event_date <= end_date
            )
        ).group_by(Event.id, Event.name).all()
        
        return {
            'current_period': {
                'reservations': current_period.reservations or 0,
                'people': current_period.people or 0
            },
            'previous_period': {
                'reservations': previous_period.reservations or 0,
                'people': previous_period.people or 0
            },
            'growth_rates': {
                'reservations': self._calculate_growth_rate(
                    current_period.reservations or 0,
                    previous_period.reservations or 0
                ),
                'people': self._calculate_growth_rate(
                    current_period.people or 0,
                    previous_period.people or 0
                )
            },
            'event_performance': [
                {
                    'event_name': event.name,
                    'reservations': event.reservations,
                    'people': event.people or 0
                }
                for event in event_performance
            ]
        }
    
    def _calculate_growth_rate(self, current, previous):
        """Büyüme oranı hesapla"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 2)
    
    def export_data_to_dataframe(self, event_id):
        """Verileri pandas DataFrame'e aktar"""
        # Rezervasyon verileri
        reservations = db.session.query(
            Reservation.id,
            Reservation.phone,
            Reservation.first_name,
            Reservation.last_name,
            Event.name.label('event_name'),
            EventSeating.seat_number,
            SeatingType.name.label('seating_type'),
            SeatingType.capacity,
            Reservation.number_of_people,
            Reservation.status,
            Reservation.checked_in,
            Reservation.created_at
        ).join(
            Event, Reservation.event_id == Event.id
        ).outerjoin(
            EventSeating, Reservation.seating_id == EventSeating.id
        ).outerjoin(
            SeatingType, EventSeating.seating_type_id == SeatingType.id
        ).filter(
            Reservation.event_id == event_id
        ).all()
        
        # DataFrame oluştur
        data = []
        for res in reservations:
            data.append({
                'Rezervasyon_ID': res.id,
                'Telefon': res.phone,
                'Ad': res.first_name or '',
                'Soyad': res.last_name or '',
                'Etkinlik': res.event_name or '',
                'Oturum_No': res.seat_number or '',
                'Oturum_Tip': res.seating_type or '',
                'Kapasite': res.capacity or 0,
                'Kisi_Sayisi': res.number_of_people or 0,
                'Durum': res.status.value if res.status else '',
                'Check_in': 'Evet' if res.checked_in else 'Hayır',
                'Olusturma_Tarihi': res.created_at.strftime('%d.%m.%Y %H:%M') if res.created_at else ''
            })
        
        return pd.DataFrame(data)
