# -*- coding: utf-8 -*-
"""
Oturum Yönetim Servisi
Dinamik oturum ekleme, düzenleme işlemlerini yönetir
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app
from app import db
from app.models import (
    SeatingType, 
    EventSeating, 
    Event, 
    SeatingType,
    Reservation
)
from sqlalchemy import and_


class SeatingService:
    """Oturum yönetim işlemlerini yöneten servis sınıfı"""
    
    def __init__(self, company_id: int):
        self.company_id = company_id
    
    def get_default_seating_types(self) -> List[Dict[str, Any]]:
        """
        Varsayılan oturum tiplerini getirir
        
        Returns:
            List[Dict]: Varsayılan oturum tipleri
        """
        return [
            {
                'name': 'Masa - 2 Kişilik',
                'capacity': 2,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#e74c3c',
                'default': True
            },
            {
                'name': 'Masa - 4 Kişilik',
                'capacity': 4,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#3498db',
                'default': True
            },
            {
                'name': 'Masa - 5 Kişilik',
                'capacity': 5,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#9b59b6',
                'default': True
            },
            {
                'name': 'Masa - 6 Kişilik',
                'capacity': 6,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#f39c12',
                'default': True
            },
            {
                'name': 'Masa - 8 Kişilik',
                'capacity': 8,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#2ecc71',
                'default': True
            },
            {
                'name': 'Masa - 10 Kişilik',
                'capacity': 10,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#1abc9c',
                'default': True
            },
            {
                'name': 'Masa - 12 Kişilik',
                'capacity': 12,
                'seat_type': 'table',
                'icon': '🪑',
                'color': '#34495e',
                'default': True
            },
            {
                'name': 'Tekli Koltuk',
                'capacity': 1,
                'seat_type': 'chair',
                'icon': '💺',
                'color': '#e74c3c',
                'default': True
            },
            {
                'name': 'İkili Koltuk',
                'capacity': 2,
                'seat_type': 'chair',
                'icon': '💺',
                'color': '#e67e22',
                'default': True
            },
            {
                'name': 'VIP Loca',
                'capacity': 8,
                'seat_type': 'vip',
                'icon': '👑',
                'color': '#f1c40f',
                'default': True
            }
        ]
    
    def create_seating_type(self, seating_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Yeni oturum tipi oluşturur
        
        Args:
            seating_data: Oturum tipi verileri
            
        Returns:
            Dict: Oluşturma sonucu
        """
        try:
            seating_type = SeatingType(
                name=seating_data.get('name'),
                seat_type=seating_data.get('seat_type', 'table'),
                capacity=seating_data.get('capacity', 4),
                icon=seating_data.get('icon', '🪑'),
                color_code=seating_data.get('color', '#3498db')
            )
            
            db.session.add(seating_type)
            db.session.commit()
            
            return {
                'success': True,
                'seating_type_id': seating_type.id,
                'name': seating_type.name,
                'message': f'Oturum tipi oluşturuldu: {seating_type.name}'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Seating type creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_seating_types(self) -> List[Dict[str, Any]]:
        """
        Şirkete ait oturum tiplerini getirir
        
        Returns:
            List[Dict]: Oturum tipi listesi
        """
        try:
            # Varsayılan tipleri dahil et
            default_types = self.get_default_seating_types()
            
            # Şirketin özel tiplerini dahil et
            custom_types = SeatingType.query.all()
            
            result = []
            
            # Varsayılan tipleri ekle
            for default_type in default_types:
                result.append({
                    'id': f'default_{default_type["capacity"]}_{default_type["seat_type"]}',
                    'name': default_type['name'],
                    'capacity': default_type['capacity'],
                    'seat_type': default_type['seat_type'],
                    'icon': default_type['icon'],
                    'color_code': default_type['color'],
                    'is_default': True,
                    'usage_count': 0
                })
            
            # Özel tipleri ekle
            for custom_type in custom_types:
                result.append({
                    'id': custom_type.id,
                    'name': custom_type.name,
                    'capacity': custom_type.capacity,
                    'seat_type': custom_type.seat_type,
                    'icon': custom_type.icon,
                    'color_code': custom_type.color_code,
                    'is_default': False,
                    'usage_count': getattr(custom_type, 'usage_count', 0)
                })
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Get seating types error: {str(e)}")
            return []
    
    def add_seatings_to_event(self, event_id: int, seating_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Etkinliğe dinamik oturum ekler
        
        Args:
            event_id: Etkinlik ID'si
            seating_configs: Oturum konfigürasyonları
            
        Returns:
            Dict: Ekleme sonucu
        """
        try:
            event = Event.query.filter_by(
                id=event_id,
                company_id=self.company_id
            ).first_or_404()
            
            created_count = 0
            errors = []
            
            for config in seating_configs:
                try:
                    # Oturum tipi ID'sini al
                    seating_type_id = self._get_or_create_seating_type(config)
                    
                    # Kaç adet oluşturulacak
                    count = config.get('count', 1)
                    
                    # Mevcut oturum sayısını al
                    existing_count = EventSeating.query.filter_by(
                        event_id=event_id
                    ).count()
                    
                    # Yeni oturumları oluştur
                    for i in range(count):
                        new_seating = EventSeating()
                        new_seating.event_id = event_id
                        new_seating.seating_type_id = seating_type_id
                        new_seating.seat_number = self._generate_seat_number(
                            event_id, existing_count + i + 1
                        )
                        new_seating.position_x = config.get('position_x', 100)
                        new_seating.position_y = config.get('position_y', 100)
                        new_seating.color_code = config.get('color_code')
                        
                        db.session.add(new_seating)
                        created_count += 1
                
                except Exception as e:
                    errors.append(f"Oturum ekleme hatası: {str(e)}")
            
            db.session.commit()
            
            return {
                'success': True,
                'created_count': created_count,
                'errors': errors,
                'message': f'{created_count} oturum başarıyla eklendi'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Add seatings to event error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def remove_seating_from_event(self, event_id: int, seating_id: int) -> Dict[str, Any]:
        """
        Etkinlikten oturum kaldırır
        
        Args:
            event_id: Etkinlik ID'si
            seating_id: Oturum ID'si
            
        Returns:
            Dict: Kaldırma sonucu
        """
        try:
            # Rezerve edilmiş oturumları kontrol et
            reservation = Reservation.query.filter_by(
                seating_id=seating_id,
                status='active'
            ).first()
            
            if reservation:
                return {
                    'success': False,
                    'error': 'Bu oturumda aktif rezervasyon bulunuyor, kaldırılamaz'
                }
            
            seating = EventSeating.query.filter_by(
                id=seating_id,
                event_id=event_id
            ).first_or_404()
            
            db.session.delete(seating)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Oturum başarıyla kaldırıldı'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Remove seating error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_seating_position(self, event_id: int, seating_id: int, x: float, y: float) -> Dict[str, Any]:
        """
        Oturum pozisyonunu günceller
        
        Args:
            event_id: Etkinlik ID'si
            seating_id: Oturum ID'si
            x: X koordinatı
            y: Y koordinatı
            
        Returns:
            Dict: Güncelleme sonucu
        """
        try:
            seating = EventSeating.query.filter_by(
                id=seating_id,
                event_id=event_id
            ).first_or_404()
            
            seating.position_x = round(x / 20) * 20  # Grid snap
            seating.position_y = round(y / 20) * 20  # Grid snap
            
            db.session.commit()
            
            return {
                'success': True,
                'position_x': seating.position_x,
                'position_y': seating.position_y
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update seating position error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_event_seating_summary(self, event_id: int) -> Dict[str, Any]:
        """
        Etkinlik oturum özetini getirir
        
        Args:
            event_id: Etkinlik ID'si
            
        Returns:
            Dict: Oturum özeti
        """
        try:
            event = Event.query.filter_by(
                id=event_id,
                company_id=self.company_id
            ).first_or_404()
            
            # Oturum tiplerine göre grupla
            seating_summary = {}
            total_capacity = 0
            
            seatings = EventSeating.query.filter_by(event_id=event_id).all()
            
            for seating in seatings:
                type_name = seating.seating_type.name
                capacity = seating.seating_type.capacity
                
                if type_name not in seating_summary:
                    seating_summary[type_name] = {
                        'count': 0,
                        'total_capacity': 0,
                        'reserved': 0,
                        'available': 0
                    }
                
                seating_summary[type_name]['count'] += 1
                seating_summary[type_name]['total_capacity'] += capacity
                total_capacity += capacity
                
                # Rezervasyon durumu
                if seating.status == 'reserved':
                    reservation = Reservation.query.filter_by(
                        seating_id=seating.id,
                        status='active'
                    ).first()
                    if reservation:
                        seating_summary[type_name]['reserved'] += 1
                    else:
                        seating_summary[type_name]['available'] += 1
                else:
                    seating_summary[type_name]['available'] += 1
            
            # Toplam özet
            summary = {
                'total_seatings': len(seatings),
                'total_capacity': total_capacity,
                'by_type': seating_summary,
                'event_info': {
                    'id': event.id,
                    'name': event.name,
                    'date': event.event_date.isoformat()
                }
            }
            
            return summary
            
        except Exception as e:
            current_app.logger.error(f"Get event seating summary error: {str(e)}")
            return {}
    
    def validate_seating_layout(self, event_id: int, seating_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Oturum düzenini validate eder
        
        Args:
            event_id: Etkinlik ID'si
            seating_configs: Oturum konfigürasyonları
            
        Returns:
            Dict: Validation sonucu
        """
        try:
            issues = []
            warnings = []
            
            for config in seating_configs:
                # Kapasite kontrolü
                if config.get('capacity', 0) <= 0:
                    issues.append(f"Geçersiz kapasite: {config.get('name', 'Bilinmeyen')}")
                
                # Konum kontrolü
                x = config.get('position_x', 0)
                y = config.get('position_y', 0)
                width = config.get('width', 60)
                height = config.get('height', 40)
                
                if x < 0 or y < 0:
                    issues.append(f"Negatif pozisyon: {config.get('name', 'Bilinmeyen')}")
                
                # Sınır kontrolü
                canvas_width = 800
                canvas_height = 600
                
                if x + width > canvas_width or y + height > canvas_height:
                    warnings.append(f"Canvas sınırı aşılıyor: {config.get('name', 'Bilinmeyen')}")
                
                # Çakışma kontrolü
                overlaps = self._check_overlaps(event_id, x, y, width, height, config)
                if overlaps:
                    warnings.append(f"Diğer oturumlarla çakışma: {config.get('name', 'Bilinmeyen')}")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings
            }
            
        except Exception as e:
            current_app.logger.error(f"Seating layout validation error: {str(e)}")
            return {
                'valid': False,
                'issues': [f'Validation hatası: {str(e)}'],
                'warnings': []
            }
    
    def _get_or_create_seating_type(self, config: Dict[str, Any]) -> int:
        """Oturum tipi ID'sini alır veya oluşturur"""
        # Varsayılan tipler
        default_types = self.get_default_seating_types()
        for default in default_types:
            if (default['capacity'] == config.get('capacity') and 
                default['seat_type'] == config.get('seat_type')):
                # Varsayılan tip için sanal ID oluştur
                return int(f"{default['capacity']}_{default['seat_type']}")
        
        # Özel tip oluştur
        seating_type = SeatingType(
            name=config.get('name', f'Özel Tip - {config.get("capacity", 0)} kişi'),
            seat_type=config.get('seat_type', 'table'),
            capacity=config.get('capacity', 4),
            icon=config.get('icon', '🪑'),
            color_code=config.get('color', '#3498db')
        )
        
        db.session.add(seating_type)
        db.session.flush()  # ID almak için
        
        return seating_type.id
    
    def _generate_seat_number(self, event_id: int, index: int) -> str:
        """Oturum numarası oluşturur"""
        # M tipi masa, K tipi koltuk, V tipi VIP için
        return f"M{index:03d}"  # M001, M002, vb.
    
    def _check_overlaps(self, event_id: int, x: float, y: float, width: float, height: float, config: Dict[str, Any]) -> bool:
        """Oturum çakışmalarını kontrol eder"""
        existing_seatings = EventSeating.query.filter_by(event_id=event_id).all()
        
        for seating in existing_seatings:
            if (x < seating.position_x + 60 and  # 60 genişlik varsayımı
                x + width > seating.position_x and
                y < seating.position_y + 40 and  # 40 yükseklik varsayımı
                y + height > seating.position_y):
                return True
        
        return False
    
    def save_seating_layout(self, event_id: int, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Oturum düzenini kaydeder
        
        Args:
            event_id: Etkinlik ID'si
            layout_data: Düzen verileri
            
        Returns:
            Dict: Kaydetme sonucu
        """
        try:
            event = Event.query.filter_by(
                id=event_id,
                company_id=self.company_id
            ).first_or_404()
            
            # Mevcut oturumları temizle (sadece boş olanları)
            EventSeating.query.filter(
                EventSeating.event_id == event_id,
                ~EventSeating.reservations.any()  # Rezervasyonu olmayanlar
            ).delete()
            
            # Yeni oturumları oluştur
            for seating_data in layout_data.get('seatings', []):
                seating = EventSeating()
                seating.event_id = event_id
                seating.seat_number = seating_data.get('seat_number', 'M001')
                seating.position_x = seating_data.get('x', 0)
                seating.position_y = seating_data.get('y', 0)
                seating.color_code = seating_data.get('color', '#3498db')
                
                # Oturum tipi
                if seating_data.get('seating_type_id'):
                    seating.seating_type_id = seating_data.get('seating_type_id')
                else:
                    # Varsayılan tip
                    default_types = self.get_default_seating_types()
                    for default in default_types:
                        if (default['capacity'] == seating_data.get('capacity', 4) and 
                            default['seat_type'] == seating_data.get('seat_type', 'table')):
                            seating.seating_type_id = int(f"{default['capacity']}_{default['seat_type']}")
                            break
                
                db.session.add(seating)
            
            # Düzen metadatasını kaydet
            event.seating_config = json.dumps(layout_data)
            event.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Oturum düzeni başarıyla kaydedildi'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Save seating layout error: {str(e)}")
            return {'success': False, 'error': str(e)}