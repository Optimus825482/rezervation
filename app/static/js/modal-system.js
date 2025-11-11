/**
 * EventFlow Modal System
 * Temaya uygun modern modal/alert sistemi
 * SweetAlert alternatifi - Özel tasarım
 */

class ModalSystem {
    constructor() {
        this.activeModal = null;
        this.queue = [];
        this.init();
    }

    init() {
        // Modal container'ı oluştur
        if (!document.getElementById('modal-system-container')) {
            const container = document.createElement('div');
            container.id = 'modal-system-container';
            container.className = 'fixed inset-0 z-[9999] pointer-events-none';
            document.body.appendChild(container);
        }

        // Escape tuşu ile kapatma
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close(false);
            }
        });
    }

    /**
     * Alert göster (OK butonu ile)
     */
    alert(options) {
        return this.show({
            type: 'info',
            title: 'Bilgi',
            message: '',
            confirmText: 'Tamam',
            showCancel: false,
            ...options
        });
    }

    /**
     * Success mesajı göster
     */
    success(options) {
        return this.show({
            type: 'success',
            title: 'Başarılı',
            message: '',
            confirmText: 'Tamam',
            showCancel: false,
            ...options
        });
    }

    /**
     * Error mesajı göster
     */
    error(options) {
        return this.show({
            type: 'error',
            title: 'Hata',
            message: '',
            confirmText: 'Tamam',
            showCancel: false,
            ...options
        });
    }

    /**
     * Warning mesajı göster
     */
    warning(options) {
        return this.show({
            type: 'warning',
            title: 'Uyarı',
            message: '',
            confirmText: 'Tamam',
            showCancel: false,
            ...options
        });
    }

    /**
     * Confirmation dialog göster
     */
    confirm(options) {
        return this.show({
            type: 'warning',
            title: 'Onay Gerekli',
            message: '',
            confirmText: 'Evet',
            cancelText: 'Hayır',
            showCancel: true,
            ...options
        });
    }

    /**
     * Ana modal gösterme fonksiyonu
     */
    show(options) {
        return new Promise((resolve) => {
            // Eğer aktif modal varsa, kuyruğa ekle
            if (this.activeModal) {
                this.queue.push({ options, resolve });
                return;
            }

            const modal = this.createModal(options, resolve);
            this.activeModal = modal;

            const container = document.getElementById('modal-system-container');
            container.appendChild(modal);

            // Animasyon için kısa gecikme
            requestAnimationFrame(() => {
                modal.classList.add('modal-show');
            });
        });
    }

    /**
     * Modal HTML'ini oluştur
     */
    createModal(options, resolve) {
        const {
            type = 'info',
            title = '',
            message = '',
            html = '',
            confirmText = 'Tamam',
            cancelText = 'İptal',
            showCancel = false,
            icon = null,
            customClass = ''
        } = options;

        // Tip bazlı stiller
        const typeStyles = {
            success: {
                icon: icon || 'fa-circle-check',
                iconColor: 'text-emerald-500',
                iconBg: 'bg-emerald-100 dark:bg-emerald-900/30',
                confirmBtn: 'bg-emerald-600 hover:bg-emerald-700 text-white'
            },
            error: {
                icon: icon || 'fa-circle-xmark',
                iconColor: 'text-rose-500',
                iconBg: 'bg-rose-100 dark:bg-rose-900/30',
                confirmBtn: 'bg-rose-600 hover:bg-rose-700 text-white'
            },
            warning: {
                icon: icon || 'fa-triangle-exclamation',
                iconColor: 'text-amber-500',
                iconBg: 'bg-amber-100 dark:bg-amber-900/30',
                confirmBtn: 'bg-amber-600 hover:bg-amber-700 text-white'
            },
            info: {
                icon: icon || 'fa-circle-info',
                iconColor: 'text-sky-500',
                iconBg: 'bg-sky-100 dark:bg-sky-900/30',
                confirmBtn: 'bg-sky-600 hover:bg-sky-700 text-white'
            }
        };

        const style = typeStyles[type] || typeStyles.info;

        const modalWrapper = document.createElement('div');
        modalWrapper.className = `modal-wrapper ${customClass}`;
        
        // Dark mode kontrolü
        const isDark = document.documentElement.classList.contains('dark') || 
                      window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const bgColor = isDark ? 'rgb(15, 23, 42)' : 'white';
        const textColor = isDark ? 'rgb(248, 250, 252)' : 'rgb(15, 23, 42)';
        const messageColor = isDark ? 'rgb(203, 213, 225)' : 'rgb(71, 85, 105)';
        const cancelBg = isDark ? 'rgb(30, 41, 59)' : 'rgb(241, 245, 249)';
        const cancelTextColor = isDark ? 'rgb(203, 213, 225)' : 'rgb(51, 65, 85)';
        
        modalWrapper.innerHTML = `
            <div class="modal-backdrop" data-modal-backdrop></div>
            <div class="modal-content-wrapper">
                <div class="modal-content" style="background: ${bgColor}; color: ${textColor};">
                    <!-- Icon -->
                    <div class="modal-icon ${style.iconBg}">
                        <i class="fas ${style.icon} ${style.iconColor}"></i>
                    </div>
                    
                    <!-- Title -->
                    ${title ? `<h3 class="modal-title" style="color: ${textColor};">${this.escapeHtml(title)}</h3>` : ''}
                    
                    <!-- Message -->
                    <div class="modal-message" style="color: ${messageColor};">
                        ${html || this.escapeHtml(message)}
                    </div>
                    
                    <!-- Buttons -->
                    <div class="modal-buttons">
                        ${showCancel ? `
                            <button class="modal-btn modal-btn-cancel" data-modal-cancel style="background: ${cancelBg}; color: ${cancelTextColor};">
                                ${this.escapeHtml(cancelText)}
                            </button>
                        ` : ''}
                        <button class="modal-btn modal-btn-confirm ${style.confirmBtn}" data-modal-confirm>
                            ${this.escapeHtml(confirmText)}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Event listeners
        const backdrop = modalWrapper.querySelector('[data-modal-backdrop]');
        const confirmBtn = modalWrapper.querySelector('[data-modal-confirm]');
        const cancelBtn = modalWrapper.querySelector('[data-modal-cancel]');

        backdrop?.addEventListener('click', () => this.close(false, resolve));
        confirmBtn?.addEventListener('click', () => this.close(true, resolve));
        cancelBtn?.addEventListener('click', () => this.close(false, resolve));

        return modalWrapper;
    }

    /**
     * Modal'ı kapat
     */
    close(result, resolve) {
        if (!this.activeModal) return;

        this.activeModal.classList.remove('modal-show');
        this.activeModal.classList.add('modal-hide');

        setTimeout(() => {
            this.activeModal?.remove();
            this.activeModal = null;

            // Resolve promise
            if (resolve) resolve(result);

            // Kuyruktan bir sonraki modal'ı göster
            if (this.queue.length > 0) {
                const next = this.queue.shift();
                this.show(next.options).then(next.resolve);
            }
        }, 200);
    }

    /**
     * HTML escape
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Toast notification göster (otomatik kapanan)
     */
    toast(options) {
        const {
            type = 'info',
            message = '',
            duration = 3000,
            position = 'top-right'
        } = options;

        const typeStyles = {
            success: {
                icon: 'fa-circle-check',
                classes: 'bg-emerald-600 text-white'
            },
            error: {
                icon: 'fa-circle-xmark',
                classes: 'bg-rose-600 text-white'
            },
            warning: {
                icon: 'fa-triangle-exclamation',
                classes: 'bg-amber-600 text-white'
            },
            info: {
                icon: 'fa-circle-info',
                classes: 'bg-sky-600 text-white'
            }
        };

        const style = typeStyles[type] || typeStyles.info;

        const toast = document.createElement('div');
        toast.className = `toast toast-${position} ${style.classes}`;
        toast.innerHTML = `
            <i class="fas ${style.icon}"></i>
            <span>${this.escapeHtml(message)}</span>
            <button class="toast-close" aria-label="Kapat">
                <i class="fas fa-xmark"></i>
            </button>
        `;

        const container = document.getElementById('modal-system-container');
        container.appendChild(toast);

        // Animasyon
        requestAnimationFrame(() => {
            toast.classList.add('toast-show');
        });

        // Otomatik kapat
        const closeToast = () => {
            toast.classList.remove('toast-show');
            toast.classList.add('toast-hide');
            setTimeout(() => toast.remove(), 200);
        };

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn?.addEventListener('click', closeToast);

        if (duration > 0) {
            setTimeout(closeToast, duration);
        }
    }
}

// Global instance oluştur
window.Modal = new ModalSystem();

// Eski API'leri override et (opsiyonel - dikkatli kullan)
window.originalAlert = window.alert;
window.originalConfirm = window.confirm;

// Yeni alert fonksiyonu
window.customAlert = function(message, title = 'Bilgi') {
    return window.Modal.alert({ message, title });
};

// Yeni confirm fonksiyonu
window.customConfirm = function(message, title = 'Onay Gerekli') {
    return window.Modal.confirm({ message, title });
};
