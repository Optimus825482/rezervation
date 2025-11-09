"""
Görsel Oturum Düzenleme Sistemi Migration
EventSeating ve SeatingLayoutTemplate tablolarına yeni alanlar ekleniyor

Tarih: 08.11.2025
Amaç: Görsel editör için gerekli pozisyon ve boyut alanları
"""

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Veritabanı bağlantısı"""
    db_path = os.path.join(os.getcwd(), 'instance', 'reservation.db')
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)

def create_visual_seating_migration():
    """Görsel oturum düzenleme için migration"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Görsel Oturum Düzenleme Migration Başlatılıyor...")
        
        # 1. EventSeating tablosuna yeni alanlar ekle
        print("📊 EventSeating tablosu güncelleniyor...")
        
        # Width alanını ekle (eğer mevcut değilse)
        try:
            cursor.execute("ALTER TABLE event_seatings ADD COLUMN width REAL DEFAULT 60")
            print("✅ width alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ width alanı zaten mevcut")
            else:
                raise e
        
        # Height alanını ekle (eğer mevcut değilse)
        try:
            cursor.execute("ALTER TABLE event_seatings ADD COLUMN height REAL DEFAULT 40")
            print("✅ height alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ height alanı zaten mevcut")
            else:
                raise e
        
        # 2. SeatingLayoutTemplate tablosuna yeni alanlar ekle
        print("🎨 SeatingLayoutTemplate tablosu güncelleniyor...")
        
        # Canvas_width alanını ekle (eğer mevcut değilse)
        try:
            cursor.execute("ALTER TABLE seating_layout_templates ADD COLUMN canvas_width INTEGER DEFAULT 800")
            print("✅ canvas_width alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ canvas_width alanı zaten mevcut")
            else:
                raise e
        
        # Canvas_height alanını ekle (eğer mevcut değilse)
        try:
            cursor.execute("ALTER TABLE seating_layout_templates ADD COLUMN canvas_height INTEGER DEFAULT 600")
            print("✅ canvas_height alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ canvas_height alanı zaten mevcut")
            else:
                raise e
        
        # Grid_size alanını ekle (eğer mevcut değilse)
        try:
            cursor.execute("ALTER TABLE seating_layout_templates ADD COLUMN grid_size INTEGER DEFAULT 20")
            print("✅ grid_size alanı eklendi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ grid_size alanı zaten mevcut")
            else:
                raise e
        
        # 3. Migration kaydı
        print("📝 Migration kaydı oluşturuluyor...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success'
            )
        """)
        
        cursor.execute("""
            INSERT INTO migration_history (migration_name, status) 
            VALUES (?, ?)
        """, ('visual_seating_enhancement', 'success'))
        
        # 4. Değişiklikleri kaydet
        conn.commit()
        print("✅ Migration tamamlandı!")
        
        # 5. Güncel durumu kontrol et
        print("\n🔍 Güncel tablo yapısı kontrol ediliyor...")
        
        # EventSeating kontrol
        cursor.execute("PRAGMA table_info(event_seatings)")
        columns = cursor.fetchall()
        print("\n📋 EventSeating sütunları:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # SeatingLayoutTemplate kontrol
        cursor.execute("PRAGMA table_info(seating_layout_templates)")
        columns = cursor.fetchall()
        print("\n📋 SeatingLayoutTemplate sütunları:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n🎉 Migration başarıyla tamamlandı!")
        
    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_visual_seating_migration()
