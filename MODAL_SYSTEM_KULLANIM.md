# EventFlow Modal System - Kullanım Kılavuzu

## 🎯 Genel Bakış
EventFlow için özel tasarlanmış, temaya uygun modern modal/alert sistemi.

## 🚀 Temel Kullanım

### Success Mesajı
```javascript
showSuccess('İşlem başarıyla tamamlandı!');
```

### Error Mesajı
```javascript
showError('Bir hata oluştu!');
```

### Warning Mesajı
```javascript
showWarning('Dikkat! Bu işlem geri alınamaz.');
```

### Info Mesajı
```javascript
showInfo('Bilgilendirme mesajı');
```

### Confirmation Dialog
```javascript
const confirmed = await showConfirm('Emin misiniz?');
if (confirmed) {
    // Onaylandı
}
```

## 🎨 Özel Confirmation'lar

```javascript
// Silme onayı
await confirmDelete('Bu şablonu');

// QR kod onayı
await confirmQRGeneration('Rezervasyon #123');

// Tümünü temizle
await confirmClearAll();

// Etkinlik iptal
await confirmEventCancel();
```

## 🍞 Toast Notifications

```javascript
toastSuccess('Kayıt güncellendi!');
toastError('Bağlantı hatası!');
toastWarning('Oturum dolmak üzere!');
toastInfo('Yeni bildirim var.');
```

## 📝 Form Örneği

```javascript
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const confirmed = await confirmDelete('Bu kaydı');
    if (confirmed) {
        form.submit();
    }
});
```

## ✨ Özellikler
- ✅ Dark mode desteği
- ✅ Mobil uyumlu
- ✅ Klavye kısayolları (ESC)
- ✅ Temaya uygun renkler
- ✅ Otomatik kapanan toast'lar
