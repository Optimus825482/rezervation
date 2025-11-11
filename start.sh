#!/bin/bash

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Rezervasyon Sistemi Başlatıcı"
echo "========================================"
echo ""

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 kurulu değil!${NC}"
    echo ""
    echo "Python kurulumu için:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    exit 1
fi

echo -e "${GREEN}✅ Python3 bulundu${NC}"

# Virtual environment kontrolü
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment bulundu${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment bulunamadı${NC}"
    echo ""
    read -p "Virtual environment oluşturmak istiyor musunuz? (E/H) [E]: " create_venv
    create_venv=${create_venv:-E}
    
    if [[ $create_venv =~ ^[Ee]$ ]]; then
        echo ""
        echo -e "${CYAN}📦 Virtual environment oluşturuluyor...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        
        echo ""
        echo -e "${CYAN}📦 Bağımlılıklar yükleniyor...${NC}"
        pip install -r requirements.txt
        
        echo ""
        echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Virtual environment olmadan devam ediliyor...${NC}"
    fi
fi

echo ""
echo -e "${CYAN}🚀 Uygulama başlatılıyor...${NC}"
echo ""

# Python script'i çalıştır
python3 start_app.py
