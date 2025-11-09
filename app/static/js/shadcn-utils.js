// shadcn/ui Utility Functions

/**
 * Dropdown Menu Utilities
 */
class DropdownMenu {
    constructor(triggerId, menuId) {
        this.trigger = document.getElementById(triggerId);
        this.menu = document.getElementById(menuId);
        this.isOpen = false;
        
        if (this.trigger && this.menu) {
            this.init();
        }
    }
    
    init() {
        this.trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        document.addEventListener('click', () => {
            if (this.isOpen) {
                this.close();
            }
        });
        
        this.menu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    toggle() {
        this.isOpen ? this.close() : this.open();
    }
    
    open() {
        this.menu.classList.remove('hidden');
        this.menu.classList.add('animate-shadcn-slide-in');
        this.isOpen = true;
        this.trigger.setAttribute('aria-expanded', 'true');
    }
    
    close() {
        this.menu.classList.add('hidden');
        this.isOpen = false;
        this.trigger.setAttribute('aria-expanded', 'false');
    }
}

/**
 * Toast Notifications
 */
class Toast {
    static show(message, variant = 'default', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `alert-shadcn alert-shadcn-${variant} fixed bottom-4 right-4 z-50 max-w-sm animate-shadcn-slide-in shadow-lg`;
        
        const icon = this.getIcon(variant);
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                ${icon}
                <div class="flex-1">
                    <div class="alert-shadcn-description">${message}</div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="btn-shadcn btn-shadcn-ghost btn-shadcn-icon">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    static getIcon(variant) {
        const icons = {
            'default': '<i class="fas fa-info-circle text-primary"></i>',
            'destructive': '<i class="fas fa-exclamation-triangle text-destructive"></i>',
            'success': '<i class="fas fa-check-circle text-green-500"></i>',
            'warning': '<i class="fas fa-exclamation-circle text-yellow-500"></i>'
        };
        return icons[variant] || icons['default'];
    }
}

/**
 * Dialog/Modal Utilities
 */
class Dialog {
    constructor(dialogId) {
        this.dialog = document.getElementById(dialogId);
        this.isOpen = false;
        
        if (this.dialog) {
            this.init();
        }
    }
    
    init() {
        // Close on backdrop click
        this.dialog.addEventListener('click', (e) => {
            if (e.target === this.dialog) {
                this.close();
            }
        });
        
        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }
    
    open() {
        this.dialog.classList.remove('hidden');
        this.dialog.classList.add('flex');
        document.body.style.overflow = 'hidden';
        this.isOpen = true;
    }
    
    close() {
        this.dialog.classList.add('hidden');
        this.dialog.classList.remove('flex');
        document.body.style.overflow = '';
        this.isOpen = false;
    }
}

/**
 * Form Validation Helper
 */
class FormValidator {
    static validate(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;
        
        const inputs = form.querySelectorAll('.input-shadcn[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('border-destructive');
                isValid = false;
            } else {
                input.classList.remove('border-destructive');
            }
        });
        
        return isValid;
    }
    
    static clearErrors(formId) {
        const form = document.getElementById(formId);
        if (!form) return;
        
        const inputs = form.querySelectorAll('.input-shadcn');
        inputs.forEach(input => {
            input.classList.remove('border-destructive');
        });
    }
}

/**
 * Tabs Component
 */
class Tabs {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.triggers = this.container.querySelectorAll('[role="tab"]');
        this.panels = this.container.querySelectorAll('[role="tabpanel"]');
        
        this.init();
    }
    
    init() {
        this.triggers.forEach((trigger, index) => {
            trigger.addEventListener('click', () => {
                this.activateTab(index);
            });
        });
    }
    
    activateTab(index) {
        // Deactivate all
        this.triggers.forEach(t => {
            t.classList.remove('border-primary', 'text-foreground');
            t.classList.add('text-muted-foreground');
            t.setAttribute('aria-selected', 'false');
        });
        
        this.panels.forEach(p => {
            p.classList.add('hidden');
        });
        
        // Activate selected
        this.triggers[index].classList.add('border-primary', 'text-foreground');
        this.triggers[index].classList.remove('text-muted-foreground');
        this.triggers[index].setAttribute('aria-selected', 'true');
        this.panels[index].classList.remove('hidden');
    }
}

/**
 * Accordion Component
 */
class Accordion {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.items = this.container.querySelectorAll('[data-accordion-trigger]');
        this.init();
    }
    
    init() {
        this.items.forEach(trigger => {
            trigger.addEventListener('click', () => {
                const content = trigger.nextElementSibling;
                const isOpen = !content.classList.contains('hidden');
                
                if (isOpen) {
                    content.classList.add('hidden');
                    trigger.setAttribute('aria-expanded', 'false');
                } else {
                    content.classList.remove('hidden');
                    content.classList.add('animate-shadcn-slide-in');
                    trigger.setAttribute('aria-expanded', 'true');
                }
            });
        });
    }
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        Toast.show('Panoya kopyalandı', 'success', 2000);
    }).catch(() => {
        Toast.show('Kopyalama başarısız', 'destructive', 2000);
    });
}

/**
 * Initialize all components on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Auto-initialize dropdowns
    document.querySelectorAll('[data-dropdown-trigger]').forEach(trigger => {
        const menuId = trigger.getAttribute('data-dropdown-menu');
        new DropdownMenu(trigger.id, menuId);
    });
    
    // Auto-initialize tabs
    document.querySelectorAll('[data-tabs]').forEach(container => {
        new Tabs(container.id);
    });
    
    // Auto-initialize accordions
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container.id);
    });
});

// Export to global scope
window.DropdownMenu = DropdownMenu;
window.Toast = Toast;
window.Dialog = Dialog;
window.FormValidator = FormValidator;
window.Tabs = Tabs;
window.Accordion = Accordion;
window.copyToClipboard = copyToClipboard;
