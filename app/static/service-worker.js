const CACHE_VERSION = 'v1.2.0';
const CACHE_NAME = `rezervasyon-cache-${CACHE_VERSION}`;

// Önbellekte saklanacak statik dosyalar
const STATIC_CACHE_URLS = [
    '/static/css/main.css',
    '/static/css/shadcn.css',
    '/static/css/modal-system.css',
    '/static/js/main.js',
    '/static/js/pwa.js',
    '/static/js/shadcn-utils.js',
    '/static/js/modal-system.js',
    '/static/js/modal-helpers.js',
    '/static/js/cache-manager.js',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    '/static/manifest.json'
];

// API route'ları için cache süresi (milisaniye)
const API_CACHE_DURATION = 5 * 60 * 1000; // 5 dakika

// Service Worker yüklendiğinde
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_CACHE_URLS);
            })
            .then(() => self.skipWaiting())
            .catch((error) => {
                console.error('[Service Worker] Cache failed:', error);
            })
    );
});

// Service Worker aktif olduğunda
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((cacheName) => cacheName !== CACHE_NAME)
                        .map((cacheName) => {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch olaylarını yakalama
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Sadece aynı origin'den gelen istekleri önbelleğe al
    if (url.origin !== location.origin) {
        // CDN kaynakları için cache-first stratejisi
        if (url.hostname.includes('cdn.jsdelivr.net') || url.hostname.includes('cdnjs.cloudflare.com')) {
            event.respondWith(cacheFirst(request));
        }
        return;
    }

    // API istekleri için network-first stratejisi
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirst(request));
        return;
    }

    // POST, PUT, DELETE istekleri için sadece network
    if (request.method !== 'GET') {
        event.respondWith(fetch(request));
        return;
    }

    // Statik dosyalar için cache-first stratejisi
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirst(request));
        return;
    }

    // HTML sayfaları için network-first stratejisi
    event.respondWith(networkFirst(request));
});

// Cache-First Strategy
async function cacheFirst(request) {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    
    if (cached) {
        console.log('[Service Worker] Cache hit:', request.url);
        return cached;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('[Service Worker] Fetch failed:', error);
        return new Response('Offline - Resource not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'text/plain'
            })
        });
    }
}

// Network-First Strategy
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('[Service Worker] Network failed, trying cache:', request.url);
        
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }
        
        // Offline sayfasını göster
        if (request.headers.get('accept').includes('text/html')) {
            const offlineResponse = await caches.match('/offline');
            if (offlineResponse) {
                return offlineResponse;
            }
        }
        
        return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Background Sync için
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Background sync:', event.tag);
    
    if (event.tag === 'sync-reservations') {
        event.waitUntil(syncReservations());
    }
});

async function syncReservations() {
    try {
        // IndexedDB'den bekleyen rezervasyonları al ve gönder
        console.log('[Service Worker] Syncing pending reservations...');
        // TODO: Implement actual sync logic
    } catch (error) {
        console.error('[Service Worker] Sync failed:', error);
    }
}

// Push notification desteği
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'Yeni bildirim',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/Icon-72.png',
        vibrate: [200, 100, 200],
        tag: 'rezervasyon-notification',
        requireInteraction: false,
        actions: [
            { action: 'open', title: 'Aç' },
            { action: 'close', title: 'Kapat' }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Rezervasyon Sistemi', options)
    );
});

// Notification tıklama olayı
self.addEventListener('notificationclick', (event) => {
    console.log('[Service Worker] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Mesaj alma (sayfa ile iletişim)
self.addEventListener('message', (event) => {
    console.log('[Service Worker] Message received:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            })
        );
    }
});

console.log('[Service Worker] Loaded successfully');
