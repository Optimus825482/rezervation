const CACHE_NAME = 'rezervasyon-v1';
const STATIC_CACHE = 'rezervasyon-static-v1';
const DYNAMIC_CACHE = 'rezervasyon-dynamic-v1';

// Offline'da cache'lenecek statik dosyalar
const STATIC_ASSETS = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS.map(url => new Request(url, {credentials: 'same-origin'})));
      })
      .catch((err) => {
        console.error('[Service Worker] Cache failed:', err);
      })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== STATIC_CACHE && key !== DYNAMIC_CACHE)
          .map((key) => {
            console.log('[Service Worker] Removing old cache:', key);
            return caches.delete(key);
          })
      );
    })
  );
  return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    // Cache CDN resources
    if (url.hostname.includes('cdn.jsdelivr.net') || url.hostname.includes('cdnjs.cloudflare.com')) {
      event.respondWith(
        caches.match(request).then((response) => {
          return response || fetch(request).then((fetchResponse) => {
            return caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, fetchResponse.clone());
              return fetchResponse;
            });
          });
        })
      );
    }
    return;
  }

  // API requests - network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, clone);
          });
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }

  // HTML pages - network first, cache fallback, offline page
  if (request.headers.get('Accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, clone);
          });
          return response;
        })
        .catch(() => {
          return caches.match(request).then((response) => {
            return response || caches.match('/offline.html');
          });
        })
    );
    return;
  }

  // Static assets - cache first, network fallback
  event.respondWith(
    caches.match(request).then((response) => {
      return response || fetch(request).then((fetchResponse) => {
        return caches.open(DYNAMIC_CACHE).then((cache) => {
          cache.put(request, fetchResponse.clone());
          return fetchResponse;
        });
      });
    })
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-reservations') {
    event.waitUntil(syncReservations());
  }
});

async function syncReservations() {
  // Get pending reservations from IndexedDB
  const db = await openDB();
  const pending = await db.getAll('pending-reservations');
  
  for (const reservation of pending) {
    try {
      const response = await fetch('/reservation/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reservation.data)
      });
      
      if (response.ok) {
        await db.delete('pending-reservations', reservation.id);
      }
    } catch (err) {
      console.error('Sync failed for reservation:', err);
    }
  }
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('rezervasyon-db', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-reservations')) {
        db.createObjectStore('pending-reservations', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Push notifications
self.addEventListener('push', (event) => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || 'Yeni bildiriminiz var',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: data,
    actions: [
      { action: 'view', title: 'Görüntüle', icon: '/static/icons/view.png' },
      { action: 'close', title: 'Kapat', icon: '/static/icons/close.png' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Rezervasyon Sistemi', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});
