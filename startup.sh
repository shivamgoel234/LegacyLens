#!/bin/sh
set -e

# Load environment variables from .env if present (for local dev/CI)
if [ -f /app/.env ]; then
  echo "[startup.sh] Loading environment variables from /app/.env"
  export $(grep -v '^#' /app/.env | xargs)
fi

# --- Pre-start cleanup ---
echo "[startup.sh] Removing asyncio package from site-packages (if present)..."
find /home/site/wwwroot/.python_packages -name asyncio -type d -exec rm -rf {} \; 2>/dev/null || true
find /home/site/wwwroot/.python_packages -name "asyncio*.egg-info" -type d -exec rm -rf {} \; 2>/dev/null || true

# --- Database migrations ---
echo "[startup.sh] Applying database migrations..."
python manage.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE} || {
  echo "[startup.sh] WARNING: Migration failed or no migrations to apply.";
}

# --- Collect static files ---
if [ "$SKIP_COLLECTSTATIC" != "true" ]; then
  echo "[startup.sh] Collecting static files..."
  python manage.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE} || {
    echo "[startup.sh] WARNING: Collectstatic failed.";
  }
else
  echo "[startup.sh] Skipping collectstatic as SKIP_COLLECTSTATIC=true"
fi

# --- Start the main process ---
echo "[startup.sh] Starting main process: $@"
exec "$@"
