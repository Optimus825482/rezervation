// PWA Installation and Features
class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.installDismissKey = 'pwa-install-dismissed';
    this.dismissCooldown = 1000 * 60 * 60 * 24 * 7; // 7 days
    this.isPrompting = false;
    this.init();
  }

  init() {
    // Register service worker
    if ('serviceWorker' in navigator) {
      this.registerServiceWorker();
    }

    // Handle install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      this.showInstallButton();
    });

    // Handle app installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA installed successfully');
      this.hideInstallButton();
      this.rememberDismiss();
      this.showToast('Uygulama başarıyla yüklendi!', 'success');
    });

    // Check if running as PWA
    if (window.matchMedia('(display-mode: standalone)').matches) {
      console.log('Running as PWA');
      document.body.classList.add('pwa-mode');
    }

    // Handle online/offline status
    this.handleConnectivity();

    // Initialize pull to refresh
    this.initPullToRefresh();
  }

  async registerServiceWorker() {
    try {
      const registration = await navigator.serviceWorker.register('/static/service-worker.js', {
        scope: '/'
      });
      console.log('Service Worker registered:', registration.scope);

      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, 60000); // Check every minute
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  }

  getDismissTimestamp() {
    try {
      const value = localStorage.getItem(this.installDismissKey);
      if (!value) {
        return null;
      }
      const parsed = parseInt(value, 10);
      return Number.isNaN(parsed) ? null : parsed;
    } catch (error) {
      console.warn('PWA dismissal bilgisi okunamadı:', error);
      return null;
    }
  }

  shouldShowInstallPrompt() {
    const lastDismiss = this.getDismissTimestamp();
    if (!lastDismiss) {
      return true;
    }
    return (Date.now() - lastDismiss) > this.dismissCooldown;
  }

  rememberDismiss() {
    try {
      localStorage.setItem(this.installDismissKey, Date.now().toString());
    } catch (error) {
      console.warn('PWA dismissal bilgisi kaydedilemedi:', error);
    }
  }

  showInstallButton() {
    const container = document.getElementById('install-pwa-btn');
    const accept = document.getElementById('install-pwa-accept');
    const dismiss = document.getElementById('install-pwa-dismiss');

    if (!container || !this.shouldShowInstallPrompt()) {
      return;
    }

    container.classList.remove('hidden');

    if (accept) {
      accept.addEventListener('click', (event) => {
        event.preventDefault();
        this.installApp();
      }, { once: true });
    }

    if (dismiss) {
      dismiss.addEventListener('click', (event) => {
        event.preventDefault();
        this.hideInstallButton();
        this.deferredPrompt = null;
        this.rememberDismiss();
      }, { once: true });
    }
  }

  hideInstallButton() {
    const container = document.getElementById('install-pwa-btn');
    if (container) {
      container.classList.add('hidden');
    }
  }

  async installApp() {
    if (!this.deferredPrompt || this.isPrompting) {
      return;
    }
    const promptEvent = this.deferredPrompt;
    this.isPrompting = true;

    try {
      await promptEvent.prompt();
      const { outcome } = await promptEvent.userChoice;
      console.log(`User response: ${outcome}`);
    } catch (error) {
      console.warn('PWA kurulum bildirimi açılamadı:', error);
      this.showToast('Yükleme isteği reddedildi.', 'warning');
    } finally {
      this.deferredPrompt = null;
      this.isPrompting = false;
      this.hideInstallButton();
      this.rememberDismiss();
    }
  }

  handleConnectivity() {
    const updateOnlineStatus = () => {
      if (navigator.onLine) {
        document.body.classList.remove('offline');
        this.showToast('Bağlantı yeniden kuruldu', 'success');
        this.syncPendingData();
      } else {
        document.body.classList.add('offline');
        this.showToast('İnternet bağlantısı yok. Çevrimdışı moddasınız.', 'warning');
      }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Initial check
    if (!navigator.onLine) {
      document.body.classList.add('offline');
    }
  }

  async syncPendingData() {
    if ('sync' in navigator.serviceWorker.ready) {
      try {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('sync-reservations');
        console.log('Background sync registered');
      } catch (error) {
        console.error('Background sync failed:', error);
      }
    }
  }

  initPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let pulling = false;

    const ptr = document.createElement('div');
    ptr.className = 'ptr-element';
    ptr.innerHTML = '<i class="fas fa-sync fa-spin"></i> Yenileniyor...';
    document.body.insertBefore(ptr, document.body.firstChild);

    document.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].pageY;
        pulling = true;
      }
    });

    document.addEventListener('touchmove', (e) => {
      if (!pulling) return;

      currentY = e.touches[0].pageY;
      const distance = currentY - startY;

      if (distance > 0 && distance < 100) {
        ptr.style.transform = `translateY(${distance - 100}%)`;
      }
    });

    document.addEventListener('touchend', () => {
      if (pulling && currentY - startY > 80) {
        ptr.classList.add('visible');
        setTimeout(() => {
          window.location.reload();
        }, 300);
      } else {
        ptr.style.transform = 'translateY(-100%)';
      }
      pulling = false;
    });
  }

  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-mobile toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
}

// Initialize PWA
const pwaManager = new PWAManager();

// Request notification permission
async function requestNotificationPermission() {
  if ('Notification' in window && Notification.permission === 'default') {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('Notification permission granted');
      subscribeToP

ush();
    }
  }
}

// Subscribe to push notifications
async function subscribeToPush() {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        'YOUR_PUBLIC_VAPID_KEY_HERE' // Replace with actual VAPID key
      )
    });

    // Send subscription to server
    await fetch('/api/push-subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription)
    });

    console.log('Push subscription successful');
  } catch (error) {
    console.error('Push subscription failed:', error);
  }
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Lazy load images
function lazyLoadImages() {
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        observer.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));
}

// Performance monitoring
function measurePerformance() {
  if ('performance' in window) {
    window.addEventListener('load', () => {
      const perfData = performance.getEntriesByType('navigation')[0];
      console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
      
      // Send to analytics (optional)
      // sendAnalytics({ loadTime: perfData.loadEventEnd - perfData.loadEventStart });
    });
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  lazyLoadImages();
  measurePerformance();
  
  // Initialize bottom navigation
  const currentPath = window.location.pathname;
  document.querySelectorAll('.bottom-nav-item').forEach(item => {
    if (item.getAttribute('href') === currentPath) {
      item.classList.add('active');
    }
  });
});

// Export for use in other scripts
window.PWA = {
  showToast: (msg, type) => pwaManager.showToast(msg, type),
  requestNotifications: requestNotificationPermission
};
