#!/bin/bash
# Railway'de migration sorununu düzelt

echo "🔧 Fixing Railway migration issue..."

# Migration'ı manuel olarak işaretle
flask db stamp head

echo "✅ Migration marked as complete!"
