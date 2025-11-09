# Rezervasyon Sistemi - Docker Makefile
# Kullanım: make [command]

.PHONY: help build up down restart logs shell db-shell db-backup db-restore test clean prod-up prod-down

# Varsayılan komut
.DEFAULT_GOAL := help

# Yardım
help:
	@echo "🚀 Rezervasyon Sistemi - Docker Komutları"
	@echo ""
	@echo "Geliştirme (Development):"
	@echo "  make build          - Docker image'lerini oluştur"
	@echo "  make up             - Container'ları başlat"
	@echo "  make down           - Container'ları durdur"
	@echo "  make restart        - Container'ları yeniden başlat"
	@echo "  make logs           - Logları göster"
	@echo "  make logs-app       - Sadece app logları"
	@echo "  make shell          - App container'a shell aç"
	@echo "  make db-shell       - PostgreSQL shell aç"
	@echo ""
	@echo "Veritabanı:"
	@echo "  make db-migrate     - Migration oluştur"
	@echo "  make db-upgrade     - Migration'ları uygula"
	@echo "  make db-downgrade   - Migration'ları geri al"
	@echo "  make db-backup      - Veritabanı yedeği al"
	@echo "  make db-restore     - Veritabanı geri yükle"
	@echo "  make seed           - Örnek veriler yükle"
	@echo ""
	@echo "Test & QA:"
	@echo "  make test           - Testleri çalıştır"
	@echo "  make test-coverage  - Test coverage raporu"
	@echo "  make qr-generate    - QR kodları oluştur"
	@echo ""
	@echo "Temizlik:"
	@echo "  make clean          - Container'ları ve volume'leri sil"
	@echo "  make clean-all      - Her şeyi temizle (dikkat!)"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build     - Production image'leri oluştur"
	@echo "  make prod-up        - Production container'ları başlat"
	@echo "  make prod-down      - Production container'ları durdur"
	@echo "  make ssl-generate   - Self-signed SSL sertifikası oluştur"
	@echo ""

# Development Commands
build:
	@echo "📦 Docker image'leri oluşturuluyor..."
	docker-compose build

up:
	@echo "🚀 Container'lar başlatılıyor..."
	docker-compose up -d
	@echo "✅ Container'lar başlatıldı!"
	@echo "🌐 Uygulama: http://localhost:5000"

down:
	@echo "⏹️  Container'lar durduruluyor..."
	docker-compose down
	@echo "✅ Container'lar durduruldu!"

restart:
	@echo "🔄 Container'lar yeniden başlatılıyor..."
	docker-compose restart
	@echo "✅ Yeniden başlatıldı!"

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

shell:
	@echo "🐚 App container shell açılıyor..."
	docker-compose exec app bash

db-shell:
	@echo "🐘 PostgreSQL shell açılıyor..."
	docker-compose exec db psql -U postgres -d rezervasyon_db

# Database Commands
db-migrate:
	@echo "📝 Migration oluşturuluyor..."
	@read -p "Migration açıklaması: " desc; \
	docker-compose exec app flask db migrate -m "$$desc"

db-upgrade:
	@echo "⬆️  Migration'lar uygulanıyor..."
	docker-compose exec app flask db upgrade
	@echo "✅ Migration'lar uygulandı!"

db-downgrade:
	@echo "⬇️  Migration geri alınıyor..."
	docker-compose exec app flask db downgrade
	@echo "✅ Migration geri alındı!"

db-backup:
	@echo "💾 Veritabanı yedeği alınıyor..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U postgres rezervasyon_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Yedek alındı: backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

db-restore:
	@echo "📥 Veritabanı geri yükleniyor..."
	@read -p "Yedek dosyası (backups/*.sql): " file; \
	docker-compose exec -T db psql -U postgres rezervasyon_db < $$file
	@echo "✅ Veritabanı geri yüklendi!"

seed:
	@echo "🌱 Örnek veriler yükleniyor..."
	docker-compose exec app python seed_data.py
	@echo "✅ Örnek veriler yüklendi!"

# Test Commands
test:
	@echo "🧪 Testler çalıştırılıyor..."
	docker-compose exec app pytest -v

test-coverage:
	@echo "📊 Test coverage raporu oluşturuluyor..."
	docker-compose exec app pytest --cov=app --cov-report=html
	@echo "✅ Rapor oluşturuldu: htmlcov/index.html"

qr-generate:
	@echo "🔲 QR kodları oluşturuluyor..."
	docker-compose exec app python generate_qr_codes.py
	@echo "✅ QR kodları oluşturuldu!"

# Cleanup Commands
clean:
	@echo "🧹 Container'lar ve volume'ler temizleniyor..."
	docker-compose down -v
	@echo "✅ Temizlendi!"

clean-all:
	@echo "⚠️  UYARI: Tüm veriler silinecek!"
	@read -p "Devam etmek istediğinize emin misiniz? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		docker-compose down -v; \
		docker system prune -af --volumes; \
		echo "✅ Her şey temizlendi!"; \
	else \
		echo "❌ İptal edildi."; \
	fi

# Production Commands
prod-build:
	@echo "🏭 Production image'leri oluşturuluyor..."
	docker-compose -f docker-compose.prod.yml build
	@echo "✅ Production image'leri hazır!"

prod-up:
	@echo "🚀 Production container'ları başlatılıyor..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production container'ları başlatıldı!"
	@echo "🌐 Nginx: http://localhost"

prod-down:
	@echo "⏹️  Production container'ları durduruluyor..."
	docker-compose -f docker-compose.prod.yml down
	@echo "✅ Production container'ları durduruldu!"

ssl-generate:
	@echo "🔐 Self-signed SSL sertifikası oluşturuluyor..."
	@mkdir -p nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout nginx/ssl/key.pem \
		-out nginx/ssl/cert.pem \
		-subj "/C=TR/ST=Istanbul/L=Istanbul/O=Rezervasyon/CN=localhost"
	@echo "✅ SSL sertifikası oluşturuldu: nginx/ssl/"

# Status Check
status:
	@echo "📊 Container durumu:"
	docker-compose ps
	@echo ""
	@echo "💾 Volume kullanımı:"
	docker volume ls --filter name=rezervation

# Quick start (ilk kurulum)
init: build up db-upgrade seed
	@echo "✅ Sistem başarıyla kuruldu!"
	@echo "🌐 Uygulama: http://localhost:5000"
	@echo ""
	@echo "Varsayılan giriş bilgileri:"
	@echo "  Kullanıcı: admin"
	@echo "  Şifre: Admin123!"
