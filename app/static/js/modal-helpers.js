/**
 * EventFlow Modal System - Helper Functions
 * Kolay kullanım için yardımcı fonksiyonlar
 */

// Modal'ın yüklenmesini bekle
(function() {
    'use strict';
    
    // Modal yüklenene kadar bekle
    const waitForModal = () => {
        return new Promise((resolve) => {
            if (window.Modal) {
                resolve();
            } else {
                const checkInterval = setInterval(() => {
                    if (window.Modal) {
                        clearInterval(checkInterval);
                        resolve();
                    }
                }, 50);
            }
        });
    };

    // Basit kullanım fonksiyonları
    window.showSuccess = (message, title = 'Başarılı') => {
        if (!window.Modal) {
            console.error('Modal system not loaded yet');
            return Promise.resolve(false);
        }
        return window.Modal.success({ message, title });
    };

    window.showError = (message, title = 'Hata') => {
        if (!window.Modal) {
            console.error('Modal system not loaded yet');
            return Promise.resolve(false);
        }
        return window.Modal.error({ message, title });
    };

    window.showWarning = (message, title = 'Uyarı') => {
        if (!window.Modal) {
            console.error('Modal system not loaded yet');
            return Promise.resolve(false);
        }
        return window.Modal.warning({ message, title });
    };

    window.showInfo = (message, title = 'Bilgi') => {
        if (!window.Modal) {
            console.error('Modal system not loaded yet');
            return Promise.resolve(false);
        }
        return window.Modal.alert({ message, title });
    };

    window.showConfirm = (message, title = 'Onay Gerekli') => {
        if (!window.Modal) {
            console.error('Modal system not loaded yet');
            return Promise.resolve(false);
        }
        return window.Modal.confirm({ message, title });
    };

    // Toast notifications
    window.toastSuccess = (message) => {
        if (!window.Modal) return;
        window.Modal.toast({ type: 'success', message });
    };

    window.toastError = (message) => {
        if (!window.Modal) return;
        window.Modal.toast({ type: 'error', message });
    };

    window.toastWarning = (message) => {
        if (!window.Modal) return;
        window.Modal.toast({ type: 'warning', message });
    };

    window.toastInfo = (message) => {
        if (!window.Modal) return;
        window.Modal.toast({ type: 'info', message });
    };

    // Özel silme onayı
    window.confirmDelete = (itemName = 'bu öğeyi') => {
        if (!window.Modal) {
            return Promise.resolve(confirm(`${itemName} silmek istediğinize emin misiniz?`));
        }
        return window.Modal.confirm({
            type: 'error',
            title: 'Silme Onayı',
            message: `${itemName} silmek istediğinize emin misiniz? Bu işlem geri alınamaz.`,
            confirmText: 'Evet, Sil',
            cancelText: 'İptal'
        });
    };

    // Form gönderme onayı
    window.confirmSubmit = (message = 'Bu işlemi gerçekleştirmek istediğinize emin misiniz?') => {
        if (!window.Modal) {
            return Promise.resolve(confirm(message));
        }
        return window.Modal.confirm({
            type: 'warning',
            title: 'İşlem Onayı',
            message,
            confirmText: 'Evet, Devam Et',
            cancelText: 'İptal'
        });
    };

    // QR kod oluşturma onayı
    window.confirmQRGeneration = (reservationLabel) => {
        if (!window.Modal) {
            return Promise.resolve(confirm(`${reservationLabel} için QR kod oluşturulsun mu?`));
        }
        return window.Modal.confirm({
            type: 'info',
            title: 'QR Kod Oluştur',
            message: `${reservationLabel} için QR kod oluşturulsun mu?`,
            confirmText: 'Oluştur',
            cancelText: 'İptal'
        });
    };

    // Tüm koltukları temizleme onayı
    window.confirmClearAll = () => {
        if (!window.Modal) {
            return Promise.resolve(confirm('Tüm koltukları silmek istediğinizden emin misiniz?'));
        }
        return window.Modal.confirm({
            type: 'error',
            title: 'Tümünü Temizle',
            message: 'Tüm koltukları silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.',
            confirmText: 'Evet, Tümünü Sil',
            cancelText: 'İptal'
        });
    };

    // Etkinlik iptal onayı
    window.confirmEventCancel = () => {
        if (!window.Modal) {
            return Promise.resolve(confirm('Bu etkinliği iptal etmek istediğinizden emin misiniz?'));
        }
        return window.Modal.confirm({
            type: 'warning',
            title: 'Etkinliği İptal Et',
            message: 'Bu etkinliği iptal etmek istediğinizden emin misiniz?',
            confirmText: 'Evet, İptal Et',
            cancelText: 'Vazgeç'
        });
    };

    // Yükleme tamamlandı mesajı
    console.log('✅ Modal helpers yüklendi');
})();
