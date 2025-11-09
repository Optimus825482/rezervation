# QR Code Scanner Implementation

## Overview

The QR Code Scanner feature enables event staff to quickly check-in guests by scanning reservation QR codes using their device's camera. The implementation uses the html5-qrcode library and provides both camera scanning and manual input options.

## Features

### 1. Dual Mode Interface
- **Camera Scanning:** Real-time QR code detection using device camera
- **Manual Input:** Fallback option for manual code entry
- **Tab Switching:** Easy toggle between camera and manual modes

### 2. Camera Features
- **Auto Camera Selection:** Automatically selects back camera on mobile devices
- **Permission Handling:** Graceful permission request and error handling
- **Real-time Scanning:** 10 FPS scanning with visual feedback
- **Auto-stop:** Scanner stops automatically after successful scan

### 3. Visual Feedback
- **Scanning Indicator:** Animated spinner during active scanning
- **Success Animation:** Pulse effect on successful check-in
- **Color-coded Alerts:** 
  - Green for success
  - Red for errors
  - Blue for info messages
- **Auto-dismiss:** Success messages auto-hide after 5 seconds

### 4. Error Handling
Comprehensive error messages for:
- **Permission Denied:** Instructions to enable camera access
- **Camera Not Found:** No camera available on device
- **Camera In Use:** Another app is using the camera
- **Incompatible Camera:** Camera doesn't support required features
- **Security Error:** HTTPS required for camera access
- **Invalid QR Code:** Code not found in database
- **Already Checked-in:** Duplicate check-in attempts

## Implementation Details

### Frontend Components

**Template:** `app/templates/checkin/index.html`

**Key Functions:**
- `startScanner()` - Initializes camera and starts QR detection
- `stopScanner()` - Stops camera and cleans up resources
- `onScanSuccess(decodedText)` - Handles successful QR code detection
- `handleCameraError(err)` - Provides user-friendly error messages
- `processCheckIn(code)` - Sends check-in request to backend
- `switchToScanner()` / `switchToManual()` - Tab switching

**Library:** html5-qrcode v2.3.8 (from unpkg CDN)

### Backend Integration

**Endpoint:** `POST /checkin/scan`

**Request:**
```json
{
  "code": "RESERVATION_CODE"
}
```

**Success Response:**
```json
{
  "success": true,
  "reservation": {
    "name": "John Doe",
    "phone": "05XX XXX XX XX",
    "seat_number": "A-15"
  }
}
```

**Error Response:**
```json
{
  "error": "Rezervasyon bulunamadı"
}
```

**Rate Limiting:** 30 requests per minute (per IP)

### Security Configuration

**CSP Updates:**
```python
# Development
CSP_SCRIPT_SRC = "'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://code.jquery.com https://unpkg.com"

# Production
CSP_SCRIPT_SRC = "'self' https://cdn.jsdelivr.net https://code.jquery.com https://unpkg.com"
```

**HTTPS Requirement:**
- Camera access requires HTTPS in production
- Use self-signed certificate or ngrok for local testing

## Usage Guide

### For Event Staff

**1. Access Check-in Page:**
- Navigate to `/checkin` in the application
- You'll see two tabs: "Kamera ile Tara" and "Manuel Giriş"

**2. Using Camera Scanner:**
1. Click "Kamera ile Tara" tab
2. Click "Taramayı Başlat" button
3. Allow camera access when prompted
4. Point camera at reservation QR code
5. Wait for automatic detection (usually < 1 second)
6. View check-in confirmation with guest details
7. Scanner stops automatically after successful scan

**3. Using Manual Input:**
1. Click "Manuel Giriş" tab
2. Type or paste reservation code
3. Click "Check-in Yap" button
4. View check-in confirmation

**4. Error Recovery:**
- If camera access fails, switch to manual input
- If QR code is damaged, use manual input
- Check error messages for specific instructions

### For Administrators

**Camera Permission Issues:**

If users report camera access problems:

1. **Browser Settings:**
   - Chrome: Settings → Privacy → Site Settings → Camera
   - Firefox: Preferences → Privacy → Permissions → Camera
   - Safari: Preferences → Websites → Camera

2. **HTTPS Check:**
   - Camera requires HTTPS in production
   - Verify SSL certificate is valid

3. **Device Compatibility:**
   - Most modern smartphones and tablets supported
   - Webcams on laptops/desktops supported
   - iOS 11+ and Android 5+ required

## Testing

### Manual Testing Steps

**1. Test Camera Scanning:**
```bash
# Run application
python run.py

# Navigate to http://localhost:5000/checkin
# Click "Kamera ile Tara"
# Click "Taramayı Başlat"
# Allow camera access
# Scan a QR code containing a valid reservation ID
# Verify success message appears
```

**2. Test Manual Input:**
```bash
# Click "Manuel Giriş" tab
# Enter a valid reservation code
# Click "Check-in Yap"
# Verify success message
```

**3. Test Error Scenarios:**
```bash
# Invalid code: Enter "INVALID123"
# Already checked-in: Scan same QR twice
# Permission denied: Block camera access
# Camera in use: Open camera in another app first
```

**4. Mobile Testing:**
- Test on iOS Safari
- Test on Android Chrome
- Test tablet landscape/portrait modes
- Verify back camera is used by default

### Browser Compatibility

| Browser | Desktop | Mobile | Notes |
|---------|---------|--------|-------|
| Chrome | ✅ | ✅ | Recommended |
| Edge | ✅ | ✅ | Chromium-based |
| Firefox | ✅ | ✅ | Works well |
| Safari | ✅ | ✅ | iOS 11+ required |
| Opera | ✅ | ✅ | Chromium-based |
| IE 11 | ❌ | N/A | Not supported |

### Performance

