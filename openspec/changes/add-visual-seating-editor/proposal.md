# Visual Seating Editor

## Why

Sistem analiz raporunda tespit edilen en kritik eksiklerden biri görsel koltuk düzenleme editörünün olmamasıdır. Bu özellik:
- Sistemin temel değer önerisi (value proposition)
- PROJE.md'de birinci öncelikli özellik olarak belirtilmiş
- Admin kullanıcılarının etkinlik koltuk düzenini kolayca oluşturmasını sağlar
- Kullanıcı deneyimi için kritik

Şu anda sadece backend veri modeli mevcut (event_seatings tablosu), ancak görsel editör UI'ı yok.

## What Changes

- **ADDED**: Drag-and-drop seating editor component
- **ADDED**: Grid-based layout system (snap-to-grid)
- **ADDED**: Zoom in/out functionality
- **ADDED**: Undo/redo functionality
- **ADDED**: Stage position configuration
- **ADDED**: Real-time seat numbering
- **ADDED**: Color coding for seat types
- **ADDED**: Template save/load functionality
- **ADDED**: Backend API endpoints for seating operations
- **MODIFIED**: Event creation flow - integrate editor step

## Impact

### Affected Specs
- `seating` (YENİ capability) - Visual seating editor
- `event-management` - Event creation flow

### Affected Code
- `app/routes/event.py` - Add seating editor endpoints
- `app/services/seating_service.py` (YENİ) - Seating business logic
- `app/templates/event/seating_editor.html` (YENİ) - Editor UI
- `app/static/js/seating-editor.js` (YENİ) - Editor JavaScript
- `app/static/css/seating-editor.css` (YENİ) - Editor styles

### Frontend Dependencies
- **Option 1 (Minimal)**: Sortable.js (lightweight drag-and-drop)
- **Option 2 (Feature-rich)**: interact.js (advanced drag, resize, gestures)
- **Recommended**: Start with Sortable.js, upgrade if needed

### Breaking Changes
None - This is a new feature

## Technology Decisions

### Drag-and-Drop Library Choice
**Decision**: Use Sortable.js
**Rationale**:
- Lightweight (19KB gzipped)
- No dependencies
- Touch-friendly (mobile support)
- Good documentation
- Sufficient for MVP

**Alternatives Considered**:
- interact.js: More features but larger (80KB)
- react-dnd: Requires React migration
- Custom implementation: Too much effort

### Data Storage Format
**Decision**: Store positions as JSON in seating_config column
**Format**:
```json
{
  "stage_position": "top",
  "grid_size": 50,
  "seats": [
    {
      "id": "seat-1",
      "type": "table-4",
      "number": "M1",
      "x": 100,
      "y": 200,
      "color": "#4CAF50"
    }
  ]
}
```

### Coordinate System
- Origin (0,0) at top-left
- Units: pixels
- Grid size: 50px default (configurable)
- Canvas size: 1200x800px default
