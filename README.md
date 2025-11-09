# Etkinlik Rezervasyon Yönetim Sistemi# Etkinlik Rezervasyon Y�netim Sistemi



Modern, kapsamlı bir etkinlik rezervasyon yönetim sistemi. Flask, PostgreSQL ve Redis ile geliştirilmiştir.Modern, kapsaml� bir etkinlik rezervasyon y�netim sistemi. Flask, PostgreSQL ve Redis ile geli�tirilmi�tir.



## 🚀 Özellikler## 🚀 �zellikler



### ✨ Ana Özellikler### ✨ Ana �zellikler

- **Görsel Koltuk Düzenleme**: Drag-and-drop koltuk yerleştirme editörü- **G�rsel Koltuk D�zenleme**: Drag-and-drop koltuk yerle�tirme edit�r�

- **Şablon Sistemi**: Yeniden kullanılabilir etkinlik ve koltuk düzeni şablonları- **�ablon Sistemi**: Yeniden kullan�labilir etkinlik ve koltuk d�zeni �ablonlar�

- **QR Kod Sistemi**: Her rezervasyon için otomatik QR kod üretimi- **QR Kod Sistemi**: Her rezervasyon i�in otomatik QR kod �retimi

- **Check-in Sistemi**: QR kod tarama veya manuel check-in- **Check-in Sistemi**: QR kod tarama veya manuel check-in

- **Gelişmiş Raporlama**: PDF, Excel ve CSV raporları- **Geli�mi� Raporlama**: PDF, Excel ve CSV raporlar�

- **Türkçe Arayüz**: Tam Türkçe kullanıcı arayüzü- **T�rk�e Aray�z**: Tam T�rk�e kullan�c� aray�z�



### 👥 Kullanıcı Rolleri### 👥 Kullan�c� Rolleri

- **Sistem Yöneticisi (Admin)**: Tam sistem erişimi- **Sistem Y�neticisi (Admin)**: Tam sistem eri�imi

- **Kontrolör (Controller)**: Etkinlik seçimi ve check-in yetkisi- **Kontrol�r (Controller)**: Etkinlik se�imi ve check-in yetkisi



### 📊 Raporlama### 📊 Raporlama

- Genel özet raporları- Genel �zet raporlar�

- Etkinlik detay raporları- Etkinlik detay raporlar�

- Rezervasyon analizi- Rezervasyon analizi

- Check-in istatistikleri- Check-in istatistikleri

- Excel/PDF export- Excel/PDF export



## 🛠️ Teknoloji Stack## 🛠️ Teknoloji Stack



- **Backend**: Python 3.11, Flask 3.x- **Backend**: Python 3.11, Flask 3.x

- **Veritabanı**: PostgreSQL 15+- **Veritaban�**: PostgreSQL 15+

- **ORM**: SQLAlchemy- **ORM**: SQLAlchemy

- **Cache/Session**: Redis- **Cache/Session**: Redis

- **Kimlik Doğrulama**: Flask-Login, Flask-JWT-Extended- **Kimlik Do�rulama**: Flask-Login, Flask-JWT-Extended

- **QR Kodlar**: qrcode + Pillow- **QR Kodlar**: qrcode + Pillow

- **Frontend**: Bootstrap 5, jQuery- **Frontend**: Bootstrap 5, jQuery

- **Deployment**: Docker + Docker Compose- **Deployment**: Docker + Docker Compose



## 📦 Kurulum## 📦 Kurulum



### Docker ile (Önerilen)### Docker ile (�nerilen)



1. Repoyu klonlayın:1. Repoyu klonlay�n:

```bash```bash

git clone <repo-url>git clone <repo-url>

cd rezervasyon-sistemicd rezervasyon-sistemi

``````



2. Docker Compose ile çalıştırın:2. Docker Compose ile �al��t�r�n:

```bash```bash

docker-compose up -ddocker-compose up -d

``````



3. Uygulamaya erişim:3. Uygulamaya eri�im:

``````

http://localhost:5000http://localhost:5000

``````



### Manuel Kurulum### Manuel Kurulum



1. Sanal ortam oluşturun:1. Sanal ortam olu�turun:

```bash```bash

python -m venv venvpython -m venv venv

source venv/bin/activate  # Linux/Macsource venv/bin/activate  # Linux/Mac

# veya# veya

venv\Scripts\activate  # Windowsvenv\Scripts\activate  # Windows

``````



2. Bağımlılıkları yükleyin:2. Ba��ml�l�klar� y�kleyin:

```bash```bash

pip install -r requirements.txtpip install -r requirements.txt

``````



3. Veritabanı ve Redis kurun:3. Veritaban� ve Redis kurun:

```bash```bash

# PostgreSQL ve Redis kurulu olduğundan emin olun# PostgreSQL ve Redis kurulu oldu�undan emin olun

# .env dosyasını ayarlayın# .env dosyas�n� ayarlay�n

cp .env.example .envcp .env.example .env

``````



