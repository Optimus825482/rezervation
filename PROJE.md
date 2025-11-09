# ETKİNLİK REZERVASYON YÖNETİM SİSTEMİ

## 📋 PROJE GENEL BAKIŞ

Etkinlik Rezervasyon Yönetim Sistemi, farklı tiplerdeki etkinlikler için oturum/masa rezervasyonu yapılmasını, görsel olarak planlanmasını ve kontrol edilmesini sağlayan **Python Flask** tabanlı web uygulamasıdır.

### 🛠️ Teknoloji Stack
- **Backend**: Python 3.11+ / Flask
- **Veritabanı**: PostgreSQL
- **Frontend**: Modern UI Framework ( Jinja2 Template)
- **ORM**: SQLAlchemy
- **Kimlik Doğrulama**: Flask-Login / JWT

---

## 👥 KULLANICI ROLLERİ VE YETKİLER

### 1. Sistem Yöneticisi (Admin)
- Sistem kurulumu ve yapılandırma
- Etkinlik oluşturma ve düzenleme
- Oturum planlaması (görsel düzenleme)
- Rezervasyon işlemleri
- Kullanıcı (Kontrolör) yönetimi
- Tüm raporlara erişim

### 2. Kontrolör
- Giriş yapıldıktan sonra aktif etkinliklerden birini seçme
- Seçilen etkinliğin rezervasyon bilgilerini görüntüleme
- Alan doluluk durumunu görüntüleme
- İstatistik ve raporlar
- Check-in işlemleri (QR kod okuma veya manuel arama)
- Müşteri bilgilerini görüntüleme (ad/soyad/telefon/oturum)

---

## 🎯 SİSTEM MODÜLLERİ VE ÖZELLİKLER

### MODÜL 1: SİSTEM KURULUMU (İlk Kurulum)

#### 1.1 Firma Bilgileri
- **Firma Adı**: (zorunlu)
- **Telefon**: (zorunlu)
- **E-posta**: (zorunlu)
- **Adres**: (opsiyonel)
- **Logo**: (opsiyonel)

#### 1.2 İlk Admin Kullanıcı Oluşturma
- **Kullanıcı Adı**: (zorunlu, benzersiz)
- **Şifre**: (zorunlu, min 8 karakter, güçlü şifre kuralları)
- **Şifre Tekrar**: (zorunlu)
- **Ad**: (zorunlu)
- **Soyad**: (zorunlu)
- **E-posta**: (zorunlu)
- **Telefon**: (opsiyonel)

#### 1.3 Doğrulama Kuralları
- E-posta formatı kontrolü
- Telefon formatı kontrolü (Türkiye: 05XX XXX XX XX)
- Şifre güvenlik kontrolü (büyük/küçük harf, sayı, özel karakter)
- Kullanıcı adı benzersizlik kontrolü

---

### MODÜL 2: YÖNETİCİ PANELİ

#### 2.1 ETKİNLİK PLANLAMA

##### A) Etkinlik Temel Bilgileri
```
- Etkinlik Adı: (zorunlu, max 200 karakter)
- Etkinlik Türü: (dropdown)
  * Konser
  * Yarışma
  * Toplantı
  * Panel
  * Düğün
  * Doğum Günü
  * Konferans
  * Sergi
  * Spor Müsabakası
  * Diğer (manuel giris)
  
- Etkinlik Tarihi: (zorunlu, date picker, geçmiş tarih seçilememeli)
- Başlangıç Saati: (zorunlu, time picker)
- Bitiş Saati: (zorunlu, time picker, başlangıçtan sonra olmalı)
- Açıklama: (opsiyonel, textarea, max 1000 karakter)
```

##### B) Etkinlik Alan Bilgileri
```
- Alan Tipi: (dropdown)
  * Açık Hava
  * Toplantı Salonu
  * Konferans Salonu
  * Düğün Salonu
  * Stadyum
  * Tiyatro
  * Diğer (manuel giriş)
  
- Toplam Kapasite: (otomatik hesaplanacak)
- Alan Boyutları: (opsiyonel)
  * Genişlik (metre)
  * Uzunluk (metre)
```

