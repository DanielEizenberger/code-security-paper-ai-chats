#!/bin/bash
set -e

echo "⚽ FC Ironwall — Starting up..."

# Run seed (idempotent — won't duplicate on restart)
python seed.py || echo "Seed already applied or skipped."

echo "🚀 Launching Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    app:app
