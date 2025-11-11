/**
 * EventFlow Cache Manager
 * Tarayıcı cache'ini ve Service Worker cache'ini temizler
 */

class CacheManager {
    constructor() {
        this.init();
    }

    init() {
        // Desktop buton
        const clearBtn = document.getElementById('clear-cache-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearAllCaches());
        }

        // Mobile buton
        const clearBtnMobile = document.getElementById('clear-cache-btn-mobile');
        if (clearBtnMobile) {
            clearBtnMobile.addEventListener('click', () => this.clearAllCaches());
        }
    }

    /**
     * Tüm cache'leri temizle
     */
    async clearAllCaches() {
        try {
            // Kullanıcıya bilgi ver
            if (window.Modal) {
                const confirmed = await window.Modal.confirm({
                    type: 'warning',
                    title: 'Önbelleği Temizle',
                    message: 'Tüm önbellek verileri silinecek ve sayfa yenilenecek. Devam etmek istiyor musunuz?',
                    confirmText: 'Evet, Temizle',
                    cancelText: 'İptal'
                });

                if (!confirmed) return;
            } else {
                if (!confirm('Önbelleği temizlemek istediğinize emin misiniz? Sayfa yenilenecek.')) {
                    return;
                }
            }

            let clearedItems = [];

            // 1. Service Worker Cache'lerini temizle
            if ('caches' in window) {
                const cacheNames = await caches.keys();
                for (const cacheName of cacheNames) {
                    await caches.delete(cacheName);
                    clearedItems.push(`Cache: ${cacheName}`);
                }
                console.log('✅ Service Worker cache\'leri temizlendi:', cacheNames);
            }

            // 2. Service Worker'ı unregister et
            if ('serviceWorker' in navigator) {
                const registrations = await navigator.serviceWorker.getRegistrations();
                for (const registration of registrations) {
                    await registration.unregister();
                    clearedItems.push('Service Worker');
                }
                console.log('✅ Service Worker unregister edildi');
            }

            // 3. LocalStorage temizle (opsiyonel - dikkatli kullan)
            // localStorage.clear();
            // clearedItems.push('LocalStorage');

            // 4. SessionStorage temizle (opsiyonel)
            // sessionStorage.clear();
            // clearedItems.push('SessionStorage');

            // 5. IndexedDB temizle (opsiyonel - dikkatli kullan)
            // await this.clearIndexedDB();
            // clearedItems.push('IndexedDB');

            console.log('✅ Temizlenen öğeler:', clearedItems);

            // Başarı mesajı göster ve sayfayı yenile
            if (window.Modal) {
                await window.Modal.success({
                    title: 'Başarılı',
                    message: 'Önbellek temizlendi! Sayfa yenileniyor...',
                    confirmText: 'Tamam'
                });
            } else {
                alert('Önbellek temizlendi! Sayfa yenileniyor...');
            }

            // Sayfayı hard reload ile yenile
            setTimeout(() => {
                window.location.reload(true);
            }, 500);

        } catch (error) {
            console.error('❌ Cache temizleme hatası:', error);
            
            if (window.Modal) {
                window.Modal.error({
                    title: 'Hata',
                    message: 'Önbellek temizlenirken bir hata oluştu: ' + error.message,
                    confirmText: 'Tamam'
                });
            } else {
                alert('Önbellek temizlenirken hata oluştu: ' + error.message);
            }
        }
    }

    /**
     * IndexedDB'yi temizle
     */
    async clearIndexedDB() {
        if (!window.indexedDB) return;

        return new Promise((resolve, reject) => {
            const databases = indexedDB.databases();
            databases.then(dbList => {
                dbList.forEach(db => {
                    indexedDB.deleteDatabase(db.name);
                });
                resolve();
            }).catch(reject);
        });
    }

    /**
     * Belirli bir cache'i temizle
     */
    async clearSpecificCache(cacheName) {
        if ('caches' in window) {
            const deleted = await caches.delete(cacheName);
            console.log(`Cache "${cacheName}" ${deleted ? 'silindi' : 'bulunamadı'}`);
            return deleted;
        }
        return false;
    }

    /**
     * Cache boyutunu hesapla (tahmini)
     */
    async getCacheSize() {
        if (!('caches' in window)) return 0;

        let totalSize = 0;
        const cacheNames = await caches.keys();

        for (const cacheName of cacheNames) {
            const cache = await caches.open(cacheName);
            const requests = await cache.keys();
            
            for (const request of requests) {
                const response = await cache.match(request);
                if (response) {
                    const blob = await response.blob();
                    totalSize += blob.size;
                }
            }
        }

        return totalSize;
    }

    /**
     * Cache bilgilerini göster
     */
    async showCacheInfo() {
        if (!('caches' in window)) {
            console.log('Cache API desteklenmiyor');
            return;
        }

        const cacheNames = await caches.keys();
        console.log('📦 Mevcut Cache\'ler:', cacheNames);

        for (const cacheName of cacheNames) {
            const cache = await caches.open(cacheName);
            const requests = await cache.keys();
            console.log(`  - ${cacheName}: ${requests.length} öğe`);
        }

        const size = await this.getCacheSize();
        console.log(`💾 Toplam Cache Boyutu: ${(size / 1024 / 1024).toFixed(2)} MB`);
    }
}

// Global instance oluştur
window.CacheManager = new CacheManager();

// Console'dan kullanım için yardımcı fonksiyonlar
window.clearCache = () => window.CacheManager.clearAllCaches();
window.showCacheInfo = () => window.CacheManager.showCacheInfo();

console.log('💡 Cache Manager yüklendi. Kullanım:');
console.log('  - clearCache() : Tüm cache\'leri temizle');
console.log('  - showCacheInfo() : Cache bilgilerini göster');