##### C) Oturum Planlaması (Dinamik Ekleme)
```
Her oturum tipi için:
- Oturum Tipi: (dropdown)
  * Masa (2 kişilik)
  * Masa (4 kişilik)
  * Masa (5 kişilik)
  * Masa (6 kişilik)
  * Masa (8 kişilik)
  * Masa (10 kişilik)
  * Masa (12 kişilik)
  * Tekli Koltuk
  * İkili Koltuk
  * VIP Loca
  * Özel Oturum (kapasiteyi belirle)
  
- Adet: (zorunlu, min 1)
- Kapasite: (otomatik doldurulur, düzenlenebilir)
- Fiyat: (opsiyonel, decimal)
- Renk Kodu: (görsel ayrım için)
```

**Otomatik Hesaplamalar:**
- Toplam Oturum Sayısı
- Toplam Kapasite
- Toplam Gelir Potansiyeli

##### D) Görsel Oturum Düzenleme (Drag & Drop)

**Özellikler:**

- Sahne konumu belirleme (üst/alt/sağ/sol)
- Her oturuma numara atama (otomatik/manuel)
- Oturumları sürükle-bırak ile yerleştirme
- Grid sistem (kolay hizalama)
- Zoom in/out özelliği
- Oturum renklerini değiştirme
- Oturum detaylarını gösterme (hover)
- Anlık veritabanı senkronizasyonu
- Geri al/İleri al (undo/redo)
- Şablon kaydetme ve yükleme

**Görsel Gösterim:**
```
[Sahne Alanı]
━━━━━━━━━━━━━━━━━━━━━━━━

[M1]  [M2]  [M3]  [M4]
 5kş   5kş   5kş   5kş

[M5]  [M6]  [M7]  [M8]
12kş  12kş  12kş  12kş

[VIP1] [VIP2]
 10kş   10kş
```

---

#### 2.2 ŞABLON SİSTEMİ

##### A) Oturum Düzeni Şablonları
```
Şablon Özellikleri:
- Şablon Adı: (zorunlu, max 100 karakter)
- Açıklama: (opsiyonel)
- Oturum konfigürasyonu (JSON)
- Sahne konumu
- Grid düzeni
- Renk şeması

Şablon İşlemleri:
- Mevcut düzeni şablon olarak kaydet
- Şablon listesini görüntüle
- Şablonu yükle (otomatik oturum oluşturma)
- Şablonu düzenle
- Şablonu sil
- Şablonu kopyala (versiyon oluştur)

Kullanım Senaryoları:
- Düğün Salonu Şablonu (20x 10kişilik masa)
- Konferans Şablonu (100x tekli koltuk)
- Konser Şablonu (VIP loca + sıralar)
```

##### B) Etkinlik Şablonları
```
Şablon İçeriği:
- Etkinlik tipi (konser, düğün, vb.)
- Varsayılan süre
- Alan tipi
- Oturum düzeni referansı
- Varsayılan fiyatlandırma

Kullanım:
- Yeni etkinlik oluştururken şablon seç
- Tüm ayarlar otomatik doldurulsun
- İstenirse özelleştir
- Zaman kazandırır
```

##### C) Şablon Yönetimi
- Şablon kategorileri (düğün, konser, toplantı)
- Sık kullanılanları işaretle
- Şablon önizleme
- Şablon paylaşma (export/import JSON)
- Versiyon kontrolü

---

#### 2.3 GELİŞMİŞ RAPORLAMA SİSTEMİ

##### A) Rapor Tipleri

**1. Genel Özet Raporu**
```
İçerik:
- Seçili tarih aralığı
- Toplam etkinlik sayısı
- Toplam rezervasyon sayısı
- Toplam katılımcı sayısı
- Check-in oranı (%)
- En popüler etkinlik tipleri
- Doluluk trendleri
```

**2. Etkinlik Detay Raporu**
```
İçerik:
- Etkinlik bilgileri
- Toplam/Rezerve/Boş oturum sayısı
- Rezervasyon listesi (telefon, ad/soyad, oturum)
- Check-in durumu
- İptal edilen rezervasyonlar
- Zaman çizelgesi (hangi tarihte kaç rezervasyon)
```

**3. Rezervasyon Analiz Raporu**
```
İçerik:
- Günlük/Haftalık/Aylık rezervasyon trendi
- En çok rezervasyon yapılan gün/saat
- Ortalama rezervasyon süresi (rezervasyon - etkinlik arası)
- İptal oranları
- Check-in oranları
```

**4. Doluluk Analiz Raporu**
```
İçerik:
- Etkinlik bazlı doluluk oranları
- Oturum tipi bazlı popülerlik
- Zaman serisinde doluluk grafiği
- Boş kalan oturumların analizi
- Kapasite kullanım verimliliği
```

