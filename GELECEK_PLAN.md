# GÖRSEL OTURUM DÜZENLEME (Drag & Drop) GELİŞTİRME PLANI

**Öncelik:** 1/5 (En Kritik)  
**Geliştirme Başlangıcı:** 08.11.2025

---

## 🎯 HEDEF
Etkinlik oluştururken/düzenlerken oturumları görsel olarak sürükle-bırak ile yerleştirebilme

## 📋 YAPILACAKLAR

### AŞAMA 1: Temel Canvas ve Grid Sistemi
- [ ] Mevcut visual-editor.js'yi geliştir
- [ ] Grid sistem ekle (snap to grid)
- [ ] Zoom in/out özelliği
- [ ] Canvas boyutları ayarlama

### AŞAMA 2: Drag & Drop Mekanizması
- [ ] Sürüklenebilir oturum objeleri
- [ ] Drop alanı tanımlama
- [ ] Pozisyon kaydetme (X,Y koordinatları)
- [ ] Çakışma kontrolü

### AŞAMA 3: Oturum Yönetimi
- [ ] Oturum tiplerini canvas'a ekleme
- [ ] Otomatik numara atama
- [ ] Renk kodlaması sistemi
- [ ] Hover detayları

### AŞAMA 4: Veritabanı Entegrasyonu
- [ ] EventSeating modeline pozisyon alanları
- [ ] Anlık kaydetme
- [ ] Drag & drop sonrası update

### AŞAMA 5: UI Geliştirmeleri
- [ ] Sahne konumu belirleme (üst/alt/sağ/sol)
- [ ] Geri al/İleri al (undo/redo)
- [ ] Şablon kaydetme/yükleme

---

## 🔧 TEKNİK GEREKSİNİMLER

### Frontend:
- HTML5 Canvas veya SVG
- Drag & Drop kütüphanesi
- Chart.js (grafik için)
- Z-index yönetimi

### Backend:
- EventSeating modeli güncelleme
- API endpoints güncelleme
- Template kaydetme sistemi

### Dosyalar:
- `app/static/js/visual-editor.js` (geliştirilecek)
- `app/templates/event/create.html` (güncellenecek)
- `app/templates/event/edit.html` (güncellenecek)
- `app/models/seating.py` (EventSeating güncelleme)

---

## 🎯 BAŞLANGIÇ
İlk adım: Mevcut visual-editor.js'yi incele ve temel Canvas altyapısını kur
