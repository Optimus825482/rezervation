#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Uygulama Başlatıcı
Redis'i otomatik başlatır ve Flask uygulamasını çalıştırır
"""
import os
import sys
import time
import subprocess
import platform
from pathlib import Path

# Renkli output için
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKGREEN):
    """Renkli mesaj yazdır"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """Başlık yazdır"""
    print("\n" + "="*60)
    print_colored(message, Colors.HEADER + Colors.BOLD)
    print("="*60 + "\n")

def check_docker():
    """Docker kurulu mu kontrol et"""
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_colored("✅ Docker kurulu", Colors.OKGREEN)
            return True
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_redis_running():
    """Redis çalışıyor mu kontrol et"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=redis-rezervasyon', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'redis-rezervasyon' in result.stdout:
            print_colored("✅ Redis zaten çalışıyor", Colors.OKGREEN)
            return True
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def start_redis():
    """Redis container'ını başlat"""
    print_colored("🚀 Redis başlatılıyor...", Colors.OKCYAN)
    
    try:
        # Önce eski container'ı kontrol et
        result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', 'name=redis-rezervasyon', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'redis-rezervasyon' in result.stdout:
            # Container var, başlat
            print_colored("📦 Mevcut Redis container başlatılıyor...", Colors.OKCYAN)
            subprocess.run(
                ['docker', 'start', 'redis-rezervasyon'],
                check=True,
                timeout=10
            )
        else:
            # Yeni container oluştur
            print_colored("📦 Yeni Redis container oluşturuluyor...", Colors.OKCYAN)
            subprocess.run(
                [
                    'docker', 'run', '-d',
                    '--name', 'redis-rezervasyon',
                    '-p', '6379:6379',
                    'redis:alpine'
                ],
                check=True,
                timeout=30
            )
        
        # Redis'in hazır olmasını bekle
        print_colored("⏳ Redis hazırlanıyor...", Colors.OKCYAN)
        time.sleep(2)
        
        # Redis bağlantısını test et
        result = subprocess.run(
            ['docker', 'exec', 'redis-rezervasyon', 'redis-cli', 'ping'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if 'PONG' in result.stdout:
            print_colored("✅ Redis başarıyla başlatıldı!", Colors.OKGREEN)
            return True
        else:
            print_colored("⚠️ Redis yanıt vermiyor", Colors.WARNING)
            return False
            
    except subprocess.CalledProcessError as e:
        print_colored(f"❌ Redis başlatılamadı: {e}", Colors.FAIL)
        return False
    except subprocess.TimeoutExpired:
        print_colored("❌ Redis başlatma zaman aşımı", Colors.FAIL)
        return False

def update_env_file(redis_enabled):
    """Environment dosyasını güncelle"""
    env_file = Path('.env')
    
    if not env_file.exists():
        # .env yoksa .env.example'dan kopyala
        example_file = Path('.env.example')
        if example_file.exists():
            print_colored("📝 .env dosyası oluşturuluyor...", Colors.OKCYAN)
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
    
    # .env dosyasını oku
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Redis ayarlarını güncelle
    updated_lines = []
    redis_enabled_found = False
    redis_url_found = False
    session_type_found = False
    
    for line in lines:
        if line.startswith('REDIS_ENABLED='):
            updated_lines.append(f'REDIS_ENABLED={str(redis_enabled).lower()}\n')
            redis_enabled_found = True
        elif line.startswith('# REDIS_URL=') and redis_enabled:
            updated_lines.append('REDIS_URL=redis://localhost:6379/0\n')
            redis_url_found = True
        elif line.startswith('REDIS_URL='):
            if redis_enabled:
                updated_lines.append('REDIS_URL=redis://localhost:6379/0\n')
            else:
                updated_lines.append('# REDIS_URL=redis://localhost:6379/0\n')
            redis_url_found = True
        elif line.startswith('SESSION_TYPE='):
            if redis_enabled:
                updated_lines.append('SESSION_TYPE=redis\n')
            else:
                updated_lines.append('SESSION_TYPE=filesystem\n')
            session_type_found = True
        else:
            updated_lines.append(line)
    
    # Eksik satırları ekle
    if not redis_enabled_found:
        updated_lines.append(f'\nREDIS_ENABLED={str(redis_enabled).lower()}\n')
    if not redis_url_found and redis_enabled:
        updated_lines.append('REDIS_URL=redis://localhost:6379/0\n')
    if not session_type_found:
        updated_lines.append(f'SESSION_TYPE={"redis" if redis_enabled else "filesystem"}\n')
    
    # Dosyayı yaz
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print_colored("✅ .env dosyası güncellendi", Colors.OKGREEN)

def start_flask():
    """Flask uygulamasını başlat"""
    print_colored("🚀 Flask uygulaması başlatılıyor...", Colors.OKCYAN)
    print_colored("📍 http://localhost:5000", Colors.OKBLUE)
    print_colored("\n⚠️  Durdurmak için Ctrl+C kullanın\n", Colors.WARNING)
    
    try:
        # Flask'ı başlat
        if platform.system() == 'Windows':
            subprocess.run(['python', 'run.py'], check=True)
        else:
            subprocess.run(['python3', 'run.py'], check=True)
    except KeyboardInterrupt:
        print_colored("\n\n👋 Uygulama durduruluyor...", Colors.WARNING)
    except subprocess.CalledProcessError as e:
        print_colored(f"\n❌ Flask başlatılamadı: {e}", Colors.FAIL)
        sys.exit(1)

def main():
    """Ana fonksiyon"""
    print_header("🎯 Rezervasyon Sistemi Başlatıcı")
    
    # .env dosyasından Redis ayarını oku
    env_file = Path('.env')
    use_redis = False
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('REDIS_ENABLED='):
                    use_redis = line.split('=')[1].strip().lower() == 'true'
                    break
    
    if use_redis:
        print_colored("🔴 Redis modu aktif (.env'den okundu)", Colors.OKGREEN)
    else:
        print_colored("📁 Filesystem modu aktif (.env'den okundu)", Colors.OKGREEN)
    
    if use_redis:
        print_header("🔧 Redis Kurulumu")
        
        # Docker kontrolü
        if not check_docker():
            print_colored("❌ Docker kurulu değil!", Colors.FAIL)
            print_colored("📁 Filesystem session kullanılacak", Colors.WARNING)
            use_redis = False
        else:
            # Redis'i kontrol et ve başlat
            if not check_redis_running():
                if not start_redis():
                    print_colored("⚠️ Redis başlatılamadı", Colors.WARNING)
                    print_colored("📁 Filesystem session kullanılacak", Colors.WARNING)
                    use_redis = False
    else:
        print_header("📁 Filesystem Modu")
        print_colored("Redis kullanılmayacak - Basit mod aktif", Colors.OKGREEN)
    
    # Environment dosyasını güncelle
    print_header("⚙️ Yapılandırma")
    update_env_file(use_redis)
    
    # Flask'ı başlat
    print_header("🚀 Uygulama Başlatılıyor")
    start_flask()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Güle güle!", Colors.WARNING)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Beklenmeyen hata: {e}", Colors.FAIL)
        sys.exit(1)