**5. Müşteri Analiz Raporu**
```
İçerik:
- Tekrarlayan müşteriler (telefon bazlı)
- En çok rezervasyon yapan müşteriler
- Müşteri davranış analizi
- İptal yapan müşteriler
```

##### B) Rapor Özelleştirme
```
Filtreler:
- Tarih aralığı (başlangıç - bitiş)
- Etkinlik tipi
- Etkinlik durumu (tamamlanmış/aktif)
- Oturum tipi
- Check-in durumu

Gruplama:
- Günlük/Haftalık/Aylık/Yıllık
- Etkinlik bazlı
- Etkinlik tipi bazlı

Sıralama:
- Tarihe göre (artan/azalan)
- Rezervasyon sayısına göre
- Doluluk oranına göre
```

##### C) Grafik ve Görselleştirme
```
Grafik Tipleri:
- Pasta Grafiği: Doluluk oranı, etkinlik tipleri dağılımı
- Çubuk Grafiği: Etkinlik karşılaştırmaları
- Çizgi Grafiği: Zaman serisinde trend analizi
- Alan Grafiği: Kümülatif rezervasyon artışı
- Isı Haritası: Hangi gün/saatlerde en çok rezervasyon

Interaktif Özellikler:
- Zoom in/out
- Veri noktasına tıklayınca detay
- Grafik üzerinde filtreleme
- Karşılaştırma modu
```

##### D) Export İşlemleri
```
PDF Export:
- Profesyonel rapor şablonu
- Firma logosu ve bilgileri
- Grafikler (yüksek çözünürlük)
- Tablo verileri
- Özet ve yorumlar
- Sayfalandırma

Excel Export:
- Çoklu sheet (özet, detay, grafikler)
- Formüllü hücreler
- Pivot tablo hazır veri
- Koşullu biçimlendirme
- Grafikler

CSV Export:
- Ham veri export
- Virgül/noktalı virgül seçimi
- UTF-8 encoding (Türkçe karakter desteği)
- Kolay import için optimizasyon
```

##### E) Otomatik Raporlama (Gelecek Faz)
```
Zamanlanmış Raporlar:
- Günlük/Haftalık/Aylık otomatik rapor
- E-posta ile gönderim
- Rapor şablonları
- Alıcı listesi yönetimi
```

---

#### 2.4 REZERVASYON İŞLEMLERİ

##### A) Etkinlik Seçimi
- Aktif etkinlikler listesi (tarih sıralı)
- Hızlı geçiş (dropdown)
- Etkinlik detayları gösterme

##### B) Rezervasyon Oluşturma
```
Müşteri Bilgileri:
- Telefon: (zorunlu, 05XX XXX XX XX formatında)
- Ad: (isteğe bağlı)
- Soyad: (isteğe bağlı)

Rezervasyon Detayları:
- Oturum Seçimi: (görsel harita üzerinden)
- Kişi Sayısı: (zorunlu, kapasite kontrolü)
- Rezervasyon Notu: (opsiyonel)
```

**Otomatik İşlemler:**
- Benzersiz rezervasyon kodu oluşturma
- QR kod üretimi (check-in için)
- Doluluk durumu güncelleme

##### C) Rezervasyon Yönetimi
- Rezervasyonları listeleme (filtreleme/arama)
- Rezervasyon düzenleme
- Rezervasyon iptali
- Rezervasyon geçmişi
- Toplu işlemler

**Filtreler:**
- Tarih aralığı
- Durum (onaylı/beklemede/iptal)
- Ödeme durumu
- Müşteri adı/telefon
- Oturum numarası

##### D) Görsel Doluluk Haritası
```
Renk Kodları:
- Yeşil: Boş
- Kırmızı: Rezerve
- Gri: Devre dışı/kapalı
```

---

#### 2.5 KULLANICI YÖNETİMİ (Kontrolör)

##### A) Kontrolör Oluşturma
```
- Kullanıcı Adı: (zorunlu, benzersiz)
- Şifre: (zorunlu, güçlü şifre)
- Ad: (zorunlu)
- Soyad: (zorunlu)
- E-posta: (opsiyonel)
- Telefon: (opsiyonel)
- Rol: Kontrolör (sabit)
- Durum: Aktif/Pasif
```

