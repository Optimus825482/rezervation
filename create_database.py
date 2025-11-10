"""
Veritabanını otomatik oluşturan script
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    """rezervasyon_db veritabanını oluşturur"""
    try:
        # postgres veritabanına bağlan (default)
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='518518Erkan',
            host='localhost'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Veritabanı var mı kontrol et
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='rezervasyon_db'")
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Veritabanı zaten mevcut: rezervasyon_db")
        else:
            # Veritabanını oluştur
            cursor.execute("CREATE DATABASE rezervasyon_db")
            print("✓ Veritabanı oluşturuldu: rezervasyon_db")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"✗ PostgreSQL bağlantı hatası: {e}")
        print("\nKontrol et:")
        print("1. PostgreSQL çalışıyor mu? (services.msc)")
        print("2. Kullanıcı adı/şifre doğru mu?")
        return False
    except Exception as e:
        print(f"✗ Hata: {e}")
        return False

if __name__ == '__main__':
    print("Veritabanı oluşturuluyor...")
    if create_database():
        print("\n✓ İşlem başarılı! Şimdi 'flask run' yapabilirsin.")
        sys.exit(0)
    else:
        print("\n✗ İşlem başarısız!")
        sys.exit(1)
