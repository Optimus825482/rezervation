## 1. Discovery
- [x] 1.1 Envanter: Tüm mevcut template ve statik assetleri kategorize et
- [x] 1.2 Kullanıcı akışlarını doğrula: dashboard, rezervasyon, etkinlik, check-in, auth

## 2. Tasarım Sistemi
- [ ] 2.1 Tailwind konfigürasyonunu (renk paleti, tipografi ölçekleri, spacing) oluştur
- [ ] 2.2 shadcn/ui bileşen envanterini belirle ve ihtiyaçlara göre özelleştir
- [ ] 2.3 Tasarım tokenlarını Jinja makroları veya partial template yapılarıyla eşleştir

## 3. Altyapı
- [ ] 3.1 Tailwind CDN konfigürasyonunu `base.html` içinde merkezi hale getir
- [ ] 3.2 shadcn-style bileşenler için gerekli yardımcı JS/CSS parçalarını vanilla JS ile hazırla
- [ ] 3.3 CDN kullanımında performans (preconnect, defer) ve güvenlik (CSP nonce) ayarlarını güncelle

## 4. Uygulama
- [ ] 4.1 `base.html` ve global layout parçalarını mobile-first olarak yeniden yaz
- [ ] 4.2 Dashboard, rezervasyon, etkinlik, check-in, auth sayfalarını yeni bileşenlerle güncelle
- [ ] 4.3 Offline/Skeleton durumları ve PWA uyumlu feedback paternlerini ekle
- [ ] 4.4 Flask view/controller tarafında yeni template parçalarına uyacak veri sözleşmelerini güncelle

## 5. Test ve Doğrulama
- [ ] 5.1 Responsive ve erişilebilirlik (a11y) testlerini tamamla
- [ ] 5.2 PWA denetimleri (Lighthouse) ile performans/uyum metriklerini doğrula
- [ ] 5.3 Pytest + snapshot veya HTML diff tabanlı regresyon testlerini güncelle

## 6. Dokümantasyon ve Geçiş
- [ ] 6.1 Yeni tasarım sistemi dokümantasyonunu oluştur
- [ ] 6.2 Geliştirici kullanım kılavuzunu (Tailwind + shadcn akışı) güncelle
- [ ] 6.3 Üretime geçiş için manuel test ve rollout planını hazırla