4. Uygulamayı çalıştırın:4. Uygulamay� �al��t�r�n:

```bash```bash

python run.pypython run.py

``````



## 🔧 Yapılandırma## 🔧 Yap�land�rma



`.env` dosyasında aşağıdaki değişkenleri ayarlayın:`.env` dosyas�nda a�a��daki de�i�kenleri ayarlay�n:



```env```env

SECRET_KEY=güçlü-bir-secret-keySECRET_KEY=g��l�-bir-secret-key

DATABASE_URL=postgresql://user:pass@localhost/rezervasyon_dbDATABASE_URL=postgresql://user:pass@localhost/rezervasyon_db

REDIS_URL=redis://localhost:6379/0REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=güçlü-bir-jwt-keyJWT_SECRET_KEY=g��l�-bir-jwt-key

``````



## 🎯 Kullanım## 🎯 Kullan�m



### İlk Kurulum### �lk Kurulum

1. Uygulamaya ilk kez eriştiğinizde kurulum sihirbazı açılır1. Uygulamaya ilk kez eri�ti�inizde kurulum sihirbaz� a��l�r

2. Şirket bilgilerinizi girin2. �irket bilgilerinizi girin

3. İlk admin kullanıcısını oluşturun3. �lk admin kullan�c�s�n� olu�turun

4. Giriş yapın4. Giri� yap�n



### Admin Kullanımı### Admin Kullan�m�

1. Etkinlik oluşturun ve düzenleyin1. Etkinlik olu�turun ve d�zenleyin

2. Görsel editörle koltuk düzenini oluşturun2. G�rsel edit�rle koltuk d�zenini olu�turun

3. Rezervasyonları yönetin3. Rezervasyonlar� y�netin

4. Raporları görüntüleyin4. Raporlar� g�r�nt�leyin



### Kontrolör Kullanımı### Kontrol�r Kullan�m�

1. Giriş yapın1. Giri� yap�n

2. Aktif etkinlik seçin2. Aktif etkinlik se�in

3. Rezervasyonları görüntüleyin3. Rezervasyonlar� g�r�nt�leyin

4. QR kod tarayarak check-in yapın4. QR kod tarayarak check-in yap�n



## 📁 Proje Yapısı## 📁 Proje Yap�s�



``````

rezervasyon-sistemi/rezervasyon-sistemi/

├── app/├── app/

│   ├── models/          # Veritabanı modelleri│   ├── models/          # Veritaban� modelleri

│   ├── routes/          # Flask blueprint'leri│   ├── routes/          # Flask blueprint'leri

│   ├── services/        # İş mantığı│   ├── services/        # �� mant���

│   ├── utils/           # Yardımcı fonksiyonlar│   ├── utils/           # Yard�mc� fonksiyonlar

│   ├── templates/       # Jinja2 şablonları│   ├── templates/       # Jinja2 �ablonlar�

│   └── static/          # CSS, JS, resimler│   └── static/          # CSS, JS, resimler

├── tests/               # Test dosyaları├── tests/               # Test dosyalar�

├── docker/              # Docker yapılandırması├── docker/              # Docker yap�land�rmas�

├── migrations/          # DB migrasyonları├── migrations/          # DB migrasyonlar�

└── run.py              # Uygulama giriş noktası└── run.py              # Uygulama giri� noktas�

``````



## 🧪 Test## 🧪 Test



```bash```bash

# Tüm testleri çalıştır# T�m testleri �al��t�r

pytestpytest



# Kapsam raporu ile# Kapsam raporu ile

pytest --cov=app tests/pytest --cov=app tests/

``````



## 📊 Veritabanı Şeması## 📊 Veritaban� �emas�



Ana tablolar:Ana tablolar:

- `companies`: Şirket bilgileri- `companies`: �irket bilgileri

- `users`: Kullanıcılar (admin/controller)- `users`: Kullan�c�lar (admin/controller)

- `events`: Etkinlikler- `events`: Etkinlikler

- `event_seatings`: Etkinlik koltuk düzeni- `event_seatings`: Etkinlik koltuk d�zeni

- `reservations`: Rezervasyonlar- `reservations`: Rezervasyonlar

- `seating_types`: Koltuk türleri- `seating_types`: Koltuk t�rleri

- `seating_layout_templates`: Koltuk düzeni şablonları- `seating_layout_templates`: Koltuk d�zeni �ablonlar�

- `event_templates`: Etkinlik şablonları- `event_templates`: Etkinlik �ablonlar�

- `activity_logs`: Aktivite logları- `activity_logs`: Aktivite loglar�



## 🔐 Güvenlik

### Şifre Politikası

Sistem güçlü şifre politikası uygular. Tüm şifreler aşağıdaki gereksinimleri karşılamalıdır:

