# -*- coding: utf-8 -*-
"""
Şablon Yönetim Servisi
Şablonların export/import işlemlerini yönetir
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app
from app import db
from app.models import (
    SeatingLayoutTemplate, 
    EventTemplate, 
    SeatingType, 
    Company, 
    User
)
from marshmallow import ValidationError


class TemplateService:
    """Şablon yönetim işlemlerini yöneten servis sınıfı"""
    
    def __init__(self, company_id: int, user_id: int):
        self.company_id = company_id
        self.user_id = user_id
    
    def export_seating_template(self, template_id: int) -> Dict[str, Any]:
        """
        Oturum düzeni şablonunu export eder
        
        Args:
            template_id: Şablon ID'si
            
        Returns:
            Dict: Export verileri
        """
        try:
            template = SeatingLayoutTemplate.query.filter_by(
                id=template_id,
                company_id=self.company_id
            ).first_or_404()
            
            # Şablon verilerini hazırla
            export_data = {
                'template_type': 'seating_layout',
                'version': '1.0',
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': self.user_id,
                'template': {
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'stage_position': template.stage_position,
                    'configuration': json.loads(template.configuration) if template.configuration else {},
                    'is_favorite': template.is_favorite
                }
            }
            
            return {
                'success': True,
                'data': export_data,
                'filename': f'seating_template_{template.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
            
        except Exception as e:
            current_app.logger.error(f"Seating template export error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_event_template(self, template_id: int) -> Dict[str, Any]:
        """
        Etkinlik şablonunu export eder
        
        Args:
            template_id: Şablon ID'si
            
        Returns:
            Dict: Export verileri
        """
        try:
            template = EventTemplate.query.filter_by(
                id=template_id,
                company_id=self.company_id
            ).first_or_404()
            
            # İlgili oturum düzeni şablonunu da dahil et
            seating_layout_data = None
            if template.seating_layout_template_id:
                seating_template = SeatingLayoutTemplate.query.get(template.seating_layout_template_id)
                if seating_template:
                    seating_layout_data = {
                        'name': seating_template.name,
                        'description': seating_template.description,
                        'category': seating_template.category,
                        'stage_position': seating_template.stage_position,
                        'configuration': json.loads(seating_template.configuration) if seating_template.configuration else {}
                    }
            
            # Şablon verilerini hazırla
            export_data = {
                'template_type': 'event_template',
                'version': '1.0',
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': self.user_id,
                'template': {
                    'name': template.name,
                    'description': template.description,
                    'default_event_type': template.default_event_type,
                    'default_venue_type': template.default_venue_type,
                    'default_duration_hours': template.default_duration_hours,
                    'default_pricing': json.loads(template.default_pricing) if template.default_pricing else {},
                    'settings': json.loads(template.settings) if template.settings else {},
                    'seating_layout': seating_layout_data
                }
            }
            
            return {
                'success': True,
                'data': export_data,
                'filename': f'event_template_{template.name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
            
        except Exception as e:
            current_app.logger.error(f"Event template export error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_seating_template(self, file_data: Dict[str, Any], override_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Oturum düzeni şablonunu import eder
        
        Args:
            file_data: Import edilecek veriler
            override_name: Yeniden adlandırma
            
        Returns:
            Dict: Import sonucu
        """
        try:
            # Veri doğrulama
            if file_data.get('template_type') != 'seating_layout':
                return {'success': False, 'error': 'Geçersiz şablon dosyası'}
            
            template_data = file_data.get('template', {})
            
            # Yeni şablon oluştur
            template = SeatingLayoutTemplate()
            template.company_id = self.company_id
            template.name = override_name or template_data.get('name', 'İmport Edilen Şablon')
            template.description = template_data.get('description', '')
            template.category = template_data.get('category', 'genel')
            template.stage_position = template_data.get('stage_position', 'top')
            template.configuration = json.dumps(template_data.get('configuration', {}))
            template.is_favorite = template_data.get('is_favorite', False)
            
            # Kullanım sayacı
            template.usage_count = 0
            
            db.session.add(template)
            db.session.commit()
            
            return {
                'success': True,
                'template_id': template.id,
                'name': template.name,
                'message': f'Seating layout şablonu başarıyla import edildi: {template.name}'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Seating template import error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_event_template(self, file_data: Dict[str, Any], override_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Etkinlik şablonunu import eder
        
        Args:
            file_data: Import edilecek veriler
            override_name: Yeniden adlandırma
            
        Returns:
            Dict: Import sonucu
        """
        try:
            # Veri doğrulama
            if file_data.get('template_type') != 'event_template':
                return {'success': False, 'error': 'Geçersiz şablon dosyası'}
            
            template_data = file_data.get('template', {})
            
            # Önce oturum düzeni şablonunu import et (varsa)
            seating_layout_template_id = None
            if template_data.get('seating_layout'):
                seating_result = self.import_seating_layout_from_data(template_data['seating_layout'])
                if seating_result['success']:
                    seating_layout_template_id = seating_result['template_id']
            
            # Yeni şablon oluştur
            template = EventTemplate()
            template.company_id = self.company_id
            template.seating_layout_template_id = seating_layout_template_id
            template.name = override_name or template_data.get('name', 'İmport Edilen Etkinlik Şablonu')
            template.description = template_data.get('description', '')
            template.default_event_type = template_data.get('default_event_type', 'genel')
            template.default_venue_type = template_data.get('default_venue_type', 'genel')
            template.default_duration_hours = template_data.get('default_duration_hours', 4)
            template.default_pricing = json.dumps(template_data.get('default_pricing', {}))
            template.settings = json.dumps(template_data.get('settings', {}))
            
            db.session.add(template)
            db.session.commit()
            
            return {
                'success': True,
                'template_id': template.id,
                'name': template.name,
                'message': f'Event template başarıyla import edildi: {template.name}'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Event template import error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_all_templates(self) -> Dict[str, Any]:
        """
        Tüm şablonları tek seferde export eder
        
        Returns:
            Dict: Export verileri
        """
        try:
            # Seating layout şablonları
            seating_templates = SeatingLayoutTemplate.query.filter_by(
                company_id=self.company_id
            ).all()
            
            # Event şablonları
            event_templates = EventTemplate.query.filter_by(
                company_id=self.company_id
            ).all()
            
            # Export verilerini hazırla
            export_data = {
                'export_type': 'all_templates',
                'version': '1.0',
                'exported_at': datetime.utcnow().isoformat(),
                'exported_by': self.user_id,
                'company_info': {
                    'id': self.company_id
                },
                'seating_templates': [],
                'event_templates': []
            }
            
            # Seating şablonlarını dahil et
            for template in seating_templates:
                export_data['seating_templates'].append({
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'stage_position': template.stage_position,
                    'configuration': json.loads(template.configuration) if template.configuration else {},
                    'is_favorite': template.is_favorite,
                    'usage_count': template.usage_count
                })
            
            # Event şablonlarını dahil et
            for template in event_templates:
                seating_layout_data = None
                if template.seating_layout_template_id:
                    seating_template = SeatingLayoutTemplate.query.get(template.seating_layout_template_id)
                    if seating_template:
                        seating_layout_data = {
                            'name': seating_template.name,
                            'description': seating_template.description,
                            'category': seating_template.category,
                            'stage_position': seating_template.stage_position,
                            'configuration': json.loads(seating_template.configuration) if seating_template.configuration else {}
                        }
                
                export_data['event_templates'].append({
                    'name': template.name,
                    'description': template.description,
                    'default_event_type': template.default_event_type,
                    'default_venue_type': template.default_venue_type,
                    'default_duration_hours': template.default_duration_hours,
                    'default_pricing': json.loads(template.default_pricing) if template.default_pricing else {},
                    'settings': json.loads(template.settings) if template.settings else {},
                    'seating_layout': seating_layout_data
                })
            
            return {
                'success': True,
                'data': export_data,
                'filename': f'all_templates_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'template_count': {
                    'seating': len(seating_templates),
                    'event': len(event_templates)
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Export all templates error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_all_templates(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tüm şablonları tek seferde import eder
        
        Args:
            file_data: Import edilecek veriler
            
        Returns:
            Dict: Import sonucu
        """
        try:
            # Veri doğrulama
            if file_data.get('export_type') != 'all_templates':
                return {'success': False, 'error': 'Geçersiz export dosyası'}
            
            import_count = {'seating': 0, 'event': 0, 'errors': []}
            
            # Önce seating şablonlarını import et
            seating_templates = file_data.get('seating_templates', [])
            for template_data in seating_templates:
                try:
                    template = SeatingLayoutTemplate()
                    template.company_id = self.company_id
                    template.name = template_data.get('name', 'İmport Edilen Şablon')
                    template.description = template_data.get('description', '')
                    template.category = template_data.get('category', 'genel')
                    template.stage_position = template_data.get('stage_position', 'top')
                    template.configuration = json.dumps(template_data.get('configuration', {}))
                    template.is_favorite = template_data.get('is_favorite', False)
                    template.usage_count = template_data.get('usage_count', 0)
                    
                    db.session.add(template)
                    import_count['seating'] += 1
                    
                except Exception as e:
                    import_count['errors'].append(f"Seating template import error: {str(e)}")
            
            # Event şablonlarını import et
            event_templates = file_data.get('event_templates', [])
            for template_data in event_templates:
                try:
                    # İlgili seating layout'u bul
                    seating_layout_template_id = None
                    if template_data.get('seating_layout'):
                        seating_name = template_data['seating_layout']['name']
                        existing_seating = SeatingLayoutTemplate.query.filter_by(
                            company_id=self.company_id,
                            name=seating_name
                        ).first()
                        if existing_seating:
                            seating_layout_template_id = existing_seating.id
                    
                    template = EventTemplate()
                    template.company_id = self.company_id
                    template.seating_layout_template_id = seating_layout_template_id
                    template.name = template_data.get('name', 'İmport Edilen Etkinlik Şablonu')
                    template.description = template_data.get('description', '')
                    template.default_event_type = template_data.get('default_event_type', 'genel')
                    template.default_venue_type = template_data.get('default_venue_type', 'genel')
                    template.default_duration_hours = template_data.get('default_duration_hours', 4)
                    template.default_pricing = json.dumps(template_data.get('default_pricing', {}))
                    template.settings = json.dumps(template_data.get('settings', {}))
                    
                    db.session.add(template)
                    import_count['event'] += 1
                    
                except Exception as e:
                    import_count['errors'].append(f"Event template import error: {str(e)}")
            
            db.session.commit()
            
            return {
                'success': True,
                'imported_count': import_count,
                'message': f'Import tamamlandı. {import_count["seating"]} seating, {import_count["event"]} event şablonu import edildi.'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Import all templates error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def duplicate_template(self, template_type: str, template_id: int, new_name: str) -> Dict[str, Any]:
        """
        Şablonu kopyalar (versiyon oluşturma)
        
        Args:
            template_type: 'seating' veya 'event'
            template_id: Kopyalanacak şablon ID'si
            new_name: Yeni şablon adı
            
        Returns:
            Dict: Kopyalama sonucu
        """
        try:
            if template_type == 'seating':
                original = SeatingLayoutTemplate.query.filter_by(
                    id=template_id,
                    company_id=self.company_id
                ).first_or_404()
                
                # Yeni şablon oluştur
                new_template = SeatingLayoutTemplate()
                new_template.company_id = self.company_id
                new_template.name = new_name
                new_template.description = f"{original.description} (Kopya)" if original.description else "Kopya"
                new_template.category = original.category
                new_template.stage_position = original.stage_position
                new_template.configuration = original.configuration
                new_template.is_favorite = False  # Kopya favorilerde olmaz
                
                db.session.add(new_template)
                
            elif template_type == 'event':
                original = EventTemplate.query.filter_by(
                    id=template_id,
                    company_id=self.company_id
                ).first_or_404()
                
                # Yeni şablon oluştur
                new_template = EventTemplate()
                new_template.company_id = self.company_id
                new_template.seating_layout_template_id = original.seating_layout_template_id
                new_template.name = new_name
                new_template.description = f"{original.description} (Kopya)" if original.description else "Kopya"
                new_template.default_event_type = original.default_event_type
                new_template.default_venue_type = original.default_venue_type
                new_template.default_duration_hours = original.default_duration_hours
                new_template.default_pricing = original.default_pricing
                new_template.settings = original.settings
                
                db.session.add(new_template)
            else:
                return {'success': False, 'error': 'Geçersiz şablon tipi'}
            
            db.session.commit()
            
            return {
                'success': True,
                'template_id': new_template.id,
                'name': new_template.name,
                'message': f'Şablon başarıyla kopyalandı: {new_template.name}'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Template duplication error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_template_usage_count(self, template_type: str, template_id: int):
        """Şablon kullanım sayısını günceller"""
        try:
            if template_type == 'seating':
                template = SeatingLayoutTemplate.query.filter_by(
                    id=template_id,
                    company_id=self.company_id
                ).first()
                if template:
                    template.usage_count = (template.usage_count or 0) + 1
                    db.session.commit()
                    
            elif template_type == 'event':
                template = EventTemplate.query.filter_by(
                    id=template_id,
                    company_id=self.company_id
                ).first()
                if template:
                    template.usage_count = (template.usage_count or 0) + 1
                    db.session.commit()
                    
        except Exception as e:
            current_app.logger.error(f"Template usage count update error: {str(e)}")
    
    def get_popular_templates(self, template_type: str, limit: int = 10) -> List[Dict]:
        """
        Popüler şablonları getirir
        
        Args:
            template_type: 'seating' veya 'event'
            limit: Sonuç sayısı limiti
            
        Returns:
            List: Popüler şablonlar
        """
        try:
            if template_type == 'seating':
                templates = SeatingLayoutTemplate.query.filter_by(
                    company_id=self.company_id
                ).order_by(SeatingLayoutTemplate.usage_count.desc()).limit(limit).all()
                
                return [
                    {
                        'id': t.id,
                        'name': t.name,
                        'description': t.description,
                        'category': t.category,
                        'usage_count': t.usage_count or 0,
                        'is_favorite': t.is_favorite
                    }
                    for t in templates
                ]
                
            elif template_type == 'event':
                templates = EventTemplate.query.filter_by(
                    company_id=self.company_id
                ).order_by(EventTemplate.usage_count.desc()).limit(limit).all()
                
                return [
                    {
                        'id': t.id,
                        'name': t.name,
                        'description': t.description,
                        'default_event_type': t.default_event_type,
                        'default_venue_type': t.default_venue_type,
                        'usage_count': t.usage_count or 0
                    }
                    for t in templates
                ]
                
        except Exception as e:
            current_app.logger.error(f"Get popular templates error: {str(e)}")
            return []
    
    def import_seating_layout_from_data(self, layout_data: Dict[str, Any]) -> Dict[str, Any]:
        """Event template import sırasında kullanılan internal method"""
        try:
            template = SeatingLayoutTemplate()
            template.company_id = self.company_id
            template.name = layout_data.get('name', 'İmport Edilen Düzen')
            template.description = layout_data.get('description', '')
            template.category = layout_data.get('category', 'genel')
            template.stage_position = layout_data.get('stage_position', 'top')
            template.configuration = json.dumps(layout_data.get('configuration', {}))
            template.is_favorite = False
            
            db.session.add(template)
            db.session.commit()
            
            return {
                'success': True,
                'template_id': template.id,
                'name': template.name
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }