@echo off
chcp 65001 >nul
title Rezervasyon Sistemi Başlatıcı

echo.
echo ========================================
echo   Rezervasyon Sistemi Başlatıcı
echo ========================================
echo.

REM Python kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python kurulu değil!
    echo.
    echo Python kurulumu için: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Virtual environment kontrolü
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment bulundu
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
    ) else (
        echo.
        echo ⚠️  Virtual environment olmadan devam ediliyor...
    )
)

echo.
echo 🚀 Uygulama başlatılıyor...
echo.

REM Python script'i çalıştır
python start_app.py

pause
