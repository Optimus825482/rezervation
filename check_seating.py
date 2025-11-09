#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import create_app, db
from app.models import SeatingType, Company

app = create_app('development')

with app.app_context():
    count = SeatingType.query.count()
    print(f"Toplam Koltuk Türü: {count}")
    
    if count == 0:
        print("\n⚠️ Koltuk türü yok! Örnek veriler oluşturuluyor...")
        
        # Örnek koltuk türleri ekle (global - tüm şirketler için)
        types = [
            SeatingType(name="VIP Masa", seat_type="table", capacity=1, color_code="#FFD700"),
            SeatingType(name="Premium Masa", seat_type="table", capacity=2, color_code="#C0C0C0"),
            SeatingType(name="Standart Masa", seat_type="table", capacity=4, color_code="#3498db"),
            SeatingType(name="Ekonomi Masa", seat_type="table", capacity=6, color_code="#95a5a6"),
            SeatingType(name="Tekli Sandalye", seat_type="chair", capacity=1, color_code="#e74c3c"),
        ]
        
        for st in types:
            db.session.add(st)
        
        db.session.commit()
        print(f"✅ {len(types)} koltuk türü oluşturuldu!")
    else:
        types = SeatingType.query.all()
        print("\nMevcut Koltuk Türleri:")
        for st in types:
            print(f"  - {st.name} (Kapasite: {st.capacity}, Renk: {st.color_code})")
