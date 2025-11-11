@echo off
chcp 65001 >nul
title Rezervasyon Sistemi - Basit Başlatıcı

echo.
echo ========================================
echo   Rezervasyon Sistemi
echo   Docker OLMADAN Çalışıyor
echo ========================================
echo.

REM .env dosyasını kontrol et
if not exist ".env" (
    echo 📝 .env dosyası oluşturuluyor...
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo REDIS_ENABLED=false > .env
        echo SESSION_TYPE=filesystem >> .env
        echo DATABASE_URL=postgresql://postgres:password@localhost/rezervasyon_db >> .env
    )
    echo ✅ .env dosyası oluşturuldu
    echo.
)

REM Redis'i devre dışı bırak
echo 📁 Filesystem session kullanılacak (Redis YOK)
echo.

REM .env dosyasında Redis'i kapat
powershell -Command "(Get-Content .env) -replace '^REDIS_ENABLED=.*', 'REDIS_ENABLED=false' | Set-Content .env"
powershell -Command "if ((Get-Content .env) -notmatch 'REDIS_ENABLED') { Add-Content .env 'REDIS_ENABLED=false' }"

REM Virtual environment kontrolü
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment aktifleştiriliyor...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  Virtual environment bulunamadı
    echo.
    set /p create_venv="Virtual environment oluşturmak istiyor musunuz? (E/H) [E]: "
    if /i "%create_venv%"=="" set create_venv=E
    if /i "%create_venv%"=="E" (
        echo.
        echo 📦 Virtual environment oluşturuluyor...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo.
        echo 📦 Bağımlılıklar yükleniyor...
        pip install -r requirements.txt
        echo.
        echo ✅ Kurulum tamamlandı!
    )
)

echo.
echo 🚀 Flask uygulaması başlatılıyor...
echo 📍 http://localhost:5000
echo.
echo ⚠️  Durdurmak için Ctrl+C kullanın
echo.

REM Flask'ı başlat
python run.py

pause
