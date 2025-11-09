#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Superadmin kullanıcısı oluşturma scripti - Docker ortamı için
Docker PostgreSQL veritabanı bilgileri:
- Host: db (docker-compose network içinde)
- Database: rezervasyon_db
- User: postgres
- Password: password
"""
import sys
import os

# Flask app'i oluştur - Docker container içinde DATABASE_URL zaten ayarlanmış
# Eğer ayarlanmamışsa (yerel test için) varsayılanı kullan
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://postgres:password@db:5432/rezervasyon_db'

from app import create_app, db
from app.models.user import User
from app.models.company import Company
from werkzeug.security import generate_password_hash

def create_superadmin():
    """Superadmin kullanıcısı oluşturur"""
    print("\n🔌 Veritabanına bağlanılıyor...")
    print(f"   Database: {os.environ.get('DATABASE_URL', 'Ayarlanmamış')[:50]}...")
    
    app = create_app()
    
    with app.app_context():
        # Veritabanı bağlantısını test et
        try:
            db.engine.connect()
            print("✅ Veritabanı bağlantısı başarılı!\n")
        except Exception as e:
            print(f"❌ Veritabanı bağlantı hatası: {str(e)}")
            print("\n💡 Docker container'ın çalıştığından emin olun:")
            print("   docker-compose ps")
            sys.exit(1)
        
        # Kullanıcı bilgileri
        email = "admin@rezervasyon.com"
        username = "superadmin"
        password = "518518Erkan."
        first_name = "Super"
        last_name = "Admin"
        
        try:
            # Önce Company kontrolü ve oluşturma
            company = Company.query.first()
            if not company:
                print("🏢 Sistem şirketi oluşturuluyor...")
                company = Company(
                    name="Sistem Yönetimi",
                    email="sistem@rezervasyon.com",
                    phone="0000000000",
                    address="Sistem",
                    is_setup_complete=True
                )
                db.session.add(company)
                db.session.commit()
                print(f"✅ Şirket oluşturuldu (ID: {company.id})")
            else:
                print(f"✅ Mevcut şirket kullanılıyor: {company.name} (ID: {company.id})")
            
            # Kullanıcı zaten var mı kontrol et
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                print(f"\n⚠️  UYARI: {email} kullanıcısı zaten mevcut!")
                print(f"   Kullanıcı ID: {existing_user.id}")
                print(f"   Kullanıcı Adı: {existing_user.username}")
                print(f"   Rol: {existing_user.role}")
                print(f"   Aktif: {'Evet' if existing_user.is_active else 'Hayır'}")
                
                # Şifreyi güncelle
                print("\n🔄 Kullanıcı şifresi güncelleniyor...")
                existing_user.password_hash = generate_password_hash(password)
                existing_user.role = 'admin'
                existing_user.is_active = True
                
                db.session.commit()
                print(f"✅ {email} kullanıcısı başarıyla güncellendi!")
                
            else:
                # Yeni kullanıcı oluştur
                print("\n🆕 Yeni superadmin kullanıcısı oluşturuluyor...")
                superadmin = User(
                    company_id=company.id,
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    role='admin',
                    is_active=True
                )
                
                db.session.add(superadmin)
                db.session.commit()
                
                print("✅ Superadmin kullanıcısı başarıyla oluşturuldu!")
            
            # Kullanıcı bilgilerini göster
            print("\n" + "="*60)
            print("SUPERADMIN BİLGİLERİ")
            print("="*60)
            print(f"Email: {email}")
            print(f"Kullanıcı Adı: {username}")
            print(f"Şifre: {password}")
            print(f"Ad Soyad: {first_name} {last_name}")
            print("Rol: admin")
            print("="*60)
            print("\n⚠️  ÖNEMLİ: Bu bilgileri güvenli bir yerde saklayın!")
            print("⚠️  İlk giriş sonrası şifrenizi değiştirmeniz önerilir.")
            
        except Exception as e:
            db.session.rollback()
            print("\n❌ HATA: Kullanıcı oluşturulurken bir hata oluştu!")
            print(f"Hata detayı: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SUPERADMIN KULLANICI OLUŞTURMA")
    print("="*60)
    create_superadmin()
    print("\n✨ İşlem tamamlandı!\n")