- **Minimum Uzunluk**: En az 8 karakter
- **Büyük Harf**: En az 1 büyük harf (A-Z)
- **Küçük Harf**: En az 1 küçük harf (a-z)
- **Rakam**: En az 1 rakam (0-9)
- **Özel Karakter**: En az 1 özel karakter (!@#$%^&*()_+-=[]{}|;:,.<>?)

**Örnek Geçerli Şifreler:**
- `Password123!`
- `Secure@Pass1`
- `MyP@ssw0rd`

### Güvenlik Özellikleri

- **CSRF Koruması**: Tüm form işlemlerinde CSRF token kontrolü
- **SQL Injection Koruması**: SQLAlchemy ORM ile parametreli sorgular
- **XSS Koruması**: 
  - Kullanıcı girişlerinde HTML sanitizasyon
  - Template'lerde otomatik escape
  - Güvenli HTML filtreleri (safe_text, safe_html)
- **Rate Limiting**: API endpoint'lerinde istek sınırlaması
- **Security Headers**:
  - Content-Security-Policy
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Strict-Transport-Security (Production)
- **Session Güvenliği**: Redis tabanlı güvenli oturum yönetimi
- **Input Validation**: Marshmallow şemaları ile veri doğrulama

### Şifre Değiştirme

Kullanıcılar şifrelerini şu yollarla değiştirebilir:

1. **Kendi Şifresini Değiştirme**: 
   - Profil > Şifre Değiştir menüsünden
   - Mevcut şifre doğrulaması gereklidir

2. **Admin Kullanıcı Şifresi Değiştirme**:
   - Admin panelinden herhangi bir kullanıcının şifresini sıfırlayabilir
   - Şifre politikası otomatik olarak kontrol edilir

## � Dokümantasyon

Detaylı dokümantasyon için aşağıdaki kaynakları inceleyebilirsiniz:

- **[Güvenlik En İyi Uygulamaları](docs/SECURITY_BEST_PRACTICES.md)**: Kapsamlı güvenlik rehberi
  - Input validation DO/DON'T örnekleri
  - Şifre güvenliği yönergeleri
  - XSS, CSRF, SQL injection koruması
  - Security header'lar açıklaması
  - Güvenlik kontrol listeleri
  - Olay müdahale prosedürü

- **[Schema Kullanım Rehberi](docs/SCHEMA_USAGE.md)**: Marshmallow şema dokümantasyonu
  - Tüm şemaların detaylı açıklaması
  - Field validation kuralları
  - Örnek kullanım senaryoları
  - Hata yönetimi pattern'leri
  - Yeni şema oluşturma adımları

- **[Migration Rehberi](docs/MIGRATION_GUIDE.md)**: Mevcut sistemlerden geçiş rehberi
  - Breaking changes listesi
  - Adım adım migration prosedürü
  - Route ve template güncellemeleri
  - Test senaryoları
  - Rollback prosedürü
  - Sıkça sorulan sorular (FAQ)

## 🧪 Testler

### Test Yapısı

Proje kapsamlı test suite'ine sahiptir:

```bash
tests/
├── test_models.py              # Model testleri (15 test)
├── test_auth.py                # Authentication testleri (8 test)
├── test_validators.py          # Validator testleri (7 test)
├── test_schemas.py             # Schema validation testleri (15 test)
├── test_password_validation.py # Şifre güvenliği testleri (10 test)
├── test_xss_simple.py          # XSS koruması testleri (6 test)
├── test_security_headers.py    # Security header testleri (14 test)
└── test_route_protection.py    # Route koruması testleri (15+ test)
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
pytest

# Kapsam raporu ile
pytest --cov=app tests/

# Belirli bir test dosyasını çalıştır
pytest tests/test_schemas.py -v

# Belirli bir testi çalıştır
pytest tests/test_password_validation.py::test_password_too_short -v
```

### Test Sonuçları

- **Toplam Test Sayısı**: 90+ test
- **Model Testleri**: 15/15 ✅
- **Authentication Testleri**: 8/8 ✅
- **Validator Testleri**: 7/7 ✅
- **Schema Testleri**: 15/15 ✅
- **Password Testleri**: 10/10 ✅
- **XSS Testleri**: 6/6 ✅
- **Security Header Testleri**: 14 (DB yapılandırması gerekli)
- **Route Protection Testleri**: 15+ (DB yapılandırması gerekli)

## �📝 Lisans



Bu proje MIT lisansı altında lisanslanmıştır.Bu proje MIT lisans� alt�nda lisanslanm��t�r.



## 🤝 Katkıda Bulunma## 🤝 Katk�da Bulunma



1. Fork'layın1. Fork'lay�n

2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)2. Feature branch olu�turun (`git checkout -b feature/yeni-ozellik`)

3. Commit'leyin (`git commit -am 'Yeni özellik eklendi'`)3. Commit'leyin (`git commit -am 'Yeni �zellik eklendi'`)

4. Push'layın (`git push origin feature/yeni-ozellik`)4. Push'lay�n (`git push origin feature/yeni-ozellik`)

5. Pull Request oluşturun5. Pull Request olu�turun



## 📞 İletişim## 📞 �leti�im



Sorularınız için issue açabilirsiniz.Sorular�n�z i�in issue a�abilirsiniz.

