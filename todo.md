# GÖRSEL OTURUM DÜZENLEME - TODO LİSTESİ

**Geliştirme Başlangıcı:** 08.11.2025  
**Amaç:** En yüksek öncelikli eksikliği (Görsel Oturum Düzenleme) tamamlamak

---

## AŞAMA 1: VERİTABANI GÜNCELLEME
- [x] EventSeating modeline pozisyon alanları ekle (x, y, width, height, stage_position)
- [x] Alembic migration oluştur ve çalıştır (PostgreSQL: rezervasyon_db)
- [x] Model validation ve API schema'ları güncelle

## AŞAMA 2: BACKEND API GELİŞTİRME  
- [x] EventSeating API endpoint'leri (/api/events/{id}/seating/config)
- [x] Oturum konfigürasyonu kaydetme/yükleme
- [x] Drag & drop sonrası anlık kaydetme
- [x] Template kaydetme sistemi

## AŞAMA 3: FRONTEND ENTEGRASYON
- [x] Event create/edit template'lerinde editörü entegre et
- [x] Oturum tiplerini ekleme paneli
- [x] Kaydet/yükle butonları
- [x] Responsive tasarım iyileştirmeleri

## AŞAMA 4: İLERİ SEVİYE ÖZELLİKLER
- [x] Geri al/İleri al (undo/redo) sistemi
- [x] Çakışma kontrolü ve düzeltme
- [x] Otomatik yerleştirme algoritmaları
- [ ] Görsel raporlama entegrasyonu (gelecek geliştirme)

## AŞAMA 5: TEST VE OPTİMİZASYON
- [ ] Tüm özellikler için test senaryoları
- [ ] Performance optimizasyonu
- [ ] Kullanıcı deneyimi iyileştirmeleri
- [ ] Dokümantasyon tamamlama

---

## GÜNÜN GÖREVİ
**Hedef:** AŞAMA 1'i tamamla - EventSeating modeli güncelleme

### İlk Adımlar:
1. [ ] EventSeating model dosyasını incele
2. [ ] Pozisyon alanlarını ekle
3. [ ] Migration script'i oluştur
4. [ ] Test et

---

## NOTLAR
- Mevcut visual-editor.js kodu oldukça gelişmiş
- Canvas, grid, zoom, drag&drop temel altyapı hazır
- EventSeating modeli güncellemesi kritik adım
- Sıralı yaklaşım: Veritabanı → Backend → Frontend → Test
