## Context
The current frontend relies on server-rendered Jinja templates styled with Bootstrap and scattered custom CSS. The goal is to migrate to a Tailwind-driven design system inspired by shadcn/ui while keeping the Flask render pipeline and enhancing PWA characteristics.

## Goals / Non-Goals
- Goals: Establish Tailwind config and tokens, wrap shadcn/ui component patterns for Jinja, modernize key flows with mobile-first layouts, integrate PWA-friendly UX patterns, and ensure build tooling supports the new stack.
- Non-Goals: Rewrite backend routing logic, convert the project to a SPA, or migrate entirely to React components.

## Decisions
- Yalnızca Tailwind CDN kullanarak `tailwind.config` inline tanımlanacak ve bütün tokenlar bu konfigürasyon üzerinden yönetilecek.
- shadcn/ui bileşen desenleri React yerine Jinja makroları/partial'ları ile temsil edilecek, utility sınıfları doğrudan markup içine yerleştirilecek.
- Ortak bileşenler `app/templates/partials/ui/` altında gruplanarak tekrar kullanılabilir hale getirilecek.
- Bootstrap bağımlılıkları ve jQuery tabanlı davranışlar parça parça vanilla JS/Tailwind uyumlu etkileşimlerle değiştirilecek.

## Risks / Trade-offs
- CDN tabanlı Tailwind yapılandırması geliştirme sırasında kolay olsa da üretim için iyi önbellekleme stratejileri gerektirir.
- shadcn desenlerini Jinja ile yeniden uygulamak için detaylı dokümantasyon şart, aksi halde stil tutarlılığı bozulabilir.
- Büyük HTML diff'leri merge çatışması çıkartabilir; aşamalı rollout planlanmalı.

## Migration Plan
1. Tailwind CDN konfigürasyonunu `base.html` içinde tanımla ve mevcut sayfalara kademeli uygula.
2. Global layout (navigation, footer, flash mesajları) Tailwind utility sınıflarıyla yeniden yaz.
3. Sayfa bazında Bootstrap sınıflarını temizleyerek shadcn uyumlu Jinja partial'larıyla değiştir.
4. PWA davranışlarını (offline banner, skeleton, install prompt) yeni tasarım sistemiyle hizala.

## Open Questions
- Mevcut jQuery davranışları tamamen vanilla JS ile mi korunacak yoksa hafif bir yardımcı kütüphane (örneğin Alpine.js) eklemeye gerek var mı?
- Geçiş döneminde eski Bootstrap temalı görünümleri korumak gerekiyor mu?
