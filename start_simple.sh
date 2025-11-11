#!/bin/bash

# Renkler
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Rezervasyon Sistemi"
echo "  Docker OLMADAN Çalışıyor"
echo "========================================"
echo ""

# .env dosyasını kontrol et
if [ ! -f ".env" ]; then
    echo -e "${CYAN}📝 .env dosyası oluşturuluyor...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
REDIS_ENABLED=false
SESSION_TYPE=filesystem
DATABASE_URL=postgresql://postgres:password@localhost/rezervasyon_db
EOF
    fi
    echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    echo ""
fi

# Redis'i devre dışı bırak
echo -e "${CYAN}📁 Filesystem session kullanılacak (Redis YOK)${NC}"
echo ""

# .env dosyasında Redis'i kapat
if grep -q "^REDIS_ENABLED=" .env; then
    sed -i 's/^REDIS_ENABLED=.*/REDIS_ENABLED=false/' .env
else
    echo "REDIS_ENABLED=false" >> .env
fi

# Virtual environment kontrolü
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment aktifleştiriliyor...${NC}"
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
    fi
fi

echo ""
echo -e "${CYAN}🚀 Flask uygulaması başlatılıyor...${NC}"
echo -e "${CYAN}📍 http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}⚠️  Durdurmak için Ctrl+C kullanın${NC}"
echo ""

# Flask'ı başlat
python3 run.py