**Scanning Speed:**
- 10 FPS detection rate
- < 1 second typical scan time
- Instant feedback on success

**Resource Usage:**
- Minimal CPU usage (camera processing)
- Auto-cleanup on page close
- No memory leaks

## Configuration

### Scanner Settings

Located in `app/templates/checkin/index.html`:

```javascript
const config = {
    fps: 10,                           // Frames per second
    qrbox: { width: 250, height: 250 }, // Scan area size
    aspectRatio: 1.0                   // Square aspect ratio
};
```

**Adjustable Parameters:**
- `fps`: Higher = faster detection, more CPU usage (5-30 recommended)
- `qrbox`: Larger = easier to scan, smaller = more precise
- `aspectRatio`: Match device camera aspect ratio

### Camera Selection

```javascript
{ facingMode: "environment" }  // Use back camera on mobile
```

Options:
- `"environment"` - Back camera (default for mobile)
- `"user"` - Front camera
- Specific deviceId for multiple cameras

## Troubleshooting

### Camera Not Working

**Issue:** "Kamera bulunamadı" error

**Solutions:**
1. Check if device has a camera
2. Verify camera is not in use by another app
3. Try different browser
4. Restart browser/device

**Issue:** "Kamera izni reddedildi" error

**Solutions:**
1. Click address bar lock icon
2. Allow camera permission
3. Refresh page
4. Clear browser cache if needed

### QR Code Not Detected

**Issue:** Scanner doesn't detect QR code

**Solutions:**
1. Improve lighting conditions
2. Hold camera steady
3. Adjust distance (6-12 inches optimal)
4. Clean camera lens
5. Use manual input as fallback

### HTTPS Errors

**Issue:** "Güvenlik hatası. HTTPS üzerinden erişim gerekiyor"

**Solutions:**
1. Deploy with valid SSL certificate
2. For local testing:
   ```bash
   # Use ngrok
   ngrok http 5000
   
   # Or use Flask with SSL
   flask run --cert=adhoc
   ```

### Performance Issues

**Issue:** Slow scanning or high CPU usage

**Solutions:**
1. Reduce FPS in config (e.g., from 10 to 5)
2. Close other browser tabs
3. Use dedicated device for check-in
4. Update browser to latest version

## Development

### Adding Custom Styling

```css
/* Custom scanner styles */
#qr-reader__scan_region {
    border: 3px solid #your-color !important;
    border-radius: 10px !important;
}
```

### Custom Success Message

```javascript
function showSuccess(message) {
    // Add custom branding
    message = '<img src="/static/logo.png">' + message;
    // ... existing code
}
```

### Multiple QR Code Formats

```javascript
function onScanSuccess(decodedText, decodedResult) {
    // Parse different QR formats
    let code = decodedText;
    
    // Handle JSON QR codes
    try {
        const data = JSON.parse(decodedText);
        code = data.reservationId;
    } catch (e) {
        // Plain text QR code
    }
    
    processCheckIn(code);
}
```

## API Integration

### Custom Backend

If using a different backend, modify:

```javascript
fetch('/your-custom-endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'  // If needed
    },
    body: JSON.stringify({
        reservationCode: code,
        eventId: currentEventId  // Add context
    })
})
```

### Webhook Integration

```python
# Send check-in notification
@bp.route('/scan', methods=['POST'])
def scan():
    # ... existing check-in logic ...
    
    # Send webhook
    requests.post('https://your-webhook.com/checkin', json={
        'reservation_id': reservation.id,
        'timestamp': datetime.now().isoformat()
    })
```

## Best Practices

### For Users
1. **Good Lighting:** Ensure QR code is well-lit
2. **Steady Hands:** Hold device still while scanning
3. **Optimal Distance:** 6-12 inches from QR code
4. **Clean Lens:** Keep camera lens clean
5. **Test First:** Do test scan before event starts

### For Developers
1. **Error Handling:** Always provide fallback to manual input
2. **User Feedback:** Clear visual indicators for all states
3. **Performance:** Monitor FPS and adjust if needed
4. **Security:** Use HTTPS in production
5. **Testing:** Test on real mobile devices

### For Administrators
1. **Training:** Train staff on both camera and manual modes
2. **Backup Plan:** Have manual input ready if camera fails
3. **Device Check:** Verify devices work before event
4. **Network:** Ensure stable internet connection
5. **Support:** Have troubleshooting guide available

## Future Enhancements

### Potential Improvements
- [ ] Multi-QR batch scanning
- [ ] Offline mode with sync
- [ ] Sound feedback on successful scan
- [ ] Scan history/statistics
- [ ] Custom QR code generation
- [ ] Barcode support (EAN, UPC, etc.)
- [ ] Guest photo capture
- [ ] Multiple camera support
- [ ] PWA for offline use
- [ ] Analytics dashboard

### Known Limitations
- Requires HTTPS for camera access
- iOS requires user interaction to start camera
- Some older Android devices may have compatibility issues
- Camera quality affects scan reliability

## Support

### Common Questions

**Q: Why does camera require HTTPS?**
A: Browser security policy requires secure connection for camera/microphone access.

**Q: Can I use front camera?**
A: Yes, change `facingMode: "user"` in scanner config.

**Q: Does it work offline?**
A: Camera works offline, but check-in requires internet connection.

**Q: Can I scan multiple codes at once?**
A: Currently no, scanner stops after first successful scan.

**Q: What QR code format is supported?**
A: Any QR code containing a valid reservation code as plain text.

### Contact

For issues or questions:
- Check troubleshooting section above
- Review error messages carefully
- Test with manual input first
- Contact system administrator

---

**Implementation Date:** 2025-01-15
**Library Version:** html5-qrcode v2.3.8
**Status:** Production Ready ✅
