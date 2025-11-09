# shadcn/ui Tailwind Integration Guide

## 📦 Kurulum Tamamlandı

### Eklenen Bileşenler:

1. **Tailwind CSS** (CDN)
   - EventFlow brand renkleri ile özelleştirildi
   - Dark mode desteği
   - Responsive breakpoints

2. **shadcn/ui CSS** (`/static/css/shadcn.css`)
   - Button variants (default, destructive, outline, secondary, ghost, link)
   - Card component
   - Badge component
   - Input component
   - Dropdown menu
   - Alert/Toast
   - Table
   - Avatar
   - Separator

3. **JavaScript Utilities** (`/static/js/shadcn-utils.js`)
   - DropdownMenu class
   - Toast notifications
   - Dialog/Modal
   - Form validation
   - Tabs component
   - Accordion component
   - Copy to clipboard

---

## 🎨 Kullanım Örnekleri

### Button Component
```html
<!-- Default Button -->
<button class="btn-shadcn btn-shadcn-default">
    <i class="fas fa-plus mr-2"></i>
    Yeni Ekle
</button>

<!-- Outline Button -->
<button class="btn-shadcn btn-shadcn-outline">
    İptal
</button>

<!-- Destructive Button -->
<button class="btn-shadcn btn-shadcn-destructive">
    <i class="fas fa-trash mr-2"></i>
    Sil
</button>

<!-- Icon Button -->
<button class="btn-shadcn btn-shadcn-ghost btn-shadcn-icon">
    <i class="fas fa-edit"></i>
</button>
```

### Card Component
```html
<div class="card-shadcn">
    <div class="card-shadcn-header">
        <h3 class="card-shadcn-title">Etkinlik Detayları</h3>
        <p class="card-shadcn-description">Etkinlik bilgilerini görüntüleyin</p>
    </div>
    <div class="card-shadcn-content">
        <p>İçerik buraya...</p>
    </div>
    <div class="card-shadcn-footer">
        <button class="btn-shadcn btn-shadcn-default">Kaydet</button>
    </div>
</div>
```

### Badge Component
```html
<span class="badge-shadcn badge-shadcn-default">Aktif</span>
<span class="badge-shadcn badge-shadcn-secondary">Beklemede</span>
<span class="badge-shadcn badge-shadcn-destructive">İptal</span>
<span class="badge-shadcn badge-shadcn-outline">Taslak</span>
```

### Input Component
```html
<div class="space-y-2">
    <label class="label-shadcn">Etkinlik Adı</label>
    <input type="text" class="input-shadcn" placeholder="Etkinlik adını girin">
</div>
```

### Alert/Toast Component
```html
<!-- Alert -->
<div class="alert-shadcn alert-shadcn-default">
    <div class="alert-shadcn-title">Bilgi</div>
    <div class="alert-shadcn-description">İşlem başarılı!</div>
</div>

<!-- JavaScript Toast -->
<script>
    Toast.show('Kayıt başarılı!', 'success', 3000);
    Toast.show('Hata oluştu!', 'destructive', 3000);
</script>
```

### Dropdown Menu
```html
<div class="relative inline-block">
    <button id="dropdownTrigger" data-dropdown-trigger data-dropdown-menu="dropdownMenu" 
            class="btn-shadcn btn-shadcn-outline">
        Menü
        <i class="fas fa-chevron-down ml-2"></i>
    </button>
    
    <div id="dropdownMenu" class="dropdown-menu-shadcn hidden absolute right-0 mt-2">
        <div class="dropdown-menu-item-shadcn">
            <i class="fas fa-edit mr-2"></i>
            Düzenle
        </div>
        <div class="dropdown-menu-item-shadcn">
            <i class="fas fa-trash mr-2"></i>
            Sil
        </div>
    </div>
</div>
```

