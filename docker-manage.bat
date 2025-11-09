@echo off
REM Rezervasyon Sistemi - Docker Yönetim Script (Windows)
REM Kullanım: docker-manage.bat [komut]

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="shell" goto shell
if "%1"=="db-shell" goto db-shell
if "%1"=="db-upgrade" goto db-upgrade
if "%1"=="db-backup" goto db-backup
if "%1"=="seed" goto seed
if "%1"=="test" goto test
if "%1"=="qr-generate" goto qr-generate
if "%1"=="clean" goto clean
if "%1"=="status" goto status
if "%1"=="init" goto init
goto unknown

:help
echo.
echo 🚀 Rezervasyon Sistemi - Docker Komutları
echo.
echo Kullanım: docker-manage.bat [komut]
echo.
echo Komutlar:
echo   build         - Docker image'lerini oluştur
echo   up            - Container'ları başlat
echo   down          - Container'ları durdur
echo   restart       - Container'ları yeniden başlat
echo   logs          - Logları göster
echo   shell         - App container'a shell aç
echo   db-shell      - PostgreSQL shell aç
echo   db-upgrade    - Migration'ları uygula
echo   db-backup     - Veritabanı yedeği al
echo   seed          - Örnek veriler yükle
echo   test          - Testleri çalıştır
echo   qr-generate   - QR kodları oluştur
echo   clean         - Container'ları temizle
echo   status        - Container durumunu göster
echo   init          - İlk kurulum (build + up + migrate + seed)
echo.
goto end

:build
echo 📦 Docker image'leri oluşturuluyor...
docker-compose build
echo ✅ Image'ler oluşturuldu!
goto end

:up
echo 🚀 Container'lar başlatılıyor...
docker-compose up -d
echo ✅ Container'lar başlatıldı!
echo 🌐 Uygulama: http://localhost:5000
goto end

:down
echo ⏹️  Container'lar durduruluyor...
docker-compose down
echo ✅ Container'lar durduruldu!
goto end

:restart
echo 🔄 Container'lar yeniden başlatılıyor...
docker-compose restart
echo ✅ Yeniden başlatıldı!
goto end

:logs
echo 📜 Loglar gösteriliyor... (Çıkmak için Ctrl+C)
docker-compose logs -f
goto end

:shell
echo 🐚 App container shell açılıyor...
docker-compose exec app bash
goto end

:db-shell
echo 🐘 PostgreSQL shell açılıyor...
docker-compose exec db psql -U postgres -d rezervasyon_db
goto end

:db-upgrade
echo ⬆️  Migration'lar uygulanıyor...
docker-compose exec app flask db upgrade
echo ✅ Migration'lar uygulandı!
goto end

:db-backup
echo 💾 Veritabanı yedeği alınıyor...
if not exist backups mkdir backups
docker-compose exec -T db pg_dump -U postgres rezervasyon_db > backups\backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
echo ✅ Yedek alındı!
goto end

:seed
echo 🌱 Örnek veriler yükleniyor...
docker-compose exec app python seed_data.py
echo ✅ Örnek veriler yüklendi!
goto end

:test
echo 🧪 Testler çalıştırılıyor...
docker-compose exec app pytest -v
goto end

:qr-generate
echo 🔲 QR kodları oluşturuluyor...
docker-compose exec app python generate_qr_codes.py
echo ✅ QR kodları oluşturuldu!
goto end

:clean
echo 🧹 Container'lar temizleniyor...
docker-compose down -v
echo ✅ Temizlendi!
goto end

:status
echo 📊 Container durumu:
docker-compose ps
goto end

:init
echo 🚀 İlk kurulum başlatılıyor...
echo.
echo 1/4 - Docker image'leri oluşturuluyor...
docker-compose build
echo.
echo 2/4 - Container'lar başlatılıyor...
docker-compose up -d
timeout /t 10 /nobreak > nul
echo.
echo 3/4 - Veritabanı migration'ları uygulanıyor...
docker-compose exec app flask db upgrade
echo.
echo 4/4 - Örnek veriler yükleniyor...
docker-compose exec app python seed_data.py
echo.
echo ✅ Sistem başarıyla kuruldu!
echo 🌐 Uygulama: http://localhost:5000
echo.
echo Varsayılan giriş bilgileri:
echo   Kullanıcı: admin
echo   Şifre: Admin123!
goto end

:unknown
echo ❌ Bilinmeyen komut: %1
echo Yardım için: docker-manage.bat help
goto end

:end
