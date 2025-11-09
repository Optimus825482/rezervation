// PWA Utilities
class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isStandalone = false;
        this.init();
    }

    init() {
        // Standalone modda mı kontrol et
        this.isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                           window.navigator.standalone ||
                           document.referrer.includes('android-app://');

        // Service Worker'ı kaydet
        this.registerServiceWorker();

        // Install prompt'u yakala
        this.setupInstallPrompt();

        // Online/Offline durumunu izle
        this.setupOnlineOfflineHandlers();

        // Performance monitoring
        this.monitorPerformance();

        // Pull to refresh (mobil)
        this.setupPullToRefresh();
    }

    // Service Worker kaydı
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/service-worker.js', {
                    scope: '/'
                });
                
                console.log('[PWA] Service Worker registered:', registration.scope);

                // Güncelleme kontrolü
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });

                // Her 1 saatte bir güncelleme kontrolü
                setInterval(() => {
                    registration.update();
                }, 60 * 60 * 1000);

            } catch (error) {
                console.error('[PWA] Service Worker registration failed:', error);
            }
        }
    }

    // Install prompt'u ayarla
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed');
            this.deferredPrompt = null;
            this.hideInstallButton();
            this.trackInstall();
        });

        // Accept butonu için event listener
        const acceptBtn = document.getElementById('install-pwa-accept');
        if (acceptBtn) {
            acceptBtn.addEventListener('click', () => this.promptInstall());
        }

        // Dismiss butonu için event listener
        const dismissBtn = document.getElementById('install-pwa-dismiss');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                this.hideInstallButton();
                // localStorage'a kaydediyoruz ki bir daha göstermeyelim
                localStorage.setItem('pwa-install-dismissed', 'true');
            });
        }
    }

    // Install butonunu göster
    showInstallButton() {
        // Daha önce dismiss edildiyse gösterme
        if (localStorage.getItem('pwa-install-dismissed') === 'true') {
            return;
        }

        const installBtn = document.getElementById('install-pwa-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }

    hideInstallButton() {
        const installBtn = document.getElementById('install-pwa-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    // Kurulum prompt'unu göster
    async promptInstall() {
        if (!this.deferredPrompt) {
            return;
        }

        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;
        
        console.log(`[PWA] User response: ${outcome}`);
        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    // Güncelleme bildirimi
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'pwa-update-notification';
        notification.innerHTML = `
            <div class="alert alert-info alert-dismissible fade show" role="alert">
                <i class="fas fa-sync-alt me-2"></i>
                Yeni bir sürüm mevcut!
                <button type="button" class="btn btn-sm btn-primary ms-3" onclick="pwaManager.reloadApp()">
                    Güncelle
                </button>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        document.body.appendChild(notification);
    }

    // Uygulamayı yeniden yükle
    reloadApp() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
        }
        window.location.reload();
    }

    // Online/Offline durumu
    setupOnlineOfflineHandlers() {
        window.addEventListener('online', () => {
            console.log('[PWA] Online');
            this.showNetworkStatus('online');
            this.syncPendingData();
        });

        window.addEventListener('offline', () => {
            console.log('[PWA] Offline');
            this.showNetworkStatus('offline');
        });
    }

    showNetworkStatus(status) {
        const statusEl = document.getElementById('network-status');
        if (statusEl) {
            statusEl.className = `network-status ${status}`;
            statusEl.textContent = status === 'online' ? 'Çevrimiçi' : 'Çevrimdışı';
            
            setTimeout(() => {
                statusEl.className = 'network-status hidden';
            }, 3000);
        }
    }

    // Bekleyen verileri senkronize et
    async syncPendingData() {
        if ('sync' in navigator.serviceWorker.registration) {
            try {
                await navigator.serviceWorker.ready;
                await navigator.serviceWorker.registration.sync.register('sync-reservations');
                console.log('[PWA] Background sync registered');
            } catch (error) {
                console.error('[PWA] Background sync failed:', error);
            }
        }
    }

    // Performance monitoring
    monitorPerformance() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                console.log(`[PWA] Page load time: ${pageLoadTime}ms`);

                // Core Web Vitals
                if ('PerformanceObserver' in window) {
                    // Largest Contentful Paint (LCP)
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        console.log('[PWA] LCP:', lastEntry.renderTime || lastEntry.loadTime);
                    }).observe({ entryTypes: ['largest-contentful-paint'] });

                    // First Input Delay (FID)
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        entries.forEach((entry) => {
                            console.log('[PWA] FID:', entry.processingStart - entry.startTime);
                        });
                    }).observe({ entryTypes: ['first-input'] });

                    // Cumulative Layout Shift (CLS)
                    let clsScore = 0;
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        entries.forEach((entry) => {
                            if (!entry.hadRecentInput) {
                                clsScore += entry.value;
                            }
                        });
                        console.log('[PWA] CLS:', clsScore);
                    }).observe({ entryTypes: ['layout-shift'] });
                }
            });
        }
    }

    // Pull to refresh (mobil için)
    setupPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let pulling = false;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].pageY;
                pulling = true;
            }
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!pulling) return;
            
            currentY = e.touches[0].pageY;
            const pullDistance = currentY - startY;

            if (pullDistance > 100) {
                this.showPullToRefreshIndicator();
            }
        }, { passive: true });

        document.addEventListener('touchend', () => {
            if (pulling && (currentY - startY) > 100) {
                this.refreshPage();
            }
            pulling = false;
            this.hidePullToRefreshIndicator();
        }, { passive: true });
    }

    showPullToRefreshIndicator() {
        let indicator = document.getElementById('pull-to-refresh-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pull-to-refresh-indicator';
            indicator.className = 'pull-to-refresh-indicator';
            indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';
            document.body.insertBefore(indicator, document.body.firstChild);
        }
        indicator.style.display = 'flex';
    }

    hidePullToRefreshIndicator() {
        const indicator = document.getElementById('pull-to-refresh-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    refreshPage() {
        window.location.reload();
    }

    // Install tracking (analytics için)
    trackInstall() {
        // Analytics event gönder
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pwa_install', {
                event_category: 'PWA',
                event_label: 'App Installed'
            });
        }
    }

    // Push notification izni iste
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            console.log('[PWA] Notification permission:', permission);
            return permission === 'granted';
        }
        return false;
    }

    // Badge sayısını güncelle (Chrome, Edge)
    updateBadge(count) {
        if ('setAppBadge' in navigator) {
            navigator.setAppBadge(count);
        }
    }

    clearBadge() {
        if ('clearAppBadge' in navigator) {
            navigator.clearAppBadge();
        }
    }
}

// Global PWA Manager instance
const pwaManager = new PWAManager();

// Share API desteği
async function shareContent(title, text, url) {
    if (navigator.share) {
        try {
            await navigator.share({ title, text, url });
            console.log('[PWA] Content shared successfully');
        } catch (error) {
            console.error('[PWA] Share failed:', error);
        }
    } else {
        // Fallback: Clipboard API
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(url);
            alert('Link kopyalandı!');
        }
    }
}

// Lazy loading için Intersection Observer
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// DOM hazır olduğunda
document.addEventListener('DOMContentLoaded', () => {
    setupLazyLoading();
    
    // Loading screen'i kaldır
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }, 500);
    }
});

// Export for use in other scripts
window.pwaManager = pwaManager;
window.shareContent = shareContent;