### Table Component
```html
<table class="table-shadcn">
    <thead class="table-shadcn-header">
        <tr class="table-shadcn-row">
            <th class="table-shadcn-head">Ad</th>
            <th class="table-shadcn-head">E-posta</th>
            <th class="table-shadcn-head">Durum</th>
        </tr>
    </thead>
    <tbody class="table-shadcn-body">
        <tr class="table-shadcn-row">
            <td class="table-shadcn-cell">John Doe</td>
            <td class="table-shadcn-cell">john@example.com</td>
            <td class="table-shadcn-cell">
                <span class="badge-shadcn badge-shadcn-default">Aktif</span>
            </td>
        </tr>
    </tbody>
</table>
```

### Dialog/Modal
```html
<div id="myDialog" class="hidden fixed inset-0 bg-black/50 items-center justify-center z-50">
    <div class="card-shadcn max-w-md w-full mx-4">
        <div class="card-shadcn-header">
            <h3 class="card-shadcn-title">Onay</h3>
            <p class="card-shadcn-description">Bu işlemi gerçekleştirmek istiyor musunuz?</p>
        </div>
        <div class="card-shadcn-footer gap-2">
            <button class="btn-shadcn btn-shadcn-outline" onclick="myDialogInstance.close()">
                İptal
            </button>
            <button class="btn-shadcn btn-shadcn-default">
                Onayla
            </button>
        </div>
    </div>
</div>

<script>
    const myDialogInstance = new Dialog('myDialog');
    myDialogInstance.open();
</script>
```

### Tabs Component
```html
<div id="myTabs" data-tabs>
    <div class="flex border-b">
        <button role="tab" class="px-4 py-2 border-b-2 border-primary text-foreground">
            Genel
        </button>
        <button role="tab" class="px-4 py-2 text-muted-foreground">
            Ayarlar
        </button>
    </div>
    
    <div role="tabpanel" class="p-4">
        Genel içerik
    </div>
    <div role="tabpanel" class="p-4 hidden">
        Ayarlar içerik
    </div>
</div>
```

---

## 🎨 Renk Paleti (EventFlow Brand)

```css
/* Primary - Orange */
--primary: hsl(16, 100%, 61%)          /* #ff6b35 */

/* Secondary - Dark Navy */
--secondary: hsl(210, 40%, 15%)        /* #1a2332 */

/* Accent - Gold */
--accent: hsl(27, 100%, 56%)           /* #f7931e */

/* Destructive - Red */
--destructive: hsl(0, 84.2%, 60.2%)    /* #ff5555 */
```

---

## 📱 Tailwind Utility Classes

```html
<!-- Layout -->
<div class="flex items-center justify-between gap-4">
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

<!-- Spacing -->
<div class="p-4 m-2 px-6 py-3">
<div class="space-y-4 space-x-2">

<!-- Typography -->
<h1 class="text-2xl font-bold text-foreground">
<p class="text-sm text-muted-foreground">

<!-- Colors -->
<div class="bg-primary text-primary-foreground">
<div class="bg-secondary text-secondary-foreground">

<!-- Borders -->
<div class="border border-border rounded-lg">
<div class="border-b border-muted">

<!-- Responsive -->
<div class="hidden md:block">
<div class="w-full md:w-1/2 lg:w-1/3">
```

---

## 🚀 Form Validation Örneği

```html
<form id="eventForm" class="space-y-4">
    <div class="space-y-2">
        <label class="label-shadcn">Etkinlik Adı</label>
        <input type="text" class="input-shadcn" required>
    </div>
    
    <button type="submit" class="btn-shadcn btn-shadcn-default">
        Kaydet
    </button>
</form>

<script>
    document.getElementById('eventForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        if (FormValidator.validate('eventForm')) {
            Toast.show('Form geçerli!', 'success');
        } else {
            Toast.show('Lütfen tüm alanları doldurun', 'destructive');
        }
    });
</script>
```

---

## 📝 Notlar

1. **Bootstrap Kaldırıldı**: Tailwind CSS ile değiştirildi
2. **Tüm componentler shadcn/ui standardında**
3. **Dark mode hazır** (class="dark" ile aktif)
4. **EventFlow brand renkleri entegre**
5. **JavaScript utilities otomatik initialize**

Bootstrap yerine artık Tailwind + shadcn/ui kullanabilirsiniz!