##### B) Kontrolör Yönetimi
- Kontrolör tüm aktif etkinliklere erişebilir
- Giriş sonrası etkinlik seçimi yapar
- Seçilen etkinliğe göre bilgileri görüntüler

##### C) Kontrolör Listesi
- Filtreleme (aktif/pasif)
- Arama (ad/kullanıcı adı)
- Düzenleme/Silme
- Şifre sıfırlama

---

### MODÜL 3: KONTROLÖR PANELİ

#### 3.1 Giriş ve Etkinlik Seçimi
```
Login sonrası:
- Tamamlanmamış (aktif) etkinlikler listesi
- Etkinlik seçimi (dropdown veya kart görünümü)
- Seçilen etkinlik bilgileri özeti
- Hızlı istatistikler
```

#### 3.2 Dashboard (Ana Sayfa)
```
İstatistik Kartları:
- Toplam Kapasite
- Rezerve Edilen Koltuk
- Boş Koltuk
- Doluluk Oranı (%)
- Güncel Check-in Sayısı

Grafikler:
- Doluluk grafiği (pasta chart)
- Günlük rezervasyon trendi
```

#### 3.3 Rezervasyon Görüntüleme
```
Tablo Görünümü:
- Rezervasyon No
- Müşteri Telefon
- Ad Soyad (varsa)
- Oturum No
- Kişi Sayısı
- Check-in Durumu
- Detay Butonu

Arama/Filtreler:
- Telefon numarası
- Ad/Soyad
- Rezervasyon kodu
- Oturum numarası
- Check-in durumu
```

#### 3.4 Görsel Doluluk Haritası
- Oturum düzeni görüntüleme (read-only)
- Renk kodlu doluluk durumu
- Hover ile rezervasyon detayları
- Oturuma tıklayarak detaylı bilgi
- Tam ekran modu
- Yazdırma özelliği

#### 3.5 Check-in İşlemleri

**Yöntem 1: QR Kod Okuma**
```
- Kamera ile QR kod okuma
- Otomatik rezervasyon bulma
- Müşteri bilgilerini gösterme (telefon, ad/soyad, oturum)
- Etkinlik alanı krokisinde oturum yerini vurgulama
- Check-in onaylama
```

**Yöntem 2: Manuel Arama**
```
- Telefon numarası ile arama
- Ad/Soyad ile arama
- Rezervasyon kodu ile arama
- Sonuçları listeleme
- Müşteri seçimi
- Rezervasyon detayları ve oturum yeri gösterme
- Check-in onaylama
```

**Check-in Sonrası:**
- Durum güncelleme
- İşlem log kaydetme
- Başarı mesajı gösterme

#### 3.6 Raporlar
```
Rapor Tipleri:
- Genel Özet Raporu
- Rezervasyon Detay Raporu
- Check-in Raporu
- Müşteri Listesi
- Doluluk Raporu

Çıktı Formatları:
- PDF
- Excel
- CSV
```

---

### MODÜL 4: MÜŞTERİ CHECK-IN EKRANI (Kapı Kontrol)

#### 4.1 Müşteri Kendini Kontrol Etme
```
Giriş Yöntemleri:

1. QR Kod Okutma:
   - Müşteri QR kodunu okutturucu cihaza okuttur
   - Sistem otomatik rezervasyonu bul
   - Bilgileri göster

2. Manuel Arama:
   - Telefon numarası gir
   - Ad/Soyad gir (opsiyonel)
   - Ara butonuna tıkla
   - Sonuçları listele

Gösterilecek Bilgiler:
- ✅ Rezervasyon Onaylandı
- Müşteri: [Ad Soyad] / [Telefon]
- Oturum Numarası: [M12]
- Kişi Sayısı: [5 kişi]
- Etkinlik Alan Krokisi (oturum vurgulu)
```

**Ekran Özellikleri:**
- Büyük fontlar (kolay okunabilir)
- Dokunmatik ekran desteği
- Kiosk modu (tam ekran)
- Otomatik sıfırlama (30 saniye sonra)
- Türkçe dil desteği

---

## 🗄️ VERİ MODELİ (Veritabanı Yapısı)

### 1. companies (Firmalar)
```sql
- id (PK)
- name (VARCHAR 200)
- phone (VARCHAR 20)
- email (VARCHAR 100)
- address (TEXT)
- logo_path (VARCHAR 255)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 2. users (Kullanıcılar)
```sql
- id (PK)
- company_id (FK)
- username (VARCHAR 50, UNIQUE)
- password_hash (VARCHAR 255)
- first_name (VARCHAR 100)
- last_name (VARCHAR 100)
- email (VARCHAR 100)
- phone (VARCHAR 20)
- role (ENUM: 'admin', 'controller')
- status (ENUM: 'active', 'inactive')
- last_login (TIMESTAMP)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 3. seating_layout_templates (Oturum Düzeni Şablonları)
```sql
- id (PK)
- company_id (FK)
- name (VARCHAR 100)
- description (TEXT)
- category (VARCHAR 50, örn: 'düğün', 'konser', 'toplantı')
- stage_position (ENUM: 'top', 'bottom', 'left', 'right')
- configuration (JSONB, oturum yapılandırması)
- is_favorite (BOOLEAN, default false)
- usage_count (INT, default 0)
- created_by (FK users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 4. event_templates (Etkinlik Şablonları)
```sql
- id (PK)
- company_id (FK)
- name (VARCHAR 100)
- event_type (VARCHAR 50)
- default_duration_hours (INT)
- venue_type (VARCHAR 100)
- seating_layout_template_id (FK, nullable)
- settings (JSONB, varsayılan ayarlar)
- is_favorite (BOOLEAN, default false)
- usage_count (INT, default 0)
- created_by (FK users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 5. events (Etkinlikler)
```sql
- id (PK)
- company_id (FK)
- event_template_id (FK, nullable)
- name (VARCHAR 200)
- type (VARCHAR 50)
- description (TEXT)
- event_date (DATE)
- start_time (TIME)
- end_time (TIME)
- venue_type (VARCHAR 100)
- venue_width (DECIMAL)
- venue_length (DECIMAL)
- stage_position (ENUM: 'top', 'bottom', 'left', 'right')
- total_capacity (INT)
- status (ENUM: 'draft', 'active', 'completed', 'cancelled')
- created_by (FK users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 6. seating_types (Oturum Tipleri - Sabit Şablon)
```sql
- id (PK)
- name (VARCHAR 100)
- capacity (INT)
- icon (VARCHAR 50)
```

### 7. event_seatings (Etkinlik Oturumları)
```sql
- id (PK)
- event_id (FK)
- seating_type_id (FK)
- seat_number (VARCHAR 20)
- capacity (INT)
- price (DECIMAL)
- position_x (INT)
- position_y (INT)
- color_code (VARCHAR 7)
- status (ENUM: 'available', 'reserved', 'disabled')
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 8. reservations (Rezervasyonlar)
```sql
- id (PK)
- event_id (FK)
- event_seating_id (FK)
- phone (VARCHAR 20, zorunlu)
- first_name (VARCHAR 100, nullable)
- last_name (VARCHAR 100, nullable)
- reservation_code (VARCHAR 20, UNIQUE)
- qr_code_path (VARCHAR 255)
- number_of_people (INT)
- notes (TEXT)
- status (ENUM: 'active', 'cancelled')
- checked_in (BOOLEAN, default false)
- checked_in_at (TIMESTAMP)
- checked_in_by (FK users)
- created_by (FK users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- cancelled_at (TIMESTAMP)
- cancelled_by (FK users)
```

### 9. activity_logs (İşlem Logları)
```sql
- id (PK)
- user_id (FK)
- event_id (FK, nullable)
- action (VARCHAR 100)
- description (TEXT)
- ip_address (VARCHAR 45)
- user_agent (VARCHAR 255)
- created_at (TIMESTAMP)
```

### 10. report_schedules (Zamanlanmış Raporlar - Gelecek Faz)
```sql
- id (PK)
- company_id (FK)
- name (VARCHAR 100)
- report_type (VARCHAR 50)
- schedule (VARCHAR 50, örn: 'daily', 'weekly', 'monthly')
- filters (JSONB)
- recipients (JSONB, e-posta listesi)
- is_active (BOOLEAN)
- last_run_at (TIMESTAMP)
- next_run_at (TIMESTAMP)
- created_by (FK users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

---

**NOT:** Toplam 10 tablo (2 yeni şablon tablosu + 1 rapor tablosu eklendi)

---

## 🛡️ GÜVENLİK ÖNLEMLERİ

### 1. Kimlik Doğrulama
- Güçlü şifre politikası (min 8 karakter, büyük/küçük harf, sayı, özel karakter)
- Şifre hash'leme (bcrypt / werkzeug.security)
- Session yönetimi (Flask-Session)
- JWT token tabanlı kimlik doğrulama (Flask-JWT-Extended)
- CSRF koruması (Flask-WTF)

### 2. Yetkilendirme
- Rol tabanlı erişim kontrolü (RBAC)
- Flask decorator ile route koruması
- API endpoint güvenliği
- CSRF koruması (Flask-WTF)
- XSS koruması (Jinja2 auto-escape)

### 3. Veri Güvenliği
- SQL Injection koruması (SQLAlchemy ORM)
- Input validasyonu (Flask-WTF, Marshmallow)
- Output sanitizasyonu
- Telefon numarası formatı kontrolü
- GDPR uyumluluğu (veri minimizasyonu)

### 4. İşlem Güvenliği
- Rate limiting (Flask-Limiter)
- IP bazlı kısıtlama
- Detaylı loglama (Flask-Logging)
- Hatalı giriş takibi
- Otomatik hesap kilitleme (opsiyonel)

### 5. Yedekleme
- Otomatik günlük PostgreSQL yedekleme (pg_dump)
- Dosya yedekleme (QR kodlar, logolar)
- Disaster recovery planı
- Yedek geri yükleme prosedürü

---

## 🚀 TEKNİK GEREKSİNİMLER

### Backend Stack (Python Flask)
```
Framework & Extensions:
- Flask 3.x (web framework)
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (veritabanı migration)
- Flask-Login (session yönetimi)
- Flask-JWT-Extended (JWT token)
- Flask-WTF (form validation & CSRF)
- Flask-CORS (API için)
- Flask-Limiter (rate limiting)
- Marshmallow (serialization/validation)

Veritabanı:
- PostgreSQL 15+ (production)
- psycopg2-binary (PostgreSQL adapter)

QR Kod & Utility:
- qrcode (QR kod oluşturma)
- Pillow (görsel işleme)
- python-dotenv (environment variables)
- phonenumbers (telefon doğrulama)

Raporlama & Analytics:
- ReportLab (PDF oluşturma)
- WeasyPrint (HTML to PDF - alternatif)
- openpyxl (Excel export)
- xlsxwriter (Excel - alternatif)
- pandas (veri manipülasyonu ve analiz)
- matplotlib / plotly (grafik oluşturma)

Şablon & JSON:
- jsonschema (JSON validasyonu)
```

### Frontend Stack (Modern & Gelişmiş)

**Seçenek 1: React Ecosystem (Önerilen)**
```
Core:
- React 18+ (UI library)
- TypeScript (type safety)
- Vite (build tool, hızlı development)

State Management:
- Zustand / Redux Toolkit (global state)
- React Query / TanStack Query (server state)

UI Framework:
- Material-UI (MUI) / Ant Design / Chakra UI
- Tailwind CSS (utility-first CSS)

Drag & Drop:
- @dnd-kit/core (modern drag & drop)
- react-beautiful-dnd (alternatif)

Charts & Graphs:
- Recharts / Chart.js / ApexCharts

Forms & Validation:
- React Hook Form
- Zod / Yup (validation)

QR Code:
- react-qr-code (QR kod gösterme)
- html5-qrcode (QR kod okuma - kamera)

Diğer:
- React Router v6 (routing)
- Axios (HTTP client)
- date-fns (tarih işlemleri)
- react-toastify (notification)
```

**Seçenek 2: Vue.js Ecosystem**
```
Core:
- Vue 3 + TypeScript
- Vite

UI Framework:
- Vuetify / Element Plus / Ant Design Vue

State: Pinia
Drag & Drop: Vue Draggable Plus
```

**Seçenek 3: Server-Side Rendering (SSR)**
```
- Jinja2 Templates (Flask native)
- Bootstrap 5 / Tailwind CSS
- Alpine.js (minimal JS framework)
- HTMX (modern HTML interactions)
- Sortable.js (drag & drop)
```

### Veritabanı & Cache
```
Production Database:
- PostgreSQL 15+ (ana veritabanı)
- TimescaleDB (zaman serisi veriler için - opsiyonel)

Development:
- PostgreSQL (Docker)
- SQLite (lokal test - opsiyonel)

Cache & Session:
- Redis (session storage, cache)
- Flask-Session + Redis
```

### DevOps & Deployment
```
Containerization:
- Docker (uygulama container)
- Docker Compose (development)

Web Server:
- Gunicorn (WSGI server)
- Nginx (reverse proxy, static files)

Process Management:
- Supervisor / systemd

CI/CD:
- GitHub Actions
- GitLab CI

Monitoring:
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- PostgreSQL slow query log
```

### Proje Yapısı (Flask)
```
rezervasyon-sistemi/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # SQLAlchemy modeller
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── template.py       # Şablon modelleri
│   │   ├── seating.py
│   │   └── reservation.py
│   ├── routes/               # Blueprint'ler
│   │   ├── __init__.py
│   │   ├── auth.py           # Login/logout
│   │   ├── admin.py          # Admin panel
│   │   ├── event.py          # Etkinlik yönetimi
│   │   ├── template.py       # Şablon yönetimi
│   │   ├── reservation.py    # Rezervasyon
│   │   ├── report.py         # Raporlama
│   │   ├── controller.py     # Kontrolör paneli
│   │   └── checkin.py        # Check-in ekranı
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── event_service.py
│   │   ├── template_service.py
│   │   ├── reservation_service.py
│   │   ├── qr_service.py
│   │   └── report_service.py
│   ├── utils/                # Yardımcı fonksiyonlar
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── decorators.py     # @login_required, @admin_required
│   │   ├── chart_generator.py  # Grafik oluşturma
│   │   └── helpers.py
│   ├── templates/            # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── templates/        # Şablon yönetimi
│   │   ├── reports/          # Rapor sayfaları
│   │   ├── controller/
│   │   └── checkin/
│   ├── static/               # Static files
│   │   ├── css/
│   │   ├── js/
│   │   ├── images/
│   │   ├── uploads/
│   │   └── reports/          # Oluşturulan raporlar
│   └── config.py             # Konfigürasyon
├── migrations/               # Alembic migrations
├── tests/                    # Test dosyaları
│   ├── test_auth.py
│   ├── test_event.py
│   ├── test_template.py
│   ├── test_reservation.py
│   └── test_report.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── requirements.txt
├── requirements-dev.txt
├── run.py                    # Uygulama entry point
└── README.md
```

---



---

## 🎨 KULLANICI DENEYIMI (UX) İLKELERİ

### 1. Basitlik
- Sezgisel navigasyon
- Minimum tıklama
- Açık ve net etiketler
- Yardımcı ipuçları (tooltips)

### 2. Geri Bildirim
- Başarılı işlem mesajları
- Hata mesajları (anlaşılır)
- Yükleniyor göstergeleri
- İşlem onay dialogs

### 3. Tutarlılık
- Tek bir tasarım dili
- Renk paleti tutarlılığı
- Buton stilleri
- Form düzenleri

### 4. Erişilebilirlik
- Klavye navigasyonu
- Screen reader desteği
- Yüksek kontrast modu
- Responsive tasarım

### 5. Performans
- Hızlı sayfa yüklemeleri (<3s)
- Lazy loading
- Image optimization
- Minimum HTTP istekleri

---



### 🎯 Temel Özellikler (Güncellenmiş):
1. ✅ Sistem kurulumu (firma + admin)
2. ✅ Etkinlik planlama (drag & drop)
3. ✅ **Şablon sistemi (oturum + etkinlik)**
4. ✅ Rezervasyon (sadece telefon)
5. ✅ QR kod sistemi
6. ✅ Kontrolör paneli (etkinlik seçimi)
7. ✅ Müşteri check-in ekranı
8. ✅ **Gelişmiş raporlama (PDF/Excel/CSV + Grafikler)**

### 🛠️ Teknoloji Stack:
```
Backend:  Python 3.11+ / Flask / PostgreSQL / SQLAlchemy
Frontend: React + TypeScript + Material-UI (önerilen)
          veya Jinja2 + Bootstrap 5 + Alpine.js
Hosting:  Docker + Nginx + Gunicorn
Analytics: pandas + matplotlib/plotly
Reports:   ReportLab + openpyxl
```

- 

### 💪 Başarı İçin:
- ✅ Güvenlik öncelikli yaklaşım
- ✅ Kullanıcı deneyimi odaklı tasarım
- ✅ Test-driven development
- ✅ Temiz kod prensipleri
- ✅ İyi dokümantasyon
- ✅ Şablon sistemi ile hız
- ✅ Detaylı analitik ve raporlama



---

**Proje Sahibi:** Erkan  
**Tarih:** 05.11.2025  
**Versiyon:** 3.0 
